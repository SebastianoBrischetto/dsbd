import requests
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

#endpoints
endpoint_users_db = "http://users_db:5000/"

@app.route('/remove', methods=['GET']) #argomenti: id = id e data = città
def remove():
    id = request.args.get('id') #ID dell'utente
    city = request.args.get('city') #città scritta dall'utente
    print(id)
    print(city)
    if id is None:
        return abort(400)
    else:
        print("Microservizio remove raggiunto!")
    params = {"city": city, "id": id}
    print(params)
    response = requests.get(endpoint_users_db + "remove_city", params)
    if response.status_code != 200:
        return abort(400)
    else:
        return jsonify(params)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
