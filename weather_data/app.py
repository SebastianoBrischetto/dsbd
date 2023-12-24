import requests
from flask import Flask, abort, jsonify
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

app.config['API_KEY'] = "464c00ac0bbe3174a13b4ac72cdae20f"
app.config['users_db_url'] = "http://users_db:5000/"
app.config['data_formatter_url'] = "http://data_formatter:5000/"


def get_cities():  # Metodo per ottenere le città delle quali vogliamo conoscere i dati meteo
    response = requests.get(app.config['users_db_url'] + "cities")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_data(city):  # Metodo per ottenere i dati meteo di una data città
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast',
                            {"q": city, "appid": app.config['API_KEY']})
    if response.status_code == 200:
        return response.json()
    else:
        return None


def push_data(data):  # Metodo per inviare i dati meteo al microservizio data_formatter
    headers = {'Content-Type': 'application/json'}
    response = requests.post(app.config['data_formatter_url'] + "format_data", headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        return False


def update():
    cities = get_cities()
    errors = False
    if cities is not None:
        for city in cities:
            res = push_data(get_data(city))
            if res is False:
                errors = True
    else:
        return abort(404)
    return jsonify({"message": "operazione avvenuta con successo", "errors": errors})


@app.route('/force_update')
def force_update():
    return update()


def scheduled_update():
    with app.app_context():
        update()

scheduler.add_job(id="scheduled_update", func=scheduled_update, trigger='interval', hours=3)
scheduler.start()

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
