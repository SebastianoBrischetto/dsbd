import requests
from flask import Flask, request, jsonify, abort

class Register(Flask):
    def __init__(self, users_db_endpoint, register_form_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Endpoint
        self.config["users_db"] = users_db_endpoint
        self.config["register_form"] = register_form_endpoint
        # Routes
        self.route('/register', methods=['GET'])(self.register)

    def register(self):
        id = request.args.get('id')
        data = request.args.getlist('data[]')
        if id is None or not data:
            return abort(400)
        params = {"city": data[0].lower(), "type": data[1], "condition": data[2], "value": data[3]}
        response = requests.get(self.config["register_form"]+"check_form", params)
        if response.status_code != 200:
            return abort(400)
        self.saveToDb(id, params)
        #response_notification = requests.get('https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/sendMessage?chat_id='+chat_id+'&text=registrazione avvenuta con successo')
        #return jsonify(response_notification.json())
        return jsonify({"id":id, "cities": params})
    
    def saveToDb(self, id, params):
        response = requests.get(self.config["users_db"]+"cities",{"id" : id})
        headers = {'Content-Type': 'application/json'}
        json = dict({"id" : id}, **params)
        if response.status_code == 200:
            requests.post(self.config["users_db"]+"update_user", headers=headers, json=json)
        else:
            requests.post(self.config["users_db"]+"save_user", headers=headers, json=json)
