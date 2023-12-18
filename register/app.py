import requests
from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

app = Flask(__name__)

#endpoint lista citta, spostare tramite nginx
endpoint_user_cities = "http://127.0.0.1:3000/cities"

#roba database da esportare in un'altro microservizio in futuro
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)
collection = mongo.db.users

#Associa l'utente alle citta richieste
#Parametri:
# @id - identificatore utente
# @new_cities - lista di citta a cui l'utente vuole essere associato
@app.route('/register' , methods=['GET'])
def register():
    id = request.args.get('id')
    new_cities = request.args.getlist('cities[]')
    if id is None or not new_cities:
        return abort(400)
    response = requests.get(endpoint_user_cities,{"id" : id})
    if response.status_code == 200:
        old_cities = response.json()
        cities_to_save = old_cities + list(set(new_cities) - set(old_cities))
        update = True
    else:
        cities_to_save = new_cities
        update = False
    save_to_db(id, cities_to_save, update)
    #response_notification = requests.get('https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/sendMessage?chat_id='+chat_id+'&text=registrazione avvenuta con successo')
    #return jsonify(response_notification.json())
    return jsonify({"id":id, "cities": cities_to_save, "update": update})

#Salva i parametri nel database, spostare in un microservizio di scrittura sul db
#Parametri:
# @id - identificatore utente
# @cities_to_save - lista di citta da associare all'id
# @update - booleano per capire se inserire o aggiornare dal db
def save_to_db(id, cities_to_save:list, update:bool):
    if update:
        collection.update_one({"id": id}, { "$set": { 'cities': cities_to_save } })
    else:
        collection.insert_one({"id": id, "cities": cities_to_save})
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')