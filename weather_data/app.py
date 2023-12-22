import requests
import string
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
api_key = ""

#endpoint lista citta, spostare tramite nginx
endpoint_cities = "http://cities:5000/cities"

#roba database da esportare in un'altro microservizio in futuro
app.config['MONGO_URI'] = 'mongodb://mongo_db:27017/weather_report_db'
mongo = PyMongo(app)
collection = mongo.db.cities

#effettua una chiamata al servizio meteo per ognuna delle citta di cui tenere traccia
def update():
    response = requests.get(endpoint_cities)
    if response.status_code == 200:
        cities = response.json()
    else:
        return
    for city in cities:
        api_call(city)

#chiamata al servizio openweathermap per il recupero dei dati meteo di una citta
#Parametri:
# @city - nome della citta di cui si vuole sapere i dati meteo
def api_call(city: string):
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast', {"q": city, "appid": api_key})
    save_to_db(city, response.json())

#Salva i parametri nel database, spostare in un microservizio di scrittura sul db
#Parametri:
# @city - nome della citta da salvare/aggiornare
# @data - dati meteo associati alla citta
def save_to_db(city: string, data):
    is_present = collection.find_one({"city": city})
    if is_present:
        collection.update_one({"city": city}, { "$set": { 'data': data } })
    else:
        collection.insert_one({"city": city, "data": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    