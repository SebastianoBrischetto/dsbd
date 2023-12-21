from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import json

app = Flask(__name__)

#database mongo
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

#salvataggio utente
#Parametri:
# @id - identificatore utente
# @cities - lista di citta da associare all'id
@app.route('/save_user' , methods=['GET'])
def save_user():
    id = request.args.get('id')
    cities = request.args.getlist('cities[]')
    collection.insert_one({"id": id, "cities": cities})
    return jsonify({"message": "richiesta effettuata con successo"})

#aggiornamento utente
#Parametri:
# @id - identificatore utente
# @cities - lista di citta da associare all'id
@app.route('/update_user' , methods=['GET'])
def update_user():
    id = request.args.get('id')
    cities = request.args.getlist('cities[]')
    collection.update_one({"id": id}, { "$set": { 'cities': cities } })
    return jsonify({"message": "richiesta effettuata con successo"})

@app.route('/list_user' , methods=['GET'])
def list_user():
    cities = request.args.get('cities')
    data = collection.find({"cities": cities})
    for document in data:
        id = document.get("id")
        if id is not None:
                result_json = json.dumps({ "id": id })
                print(result_json)        
    return jsonify({"message": "richiesta effettuata con successo"})
    
   



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')