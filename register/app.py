import requests
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

#endpoint lista citta, spostare tramite nginx
endpoint_user_db = "http://127.0.0.1:3000/"

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
    response = requests.get(endpoint_user_db+"cities",{"id" : id})
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

#esegue la chiamata per poter salvare/aggiornare
#Parametri:
# @id - identificatore utente
# @cities_to_save - lista di citta da associare all'id
# @update - booleano per capire se inserire o aggiornare dal db
def save_to_db(id, cities_to_save:list, update:bool):
    params = {"id" : id, "cities[]": cities_to_save}
    if update:
        response = requests.get(endpoint_user_db+"update_user", params)
    else:
        response = requests.get(endpoint_user_db+"save_user", params)
    return response
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')