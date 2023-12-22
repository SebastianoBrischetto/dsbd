import requests
import time
from flask import Flask, abort

app = Flask(__name__)

app.config['API_KEY'] = "464c00ac0bbe3174a13b4ac72cdae20f"
app.config['cities_db_url'] = "http://127.0.0.1:5001/cities"  # PORTA MESSA A 5001 PER TESTARE
app.config['data_formatter_url'] = "http://127.0.0.1:5002/format_data"  # PORTA MESSA A 5002 PER TESTARE


def get_cities():  # Metodo per ottenere le città delle quali vogliamo conoscere i dati meteo
    cities = []
    response = requests.get(app.config['cities_db_url'])
    if response.status_code == 200:
        data = response.json()
        for new_city in data:
            cities.append(new_city)
        return cities
    else:
        return None


def get_data(city):  # Metodo per ottenere i dati meteo di una data città
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast',
                            {"q": city, "appid": app.config['API_KEY']})
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def push_data(data):  # Metodo per inviare i dati meteo dal microservizio data_formatter
    headers = {'Content-Type': 'application/json'}
    response = requests.post(app.config['data_formatter_url'], headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        return False


@app.route('/', methods=['GET'])
def update():
    while True:
        if get_cities() is not None:
            for city in get_cities():
                res = push_data(get_data(city))  # Implementare il controllo sul ritorno della POST
                if res is False:
                    return abort(400)
        time.sleep(30)  # Frequenza di aggiornamento dei dati meteo


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
