import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['telegram_bot'] = "https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/"

type_mapping = {
    "temperatura": "feels_like",
    "umidità": "humidity", 
    "pressione": "pressure", 
    "vento": "speed"
}
taxonomy_mapping = {
    "feels_like": "main",
    "humidity": "main",
    "pressure": "main",
    "speed": "wind",
}

#database mongo
app.config['users_db_url'] = "http://users_db:5000/"
app.config['cities_db_url'] = "http://cities_db:5000/"

#notifica gli utenti registrati alla citta quando si verificano le condizioni
#Parametri:
# @city - nome citta
@app.route('/notify' , methods=['GET'])
def check_city():
    city = request.args.get("city").lower()
    user_conditions_list = requests.get(app.config['users_db_url']+"list_user", {"city": city}).json()[0]
    city_weather_data = requests.get(app.config['cities_db_url']+"cities", {"city": city}).json()
    notifies = []
    for condition in user_conditions_list['conditions']:
        type = type_mapping[condition["type"]]
        taxonomy = taxonomy_mapping[type]
        for city_weather_data_point in city_weather_data:
            if condition['condition'] == '>' and city_weather_data_point[taxonomy][type] > float(condition['value']):
                notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" maggiore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
            elif condition['condition'] == '<' and city_weather_data_point[taxonomy][type] < float(condition['value']):
                notifies.append({'user': user_conditions_list['id'], 'message': condition["type"]+" minore di "+condition['value']+" a "+ city +" per giorno "+city_weather_data_point["dt_txt"]})
    notify(notifies)
    return jsonify({"notifiche": notifies})

def notify(notifies):
    for notify in notifies:
        requests.get(app.config['telegram_bot'] + "sendMessage", {"chat_id":notify['user'], "text":notify['message']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')