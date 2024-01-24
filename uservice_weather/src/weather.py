from flask import Flask, jsonify, abort
from flask_apscheduler import APScheduler
from flask_pymongo import PyMongo
import requests, threading

class WeatherUService(Flask):
    def __init__(self, api_key, mongo_endpoint, user_conditions_endpoint, city_conditions_endpoint,kafka_producer, kafka_consumer, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Config
        self.config['API_KEY'] = api_key
        self.config['api'] = "https://api.openweathermap.org/data/2.5/forecast"
        self.config['user_conditions_endpoint'] = user_conditions_endpoint
        self.config['city_conditions_endpoint'] = city_conditions_endpoint

        # Config per connettersi a MongoDB
        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.cities

        # Mapping condizioni
        self.type_mapping = {
            "temperatura": "feels_like",
            "umidità": "humidity", 
            "pressione": "pressure", 
            "vento": "speed"
        }
        self.taxonomy_mapping = {
            "feels_like": "main",
            "humidity": "main",
            "pressure": "main",
            "speed": "wind",
        }

        # Kafka producer
        #self.kafka_producer = kafka_producer
        #self.kafka_producer.produceMessage('users-to-notify-topic', 'city_name', data["city"]["name"])

        # Kafka Consumer
        #self.kafka_consumer = kafka_consumer
        #kafka_thread = threading.Thread(target = self.kafka_consumer.consumeMessages)
        #kafka_thread.start()

        # Scheduler
        self.scheduler = APScheduler()
        self.scheduler.add_job(id="scheduled_update", func=self._scheduled_update, trigger='interval', hours=3)
        self.scheduler.start()

        # Routes
        self.route('/force_update', methods=['get'])(self.force_update_handler)

    def _scheduled_update(self):
        with self.app_context():
            self._update_saved_cities()

    def force_update_handler(self):
        if self._update_saved_cities():
            return jsonify({"message": "operazione avvenuta con successo"})
        else:
            return abort(404)
    
    def _update_saved_cities(self):
        cities = self._get_cities_to_update()
        if cities is None:
            return False
        for city in cities:
            data = self._format_api_data(self._get_weather_data_from_api(city))
            self._save_weather_data(data)
        return True

    # Metodo per ottenere le città delle quali vogliamo conoscere i dati meteo (va sostituito con una lettura sul db)
    def _get_cities_to_update(self):
        response = requests.get(self.config['user_conditions_endpoint'])
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _get_weather_data_from_api(self, city):
        response = requests.get(self.config["api"], {"q": city, "appid": self.config['API_KEY']})
        if response.status_code == 200:
            data = response.json()
            data['city']['name'] = city
            return data
        else:
            return None
        
    def _format_api_data(self, data):
        if not data:
            return None
        return {"weather_data": data.pop("list")[:8], "city": data.pop("city")}

    def _save_weather_data(self, data):
        if self._db_read_city_weather_data(data['city']['name']):
            self._db_update_city(data)
        else:
            self._db_create_new_city(data)

    # Controllo condizioni per una citta, se soddisfate inserisce l'id dell'utente e un messaggio nella lista di notifiche
    def _check_city_conditions(self, city):
        user_conditions_list = requests.get(self.config['city_conditions_endpoint'], {"city": city}).json()[0]
        city_weather_data = self._db_read_city_weather_data(city)
        notifies = []
        for condition in user_conditions_list['conditions']:
            type = self.type_mapping[condition["type"]]
            taxonomy = self.taxonomy_mapping[type]
            for city_weather_data_point in city_weather_data:
                if condition['condition'] == '>' and city_weather_data_point[taxonomy][type] > float(condition['value']):
                    notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" maggiore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
                elif condition['condition'] == '<' and city_weather_data_point[taxonomy][type] < float(condition['value']):
                    notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" minore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
        return notifies

    # Operazioni CRUD sul db
    # Create
    def _db_create_new_city(self, data):
        if not data:
            return False
        self.collection.insert_one(data)
        return True
    
    # Read
    def _db_read_city_weather_data(self, city = None):
        if city is not None:
            data = self.collection.find_one({"city.name": city})
            return data.get("weather_data") if data else None
        return None

    # Update
    def _db_update_city(self, data):
        if not data:
            return False
        self.collection.update_one({"city.name": data["city"]["name"]}, {"$set": {'weather_data': data["weather_data"]}})
        return True
