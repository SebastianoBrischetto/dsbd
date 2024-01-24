import requests
from flask import Flask, request, jsonify, abort

class DataFormatter(Flask):
    def __init__(self, cities_db_endpoint, kafka_producer, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Endpoint
        self.config["cities_db"] = cities_db_endpoint

        # Kafka producer
        self.kafka_producer = kafka_producer
        
        # Routes
        self.route('/format_data', methods=['POST'])(self.formatData)

    # POST: Esegue la formattazione dei dati ricevuti e li salva nel db
    def formatData(self):
        data = request.get_json()
        if not data:
            return abort(400)
        formatted_data = {"weather_data": data.pop("list")[:8], "city": data.pop("city")}
        self.saveToDb(formatted_data)
        self.kafka_producer.produceMessage('weather-topic', 'city_name', formatted_data["city"]["name"])
        return jsonify({"message": "richiesta effettuata con successo"})

    # Esegue la richiesta al servizio cities_db
    def saveToDb(self, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(self.config["cities_db"]+"cities",{"city" : data["city"]["name"]})
        if response.status_code == 200:
            requests.post(self.config["cities_db"] + "update_weather_data", headers=headers, json=data)
        else:
            requests.post(self.config["cities_db"] + "save_weather_data", headers=headers, json=data)
