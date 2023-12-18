from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

app = Flask(__name__)

#roba database da esportare in un'altro microservizio in futuro
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)
collection = mongo.db.users

#recupera la lista delle citta associate ad un utente se viene passato un id, in caso di assenza ritorna la lista delle citta che vanno tracciate
#Parametri:
# @id -identificatore utente
@app.route('/cities' , methods=['GET'])
def cities():
    id = request.args.get('id')
    if id:
        response = user_cities(id)
    else:
        response = all_cities()
    return response

#ritorna le citta a cui un id e associato
#Parametri:
# @id -identificatore utente
def user_cities(id):
    data = collection.find_one({"id" : id})
    if data and data["cities"]:
        return jsonify(data["cities"])
    return abort(404)

#ritorna la lista delle citta che vanno tracciate
def all_cities():
    data = collection.distinct('cities')
    if data:
        return jsonify(data)
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')