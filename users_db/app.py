from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import json

app = Flask(__name__)


#database mongo
app.config['MONGO_URI'] = 'mongodb://root:password@mongo_db:27017/weather_report_db?authSource=admin&authMechanism=SCRAM-SHA-256'
mongo = PyMongo(app)
collection = mongo.db.users


#recupera la lista dei parametri associati ad un utente se viene passato un id, in caso di assenza ritorna la lista delle citta che vanno tracciate
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


#ritorna i parametri associati ad un id
#Parametri:
# @id -identificatore utente
def user_cities(id):
    data = collection.find_one({"id" : id})
    if data:
        return jsonify(data["cities"])
    return abort(404)


#ritorna la lista delle citta che vanno tracciate
def all_cities():
    data = collection.distinct('cities.city')
    if data:
        return jsonify(data)
    return abort(404)


#salvataggio utente
#Parametri:
# @id - identificatore utente
# @cities - lista di parametri sulle citta da associare all'id
@app.route('/save_user' , methods=['POST'])
def save_user():
    data = request.get_json()
    id = data.pop("id",None)
    collection.insert_one({"id": id, "cities": [data]})
    return jsonify({"message": "richiesta effettuata con successo"})


#aggiornamento utente
#Parametri:
# @id - identificatore utente
# @cities - lista di parametri sulle citta da associare all'id
@app.route('/update_user' , methods=['POST'])
def update_user():
    data = request.get_json()
    id = data.pop("id",None)
    collection.update_one({"id": id}, { "$push": { 'cities': {"$each": [data]} } })
    return jsonify({"message": "richiesta effettuata con successo"})


@app.route('/list_user' , methods=['GET'])
def list_user():
    city = request.args.get('city')
    query = [
        {"$match": {"cities": {"$elemMatch": {"city": city}}}}, #trova i documenti che contengono almeno una volta le condizioni relative alla citta richiesta
        {"$project": { #recupera solo l'id e le condizioni che appartengono alla citta richiesta (ignora le altre citta)
                "id": 1,
                "conditions": {
                    "$filter": {
                        "input": "$cities",
                        "as": "city",
                        "cond": {"$eq": ["$$city.city", city]}
                    }
                }
            }
        }
    ]
    response = collection.aggregate(query)
    data = []
    for document in response:
        data.append({"id": document['id'], 'conditions': document['conditions']})
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')