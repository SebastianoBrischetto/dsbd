from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo

app = Flask(__name__)
#URL database mongodb://<ip>/<nome_database>
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)
collection = mongo.db.users

#ritorna le citta a cui un utente e registrato
@app.route('/user_cities' , methods=['GET'])
def user_cities():
    chat_id = request.args.get('chat_id')
    data = collection.find_one({"chat_id" : chat_id})
    if data and data["cities"]:
        return jsonify(data["cities"])
    return abort(404)

#ritorna tutte le citta a cui sono registrati gli utenti
@app.route('/subscribed_cities')
def all_cities():
    data = collection.distinct('cities')
    if data:
        return jsonify(data)
    else:
        return abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')