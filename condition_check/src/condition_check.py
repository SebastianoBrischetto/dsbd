import requests
from flask import Flask, request, jsonify, abort

class ConditionCheck(Flask):
    def __init__(self, telegram_bot_endpoint, users_db_endpoint, cities_db_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Endpoint
        self.config['telegram_bot'] = telegram_bot_endpoint
        self.config['users_db'] = users_db_endpoint
        self.config['cities_db'] =  cities_db_endpoint

        # Routes
        self.route('/notify', methods=['GET'])(self.notifyUsers)

        # Mapping condizioni API open weather
        self.type_mapping = {
            "temperatura": "feels_like",
            "umidità": "humidity", 
            "pressione": "pressure", 
            "vento": "speed"
        }

        # Mapping tassonomie open weather
        self.taxonomy_mapping = {
            "feels_like": "main",
            "humidity": "main",
            "pressure": "main",
            "speed": "wind",
        }

    # GET: Notifica gli utenti sottoiscritti a una città (se e presente il parametro GET 'city')
    def notifyUsers(self):
        city = request.args.get('city')
        if city:
            response = self.checkCity(city.lower())
        else:
            response = abort(400)
        return response

    # Effettua il controllo delle condizioni definite dagli utenti rispetto a una citta e se soddisfatte notifica gli utenti
    def checkCity(self, city):
        user_conditions_list = requests.get(self.config['users_db']+"list_user", {"city": city}).json()[0]
        city_weather_data = requests.get(self.config['cities_db']+"cities", {"city": city}).json()
        notifies = []
        for condition in user_conditions_list['conditions']:
            type = self.type_mapping[condition["type"]]
            taxonomy = self.taxonomy_mapping[type]
            for city_weather_data_point in city_weather_data:
                if condition['condition'] == '>' and city_weather_data_point[taxonomy][type] > float(condition['value']):
                    notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" maggiore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
                elif condition['condition'] == '<' and city_weather_data_point[taxonomy][type] < float(condition['value']):
                    notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" minore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
        for notific in notifies:
            requests.get(self.config['telegram_bot'] + "sendMessage", {"chat_id":notific['user'], "text":notific['message']})
        return jsonify(notifies)
