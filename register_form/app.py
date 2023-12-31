from flask import Flask, request, jsonify, abort

app = Flask(__name__)
types = ["temperatura", "umidità", "pressione", "vento"]
conditions = ["<",">"]

#controlla i parametri prima di accettare la registrazione
#Parametri:
# @city - nome citta
# @type - tipo condizione da controllare
# @condition - condizione 
# @value - valore 

@app.route('/check_form' , methods=['GET'])
def check_form():
    city = request.args.get('city')
    type = request.args.get('type')
    condition = request.args.get('condition')
    value = request.args.get('value')
    checks = [check_city(city), check_type(type), check_condition(condition), check_value(value)]
    if all(checks):
        return jsonify({"message": "richiesta effettuata con successo"})
    return abort(400)

def check_city(city):
    if city and city!="":
        return True
    return False

def check_type(type):
    if type in types:
        return True
    return False

def check_condition(condition):
    if condition in conditions:
        return True
    return False

def check_value(value):
    try:
        value = float(value)
    except:
        return False
    return True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')