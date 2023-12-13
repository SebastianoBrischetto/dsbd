import requests
from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
#URL database mongodb://<ip>/<nome_database>
app.config['MONGO_URI'] = 'mongodb://localhost:27017/weather_report_bot'
mongo = PyMongo(app)

#Mostra il contenuto della collection selezionata collection = mongo.db.<nome_collection>
@app.route('/')
def index():
    collection = mongo.db.users
    cursor = collection.find()
    return render_template('index.html', cursor=cursor)

#Route per la registrazione al servizio, usata dal bot
@app.route('/register' , methods=['GET'])
def register():
    #parametri get
    chat_id = request.args.get('chat_id')
    cities = request.args.getlist('cities[]')
    #database
    collection = mongo.db.users
    #controllo esistenza chat
    entry = collection.find_one({"chat_id" : chat_id})
    if not entry:
        data = {"chat_id": chat_id, "cities": cities}
        result = collection.insert_one(data)
    else:
        saved_cities = entry.get("cities")
        data = saved_cities + list(set(cities) - set(saved_cities))
        result = collection.update_one({"_id": entry.get("_id")}, { "$set": { 'cities': data } })
    requests.get('https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/sendMessage?chat_id='+chat_id+'&text=registrazione avvenuta con successo')
    return jsonify({"message": "Registrazione avvenuta con successo"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')