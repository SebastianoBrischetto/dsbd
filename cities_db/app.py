from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

app = Flask(__name__)

#database mongo
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)
collection = mongo.db.cities

#recupera i dati relativi ad una citta
#Parametri:
# @city - nome citta
@app.route('/cities' , methods=['GET'])
def cities():
    city = request.args.get('city')
    if city:
        response = city_weather(city)
    else:
        response = abort(400)
    return response

#recupera i dati relativi ad una citta
#Parametri:
# @city - nome citta
def city_weather(city):
    data = collection.find_one({"city.name" : city})
    if data:
        return jsonify(data["weather_data"])
    return abort(404)

@app.route('/save_weather_data' , methods=['POST'])
def save_weather_data():
    data = request.get_json()
    if not data:
        return abort(400)
    collection.insert_one(data)
    return jsonify({"message": "richiesta effettuata con successo"})

@app.route('/update_weather_data' , methods=['POST'])
def update_weather_data():
    data = request.get_json()
    if not data:
        return abort(400)
    collection.update_one({"city.name" : data["city"]["name"]}, { "$set": { 'weather_data': data["weather_data"] } })
    return jsonify({"message": "richiesta effettuata con successo"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')