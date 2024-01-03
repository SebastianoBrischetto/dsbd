from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

class UsersDb(Flask):
    def __init__(self, mongo_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Config per connettersi a MongoDB
        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.users

        # Routes
        self.route('/cities', methods=['GET'])(self.cities)
        self.route('/save_user', methods=['POST'])(self.saveUser)
        self.route('/update_user', methods=['POST'])(self.updateUser)
        self.route('/remove_city', methods=['GET'])(self.removeCity)
        self.route('/list_user', methods=['GET'])(self.listUserCitiesConditions)

    def cities(self):
        id = request.args.get('id')
        if id:
            response = self.userCities(id)
        else:
            response = self.allUsersCities()
        return response

    def userCities(self, id):
        data = self.collection.find_one({"id" : id})
        if data:
            return jsonify(data["cities"])
        return abort(404)

    def allUsersCities(self):
        data = self.collection.distinct('cities.city')
        if data:
            return jsonify(data)
        return abort(404)
    
    def saveUser(self):
        data = request.get_json()
        id = data.pop("id",None)
        self.collection.insert_one({"id": id, "cities": [data]})
        return jsonify({"message": "richiesta effettuata con successo"})
    
    def updateUser(self):
        data = request.get_json()
        id = data.pop("id",None)
        self.collection.update_one({"id": id}, { "$push": { 'cities': {"$each": [data]} } })
        return jsonify({"message": "richiesta effettuata con successo"})
    
    #elimina città "city" dall'utente "id"
    def removeCity(self):
        city = request.args.get('city')
        id = request.args.get('id')

        result = self.collection.update_one({"id": id}, {"$pull": {"cities": {"city": city}}})

        if result.acknowledged:
            return jsonify({"message": "Eliminazione effettuata con successo"})
        else:
            return abort(400)
        
    def listUserCitiesConditions(self):
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
        response = self.collection.aggregate(query)
        data = []
        for document in response:
            data.append({"id": document['id'], 'conditions': document['conditions']})
        return jsonify(data)
