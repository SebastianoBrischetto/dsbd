from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

class CitiesDb(Flask):
    def __init__(self, mongo_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Config per connettersi a MongoDB
        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.cities

        # Routes
        self.route('/cities', methods=['GET'])(self.cities_route)
        self.route('/save_weather_data', methods=['POST'])(self.save_weather_data_route)
        self.route('/update_weather_data', methods=['POST'])(self.update_weather_data_route)

    # GET: Ritorna i dati meteorologici di una città (se e presente il parametro GET 'city')
    def cities_route(self):
        city = request.args.get('city')
        if city:
            response = self.city_weather(city)
        else:
            response = abort(400)
        return response

    # Recupera e ritorna i dati meteorologici in formato json di una città da MongoDB
    def city_weather(self, city):
        data = self.collection.find_one({"city.name": city})
        if data:
            return jsonify(data["weather_data"])
        return abort(404)

    # POST: Salva i data meteorologici di una citta
    def save_weather_data_route(self):
        data = request.get_json()
        if not data:
            return abort(400)
        self.collection.insert_one(data)
        return jsonify({"message": "richiesta effettuata con successo"})

    # POST: Aggiorna i dati meteorologici di una città
    def update_weather_data_route(self):
        data = request.get_json()
        if not data:
            return abort(400)
        self.collection.update_one({"city.name": data["city"]["name"]}, {"$set": {'weather_data': data["weather_data"]}})
        return jsonify({"message": "richiesta effettuata con successo"})
