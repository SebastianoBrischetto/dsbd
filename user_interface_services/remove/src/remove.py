from flask import Flask, request, jsonify, abort
import requests

class Remove(Flask):
    def __init__(self, users_db_endpoint, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Endpoint
        self.config["users_db"] = users_db_endpoint
        # Routes
        self.route('/remove', methods=['GET'])(self.remove)

    def remove(self):
        id = request.args.get('id') #ID telegram dell'utente
        city = request.args.get('city').lower() #città scritta dall'utente
        if id is None:
            return abort(400)
        params = {"id":id, "city": city}
        response = requests.get(self.config["users_db"] + "remove_city", params)
        if response.status_code != 200:
            return abort(400)
        else:
            return jsonify(params)


    
