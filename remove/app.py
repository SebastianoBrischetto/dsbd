import requests
from flask import Flask, request, abort

app = Flask(__name__)

#endpoints
endpoint_users_db = "http://users_db:5000/"
endpoint_register_form = "http://register_form:5000/"

@app.route('/remove', methods=['GET']) #argomenti: id = id e data = città
def remove():
    id = request.args.get('id') #ID dell'utente
    city = request.args.get('city') #città scritta dall'utente
    if id is None:
        return abort(400)
    else:
        print("Microservizio remove raggiunto!")
    params = {"city": city, "id": id}
    response = requests.get(endpoint_users_db + "remove", params)
    if response.status_code != 200:
        return abort(400)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')