from flask import Flask, jsonify, abort
from flask_apscheduler import APScheduler
from flask_pymongo import PyMongo
import requests

class WeatherData(Flask):
    def __init__(self, api_key, mongo_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Config
        self.config['API_KEY'] = api_key
        self.config['api'] = "https://api.openweathermap.org/data/2.5/forecast"

        # Config per connettersi a MongoDB
        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.cities

        # Scheduler
        self.scheduler = APScheduler()
        self.scheduler.add_job(id="scheduled_update", func=self.scheduled_update, trigger='interval', hours=3)
        self.scheduler.start()

        # Routes
        self.route('/force_update')(self.update_saved_cities)

    # Metodo per ottenere le città delle quali vogliamo conoscere i dati meteo (va sostituito con una lettura sul db)
    def getCities(self):
        response = requests.get(self.config['users_db'] + "cities")
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def update_saved_cities(self):
        cities = self.getCities()
        if cities is None:
            return abort(404)
        
        for city in cities:
            data = self.formatApiResponse(self.getData(city))
            self.save_city(data)
            self.kafka_producer.produceMessage('weather-topic', 'city_name', data["city"]["name"])
        return True
    
    # Metodo per ottenere i dati meteo di una data città dall'api di open weather
    def getData(self, city):
        response = requests.get(self.config["api"], {"q": city, "appid": self.config['API_KEY']})
        if response.status_code == 200:
            data = response.json()
            data['city']['name'] = city
            return data
        else:
            return None

    # Formattazione dati
    def formatApiResponse(self, data):
        if not data:
            return None
        return {"weather_data": data.pop("list")[:8], "city": data.pop("city")}

    def save_city(self, data):
        if self._DB_ReadCityWeatherData(data['city']['name']):
            self._DB_UpdateCity(data)
        else:
            self._DB_CreateNewCity(data)

    def scheduled_update(self):
        with self.app_context():
            self.update_saved_cities()

    # Operazioni CRUD sul db
    # Create
    def _DB_CreateNewCity(self, data):
        if not data:
            return False
        self.collection.insert_one(data)
        return True
    
    # Read
    def _DB_ReadCityWeatherData(self, city = None):
        if city is not None:
            data = self.collection.find_one({"city.name": city})
            return data.get("weather_data") if data else None
        return None

    # Update
    def _DB_UpdateCity(self, data):
        if not data:
            return False
        self.collection.update_one({"city.name": data["city"]["name"]}, {"$set": {'weather_data': data["weather_data"]}})
        return True
