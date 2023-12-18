import requests
import string
import schedule
import time
from flask import Flask, request, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
#URL database mongodb://<ip>/<nome_database>
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)

#Mostra il contenuto della collection selezionata collection = mongo.db.<nome_collection>
@app.route('/')
def index():
    update()
    cursor = mongo.db.cities.find()
    return render_template('index.html', cursor=cursor)

def update():
    cities = mongo.db.users.distinct('cities')
    for city in cities:
        api_call(city)

def api_call(city: string):
    api_key = ""
    data = requests.get('https://api.openweathermap.org/data/2.5/forecast?q='+city+'&appid='+api_key)
    collection = mongo.db.cities
    entry = collection.find_one({"city": city})
    if not entry:
        collection.insert_one({"city": city, "data": data.json()})
    else:
        collection.update_one({"_id": entry.get("_id")}, { "$set": { 'data': data.json() } })
    return

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    