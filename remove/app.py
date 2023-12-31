import requests
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

#endpoints
endpoint_users_db = "http://users_db:5000/"

@app.route('/remove', methods=['GET'])
def remove():
    id = request.args.get('id') #ID telegram dell'utente
    city = request.args.get('city') #città scritta dall'utente
    if id is None:
        return abort(400)
    params = {"id":id, "city": city}
    response = requests.get(endpoint_users_db + "remove_city", params)
    if response.status_code != 200:
        return abort(400)
    else:
        return jsonify(params)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
