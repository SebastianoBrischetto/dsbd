from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import requests

class SlaManager(Flask):
    def __init__(self, mongo_endpoint, metrics_endpoint, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.route('/sla', methods=['PUT'])(self.create_update_sla)
        self.route('/sla', methods=['GET'])(self.query_sla)
        self.route('/sla', methods=['DELETE'])(self.remove_sla)
        self.route('/violations', methods=['GET'])(self.query_violations)
        self.route('/probability', methods=['GET'])(self.query_probability)

        self.config['metrics_endpoint'] = metrics_endpoint

        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.sla

    def create_update_sla(self):
        data = request.json

        metric_name = data.get('metric_name')
        range_min = data.get('range_min')
        range_max = data.get('range_max')

        sla = self.collection.find_one({'metric_name': metric_name })

        if sla:
            try:
                self.collection.update_one({'metric_name': metric_name },{'$set': {'range_min': range_min, 'range_max': range_max}})
            except Exception as e:
                abort(500, description="Internal Server Error")
        else:
            try:
                self.collection.insert_one({'metric_name': metric_name, 'range_min': range_min, 'range_max': range_max})
            except Exception as e:
                abort(500, description="Internal Server Error")

        return jsonify({"message": "SLA created/updated successfully"}), 201


    def query_sla(self):
        metric_name = request.args.get('metric_name')
        sla = self.collection.find_one({'metric_name': metric_name })

        if not sla:
            abort(404, description="SLA not found")

        response = requests.get(self.config['metrics_endpoint'], {'query': metric_name})
        current_value = response.json().get('data', {}).get('result', [{}])[0].get('value', [])[1]
        violation = self._get_sla_status(current_value, sla.get('range_min'), sla.get('range_max'))
        return jsonify({"metric_name": sla.get('metric_name'), "current_value": current_value, "violation": violation})

        
    def remove_sla(self):
        metric_name = request.args.get('metric_name')
        sla = self.collection.find_one({'metric_name': metric_name })

        if not sla:
            abort(404, description="SLA not found")

        try:
            self.collection.delete_one({'_id': sla['_id']})
        except Exception as e:
            abort(500, description="Internal Server Error")

        return jsonify({"message": "SLA deleted successfully"}), 200


    def query_violations(self):
        metric_name = request.args.get('metric_name')
        interval = request.args.get('hours')

        response = requests.get(self.config['metrics_endpoint'], {'query': f'{metric_name}[{interval}h]'})
        raw_values = response.json()
        values = [x[1] for x in raw_values['data']['result'][0]['values']]

        sla = self.collection.find_one({'metric_name': metric_name })

        violations = [value for value in values if self._get_sla_status(value, sla.get('range_min'), sla.get('range_max'))]
        
        return jsonify({"violations_count": len(violations)})

    def query_probability(self):
        pass  # metric_name = request.args.get('metric_name')  # x_minutes = int(request.args.get('minutes', 5))  #  # #
        # Simulate calculating the probability (replace with actual logic)  # probability = random.uniform(0,
        # 1)  #  # return jsonify({"probability": probability})
    
    def _get_sla_status(self, current_value, range_min, range_max):
        return range_min > float(current_value) or range_max < float(current_value)