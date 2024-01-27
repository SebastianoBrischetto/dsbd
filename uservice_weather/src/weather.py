from flask import Flask, jsonify, abort
from flask_apscheduler import APScheduler
from flask_pymongo import PyMongo
from .kafka_consumer import KafkaConsumer
from .kafka_producer import KafkaProducer
from prometheus_client import start_http_server, Counter
import requests
import threading
import json

class WeatherUService(Flask):
    """
    Servizio meteo.

    Parameters:
    - api_key: API key per accedere ai dati di OpenWeather.
    - db_endpoint: URL per la connessione con il DB.
    - user_conditions_endpoint: Endpoint per recuperare le informazioni sulle citta da aggiornare.
    - city_conditions_endpoint: Endpoint per recuperare le condizioni relative ad una citta.
    - args, kwargs: Argomenti per Flask.
    """
    def __init__(self, api_key, db_endpoint, city_conditions_endpoint, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuration
        self.config['API_KEY'] = api_key
        self.config['api'] = "https://api.openweathermap.org/data/2.5/forecast"
        self.config['city_conditions_endpoint'] = city_conditions_endpoint

        # MongoDB configuration
        self.config['MONGO_URI'] = db_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.cities
        self.users_collection = self.mongo.db.users_copy

        # Mapping conditions
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

        # Kafka producer and consumer
        self.kafka_producer = KafkaProducer("PLAINTEXT://kafka:9092")
        self.kafka_consumer = KafkaConsumer('weather-consumer-group', 'new-city-topic', self.process_message, 'PLAINTEXT://kafka:9092')
        kafka_thread = threading.Thread(target=self.kafka_consumer.consume_messages)
        kafka_thread.start()

        # Scheduler
        self.scheduler = APScheduler()
        self.scheduler.add_job(id="scheduled_update", func=self._scheduled_update, trigger='interval', hours=3)
        self.scheduler.start()

        # Routes
        self.route('/force_update', methods=['GET'])(self.force_update_handler)

        # Prometheus
        self.num_of_notifications = Counter('num_of_notifications_sent', 'Total number of writes to Kafka notifications-topic')
        start_http_server(8000)

    def process_message(self, kafka_data):
        """
        Processa un messaggio.

        Parameters:
        - city: Nome citta ricevuto da Kafka.
        """
        user_condition = json.loads(kafka_data)
        city = user_condition.get('city')
        self._save_user_data(user_condition)
        self._update_city(city)


    def _scheduled_update(self):
        """
        Schedula l'update delle citta.
        """
        with self.app_context():
            self._update_saved_cities()

    def force_update_handler(self):
        """
        Handler per gestire la richiesta force update.
        """
        if self._update_saved_cities():
            return jsonify({"message": "Operazione avvenuta con successo"})
        else:
            return abort(404)

    def _update_saved_cities(self):
        """
        Aggiorna i dati meteo per le citta tracciate.
        """
        cities = self._db_read_cities_names()
        if cities is None:
            return False
        for city in cities:
            self._update_city(city)
        return True

    def _update_city(self, city):
        data = self._format_api_data(self._get_weather_data_from_api(city))
        if data:
            self._save_weather_data(data)
            self._send_notifications(city)
        return

    def _get_weather_data_from_api(self, city):
        """
        Recupera i dati meteo da OpenWeather per una citta.

        Parameters:
        - city: Nome della citta.

        Returns:
        - Dati meteo in formato json o None se la richiesta fallisce.
        """
        response = requests.get(self.config["api"], {"q": city, "appid": self.config['API_KEY']})
        if response.status_code == 200:
            data = response.json()
            data['city']['name'] = city
            return data
        else:
            return None

    def _format_api_data(self, data):
        """
        Formatta la risposta dell'api.

        Parameters:
        - data: Dati raw dell'api di openweather.

        Returns:
        - dati formattati.
        """
        if not data:
            return None
        return {"city": data.pop("city"), "weather_data": data.pop("list")[:8]}

    def _save_weather_data(self, data):
        """
        Salva i dati meteo sul database.

        Parameters:
        - data: Dati meteo formattati.
        """
        if self._db_read_city_weather_data(data["city"]["name"]):
            self._db_update_city(data)
        else:
            self._db_create_new_city(data)

    def _save_user_data(self, data):
        """
        Salva i dati utente sul database.

        Parameters:
        - data: Dati utente.
        """
        if self._db_read_city_user_data(data.get("user_id"), data.get("city")) is None:
            self._db_create_user(data)

    def _send_notifications(self, city):
        notifications = self._check_city_conditions(city)
        for notification in notifications:
            self.kafka_producer.produce_message('notifications-topic', 'notification', notification)
            self.num_of_notifications.inc()
        return

    def _check_city_conditions(self, city):
        """
        Controlla le condizioni meteo relativi ad una citta e crea una lista di utenti da aggiornare.

        Parameters:
        - city: Nome della citta.

        Returns:
        - Lista di notifiche.
        """
        user_conditions_list = []
        results = self.users_collection.find({'city': city})
        if results is None:
            return

        city_weather_data = self._db_read_city_weather_data(city)
        notifications = []
        for result in results:
            user_conditions_list.append(result)
        for condition in user_conditions_list:
            type = self.type_mapping[condition["condition_type"]]
            taxonomy = self.taxonomy_mapping[type]
            for city_weather_data_point in city_weather_data:
                if condition['operator'] == '>' and city_weather_data_point[taxonomy][type] > float(condition['value']):
                    notifications.append({'user': condition['user_id'], 'message': f"{condition['condition_type']} maggiore di {condition['value']} a {city} per giorno {city_weather_data_point['dt_txt']}"})
                elif condition['operator'] == '<' and city_weather_data_point[taxonomy][type] < float(condition['value']):
                    notifications.append({'user': condition['user_id'], 'message': f"{condition['condition_type']} minore di {condition['value']} a {city} per giorno {city_weather_data_point['dt_txt']}"})
        return notifications

    def _db_create_new_city(self, data):
        """
        Crea una nuova entry nel db.

        Parameters:
        - data: Dati meteo sulla citta.
        """
        if not data:
            return False
        self.collection.insert_one(data)
        return True

    def _db_create_user(self, data):
        """
        Crea un nuovo utente nel database.

        Parameters:
            - data (dict): Dati utente da salvare.
        """
        if not data:
            return False
        self.users_collection.insert_one(data)
        return True

    def _db_read_city_weather_data(self, city=None):
        """
        Recupera i dati meteo per la citta specificata.

        Parameters:
        - city: Nome della citta.

        Returns:
        - Dati meteo della citta.
        """
        if city is not None:
            data = self.collection.find_one({"city.name": city})
            return data.get("weather_data") if data else None
        return None

    def _db_read_city_user_data(self, user_id, city):
        """
        Recupera i dati meteo per la citta specificata.

        Parameters:
        - city: Nome della citta.

        Returns:
        - Dati utente per quella citta.
        """
        if city is not None:
            data = self.users_collection.find_one({"user_id": user_id, "city": city})
            return data.get("weather_data") if data else None
        return None
    
    def _db_update_city(self, data):
        """
        Aggiorna un'entry nel database con i dati meteo.

        Parameters:
        - data: Dati meteo sulla citta.
        """
        if not data:
            return False
        self.collection.update_one({"city.name": data["city"]["name"]}, {"$set": {'weather_data': data["weather_data"]}})
        return True
    
    def _db_read_cities_names(self):
        return self.collection.distinct('city.name')
