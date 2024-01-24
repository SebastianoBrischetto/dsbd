from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
from .kafka_producer import KafkaProducer

class UserUService(Flask):
    """
    UserUService class estende Flask per le operazioni CRUD sugli utenti in un database.
    """

    def __init__(self, mongo_endpoint, *args, **kwargs):
        """
        Costruttore per la classe UserUservice.

        Parameters:
            - mongo_endpoint (str): endpoint MongoDb per la connessione.
        """
        super().__init__(*args, **kwargs)

        # Routes
        self.route('/register', methods=['GET'])(self.register_handler)
        self.route('/user_conditions', methods=['GET'])(self.get_conditions_handler)
        self.route('/remove', methods=['GET'])(self.remove_conditions_handler)
        self.route('/city_conditions', methods=['GET'])(self.user_conditions_for_city)

        # Valori supportati per gli argomenti di /register
        self.condition_types = ["temperatura", "umidità", "pressione", "vento"]
        self.operators = ["<", ">"]

        # Configurazione mongo db
        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.users

        self.kafka_producer = KafkaProducer("PLAINTEXT://kafka:9092")

    def register_handler(self):
        """
        Gestisce la registrazione di un nuovo utente e il salvataggio delle condizioni.
        """
        user_id = request.args.get('id')
        data = request.args.getlist('data[]')
        if user_id is None or not data:
            return abort(400)
        
        params = {"city": data[0].lower(), "condition_type": data[1], "operator": data[2], "value": data[3]}
        if not self._check_form(**params):
            return abort(400)

        data = dict({"id": user_id}, **params)
        if params["city"] not in self._db_read_all_users_conditions():
            self.kafka_producer.produce_message('new-city-topic', 'city', params["city"])
        self._save_to_db(data)
        return jsonify(data)

    def _save_to_db(self, data):
        """
        Salva un nuovo user nel database.

        Parameters:
            - data (dict): Dati da salvare.
        """
        if self._db_read_user_conditions(data["id"]):
            self._db_update_user(data)
        else:
            self._db_create_user(data)

    def get_conditions_handler(self):
        """
        Gestisce le richieste per il recupero delle condizioni.
        """
        user_id = request.args.get('id')
        if user_id:
            data = self._db_read_user_conditions(user_id)
        else:
            data = self._db_read_all_users_conditions()
        return jsonify(data)

    def _check_form(self, city, condition_type, operator, value):
        """
        Effettua un controllo sui parametri ricevuti per la registrazione.

        Parameters:
            - city (str): Nome citta.
            - condition_type (str): Tipo di condizione.
            - operator (str): Operatore.
            - value (str): Valore.

        Returns:
            - bool: True se il form e valido, False altrimenti.
        """
        checks = [self._check_city(city), self._check_condition_type(condition_type), self._check_operator(operator), self._check_value(value)]
        return all(checks)

    def _check_city(self, city):
        """
        Controlla il nome della citta e valido.

        Parameters:
            - city (str): Nome citta.

        Returns:
            - bool: True se il nome e valido, False altrimenti.
        """
        return bool(city and city != "")

    def _check_condition_type(self, condition_type):
        """
        Controlla che il tipo di condizione e valido.

        Parameters:
            - condition_type (str): Tipo di condizione.

        Returns:
            - bool: True se il tipo e valido, False altrimenti.
        """
        return condition_type in self.condition_types

    def _check_operator(self, operator):
        """
        Controlla che un operatore sia valido.

        Parameters:
            - operator (str): Operatore.

        Returns:
            - bool: True se l'operatore e valido, False altrimenti.
        """
        return operator in self.operators

    def _check_value(self, value):
        """
        Controlla che il valore sia convertibile in float.

        Parameters:
            - value (str): Valore.

        Returns:
            - bool: True se la conversione e valida, False altrimenti.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def remove_conditions_handler(self):
        """
        Gestisce la richiesta di rimozione delle condizioni relative ad una citta.
        """
        user_id = request.args.get('id')
        city = request.args.get('city').lower()

        if user_id is None:
            return abort(400)
        
        params = {"id": user_id, "city": city}
        return jsonify(params) if self._db_remove_user_conditions_for_city(**params) else abort(400)

    def user_conditions_for_city(self):
        """
        Gestisce la richiesta per il recupero di tutte le condizioni relative ad una citta.
        """
        city = request.args.get('city')
        data = self._db_read_all_users_conditions_for_city(city)
        response = jsonify(data)
        return response

    # CRUD operations on the DB

    def _db_create_user(self, data):
        """
        Crea un nuovo utente nel database.

        Parameters:
            - data (dict): Dati utente da salvare.
        """
        user_id = data.pop("id", None)
        self.collection.insert_one({"id": user_id, "cities": [data]})

    def _db_read_user_conditions(self, user_id):
        """
        Recupera le condizioni di un utente.

        Parameters:
            - user_id (str): ID utente.

        Returns:
            - list: Lista delle condizioni associate all'utente.
        """
        data = self.collection.find_one({"id": user_id})
        return data.get("cities", []) if data else None

    def _db_read_all_users_conditions(self):
        """
        Recupera le condizioni di tutti gli utenti.

        Returns:
            - list: Lista delle condizioni di tutti gli utenti.
        """
        data = self.collection.distinct('cities.city')
        return data if data else None

    def _db_read_all_users_conditions_for_city(self, city):
        """
        Recupera tutte le condizioni associate ad una citta.

        Parameters:
            - city (str): Nome citta.

        Returns:
            - list: Lista delle condizioni associate ad una citta.
        """
        query = [
            {"$match": {"cities": {"$elemMatch": {"city": city}}}},
            {"$project": {
                "id": 1,
                "conditions": {
                    "$filter": {
                        "input": "$cities",
                        "as": "city",
                        "cond": {"$eq": ["$$city.city", city]}
                    }
                }
            }
            }
        ]
        response = self.collection.aggregate(query)
        data = [{"id": document['id'], 'conditions': document['conditions']} for document in response]
        return data

    def _db_update_user(self, data):
        """
        Aggiorna le condizioni di un utente nel db.

        Parameters:
            - data (dict): Dati utente da aggiornare.
        """
        user_id = data.pop("id", None)
        self.collection.update_one({"id": user_id}, {"$push": {'cities': {"$each": [data]}}})

    def _db_remove_user_conditions_for_city(self, user_id, city):
        """
        Rimuove le condizioni associate ad una citta per un utente.

        Parameters:
            - user_id (str): ID utente.
            - city (str): Nome citta.

        Returns:
            - bool: True se l'operazione e avvenuta con successo, False altrimenti.
        """
        result = self.collection.update_one({"id": user_id}, {"$pull": {"cities": {"city": city}}})
        return result.acknowledged if result else False