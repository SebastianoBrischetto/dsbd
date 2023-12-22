import time

from flask import Flask, abort
import requests

app = Flask(__name__)

app.config['API_KEY'] = "464c00ac0bbe3174a13b4ac72cdae20f"
app.config['cities_URL'] = "http://127.0.0.1:3000/cities"
app.config['end_point_url'] = "http://127.0.0.1:5001/update"


def get_city():
    cities = ['Catania', 'Palermo']
    return cities


def get_data(city):
    api_url = 'https://api.openweathermap.org/data/2.5/forecast?q=' + city + '&appid=' + app.config['API_KEY']
    response = requests.get(api_url)  # Response GET request
    #print("Response: ",response.json())
    data = response.json()
    if data:
        return data
    else:
        return None


def push_data(data):
    headers = {'Content-Type': 'application/json'}
    if data == None:
        print("Dati inesistenti")
    else:
        print("Pronto ad inviare i dati")
        print("URL POST: ",app.config['end_point_url'])
        print("Header: ",headers)
        try:
            response = requests.post(app.config['end_point_url'], headers=headers, json=data)

            if response.status_code == 200:
                print("Richiesta POST completata con successo!")
                print("Risposta dal server:", response.json())
                time.sleep(2)
                return True
            else:
                print("Impossibile inviare i dati")
                return False
        except requests.exceptions.RequestException as e:
            print("Errore durante la connessione:", e)


def update():
    for city in get_city():
        res = push_data(get_data(city))
        if res:
            print("Dati riguardo alla città di " + city + " inviati.")
        else:
            print("Dati riguardo alla città di " + city + " non inviati.")
        time.sleep(3)  # PROVVISORIO, GIUSTO PER MONITORARE MEGLIO L'INVIO DELLE RICHIESTE POST
    time.sleep(10)

@app.route('/', methods=['GET'])
def function():
    while True:
        update()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
