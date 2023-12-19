from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

app = Flask(__name__)

#database mongo
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)
collection = mongo.db.cities

#recupera la lista delle citta associate ad un utente se viene passato un id, in caso di assenza ritorna la lista delle citta che vanno tracciate
#Parametri:
# @id -identificatore utente
@app.route('/cities' , methods=['GET'])
def cities():
    city = request.args.get('city')
    if city:
        response = city_weather(city)
    else:
        response = abort(400)
    return response

#ritorna le citta a cui un id e associato
#Parametri:
# @id -identificatore utente
def city_weather(city):
    data = collection.find_one({"city" : city})
    if data:
        return jsonify(data["data"])
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')