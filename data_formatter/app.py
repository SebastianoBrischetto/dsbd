import requests
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

#endpoint lista citta, spostare tramite nginx
endpoint_cities_db = "http://127.0.0.1:5000/"

#formatta i dati ricevuti prima di inserirli nel db
@app.route('/format_data', methods=['POST'])
def format_data():
    data = request.get_json()
    if not data:
        return abort(400)
    formatted_data = {"weather_data": data.pop("list")[:8], "city": data.pop("city")}
    save_to_db(formatted_data)
    return jsonify({"message": "richiesta effettuata con successo"})

def save_to_db(data, update):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(endpoint_cities_db+"cities",{"city" : data["city"]["name"]})
    if response.status_code == 200:
        requests.post(endpoint_cities_db + "update_weather_data", headers=headers, json=data)
    else:
        requests.post(endpoint_cities_db + "save_weather_data", headers=headers, json=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    