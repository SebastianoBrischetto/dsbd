from flask import Flask, request, jsonify, abort

class RegisterForm(Flask):
    def __init__(self, *args, **kwargs):
        # Costruttore flask
        super().__init__(*args, **kwargs)

        # Tipi supportati
        self.types = ["temperatura", "umidità", "pressione", "vento"]
        # Condizioni supportate
        self.conditions = ["<",">"]
        # Routes
        self.route('/check_form', methods=['GET'])(self.checkForm)

    def checkForm(self):
        city = request.args.get('city')
        type = request.args.get('type')
        condition = request.args.get('condition')
        value = request.args.get('value')
        checks = [self.checkCity(city), self.checkType(type), self.checkCondition(condition), self.checkValue(value)]
        if all(checks):
            return jsonify({"message": "richiesta effettuata con successo"})
        return abort(400)

    def checkCity(self, city):
        if city and city!="":
            return True
        return False

    def checkType(self, type):
        if type in self.types:
            return True
        return False

    def checkCondition(self, condition):
        if condition in self.conditions:
            return True
        return False

    def checkValue(self, value):
        try:
            value = float(value)
        except:
            return False
        return True