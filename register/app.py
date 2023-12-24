import requests
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

#endpoints
endpoint_users_db = "http://users_db:5000/"
endpoint_register_form = "http://register_form:5000/"

#Associa l'utente alle citta richieste
#Parametri:
# @id - identificatore utente
# @data - parametri da tracciare (nome, tipo, condizione, valore)
@app.route('/register' , methods=['GET'])
def register():
    id = request.args.get('id')
    data = request.args.getlist('data[]')
    if id is None or not data:
        return abort(400)
    params = {"city": data[0].lower(), "type": data[1], "condition": data[2], "value": data[3]}
    response = requests.get(endpoint_register_form+"check_form", params)
    if response.status_code != 200:
        return abort(400)
    save_to_db(id, params)
    #response_notification = requests.get('https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/sendMessage?chat_id='+chat_id+'&text=registrazione avvenuta con successo')
    #return jsonify(response_notification.json())
    return jsonify({"id":id, "cities": params})

#esegue la chiamata per poter salvare/aggiornare
#Parametri:
# @id - identificatore utente
# @params - lista di parametri da associare all'id per il tracciamento
def save_to_db(id, params):
    response = requests.get(endpoint_users_db+"cities",{"id" : id})
    headers = {'Content-Type': 'application/json'}
    json = dict({"id" : id}, **params)
    if response.status_code == 200:
        requests.post(endpoint_users_db+"update_user", headers=headers, json=json)
    else:
        requests.post(endpoint_users_db+"save_user", headers=headers, json=json)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')