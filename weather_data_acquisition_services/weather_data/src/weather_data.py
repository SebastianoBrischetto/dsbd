from flask import Flask, jsonify, abort
from flask_apscheduler import APScheduler
import requests

class WeatherData(Flask):
    def __init__(self, api_key, users_db_endpoint, data_formatter_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Config
        self.config['API_KEY'] = api_key
        self.config['users_db'] = users_db_endpoint
        self.config['data_formatter'] = data_formatter_endpoint
        self.config['api'] = "https://api.openweathermap.org/data/2.5/forecast"

        # Scheduler
        self.scheduler = APScheduler()
        self.scheduler.add_job(id="scheduled_update", func=self.scheduled_update, trigger='interval', hours=3)
        self.scheduler.start()

        # Routes
        self.route('/force_update')(self.update)

    def getCities(self):  # Metodo per ottenere le città delle quali vogliamo conoscere i dati meteo
        response = requests.get(self.config['users_db'] + "cities")
        if response.status_code == 200:
            return response.json()
        else:
            return None
            

    def getData(self, city):  # Metodo per ottenere i dati meteo di una data città
        response = requests.get(self.config["api"], {"q": city, "appid": self.config['API_KEY']})
        if response.status_code == 200:
            data = response.json()
            data['city']['name'] = city
            return data
        else:
            return None

    def pushData(self, data):  # Metodo per inviare i dati meteo al microservizio data_formatter
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.config['data_formatter'] + "format_data", headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            return False
        
    def update(self):
        cities = self.getCities()
        if cities is None:
            return abort(404)
        
        errors = False
        for city in cities:
            res = self.pushData(self.getData(city))
            if not res:
                errors = True
        return jsonify({"message": "operazione avvenuta con successo", "errors": errors})
    
    def scheduled_update(self):
        with self.app_context():
            self.update()