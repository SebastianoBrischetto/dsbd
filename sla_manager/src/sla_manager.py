from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import requests
from datetime import datetime, timedelta
from .time_series import reevaluate_model, compute_out_of_bounds_probability
import dill

class SlaManager(Flask):
    def __init__(self, mongo_endpoint, metrics_endpoint, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.route('/save_SLA', methods=['PUT'])(self.create_update_sla)
        self.route('/is_violated', methods=['GET'])(self.query_sla)
        self.route('/delete_SLA', methods=['DELETE'])(self.remove_sla)
        self.route('/violations', methods=['GET'])(self.query_violations)
        self.route('/reevaluate_model', methods=['POST'])(self.reevaluate_model_endpoint)
        self.route('/get_probability', methods=['GET'])(self.query_probability)

        self.config['metrics_endpoint'] = metrics_endpoint

        self.config['MONGO_URI'] = mongo_endpoint
        self.mongo = PyMongo(self)
        self.collection = self.mongo.db.sla
        self.collection_time_series = self.mongo.db.time_series

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

    def reevaluate_model_endpoint(self):
        data = request.json
        metric_name = data.get('metric_name')
        interval = data.get('range_in_minute')

        if not metric_name or not interval:
            abort(400)

        response = requests.get(self.config['metrics_endpoint'], {'query': f'{metric_name}[{interval}m]'})
        raw_values = response.json()
        values = [x for x in raw_values['data']['result'][0]['values']]

        if values is None:
            abort(404, description=f"No time series data found for metric '{metric_name}'")

        try:
            trend_function, error_std = reevaluate_model(values)
            trend_function_binary = dill.dumps(trend_function)
            model_instance = self.collection_time_series.find_one({'metric_name': metric_name })
            if model_instance:
                self.collection_time_series.update_one({'metric_name': metric_name },{'$set': {'error_std': error_std, 'serialized_trend': trend_function_binary}})
            else:
                self.collection_time_series.insert_one({'metric_name': metric_name, 'error_std': error_std, 'serialized_trend': trend_function_binary})
        except Exception as e:
            abort(500, description=f"Error storing the new model for metric '{metric_name}': {str(e)}")

        return jsonify({"message": f"Model re-evaluation completed for metric '{metric_name}'"}), 200

    def query_probability(self):
        metric_name = request.args.get('metric_name')
        x_minutes = int(request.args.get('minutes', 5))

        sla = self.collection.find_one({'metric_name': metric_name })
        if not sla:
            return jsonify({"error": f"No SLA Document found with metric name '{metric_name}'"}), 404

        y_lower_bound = sla.get('range_max')

        # Define time boundaries
        current_datetime = datetime.now()
        x_lower_limit = int(current_datetime.timestamp())
        future_datetime = current_datetime + timedelta(minutes=x_minutes)
        x_upper_limit = int(future_datetime.timestamp())

        # Fetch SeriesModel instance and necessary parameters
        model_instance = self.collection_time_series.find_one({'metric_name': metric_name })
        if not model_instance:
            return jsonify({"error": f"No SeriesModel found with metric name '{metric_name}'"}), 404

        try:
            trend_function = dill.loads(model_instance.get('serialized_trend'))
            error_std = model_instance.get('error_std')
            probability, _, _, _ = compute_out_of_bounds_probability(trend_function, error_std, x_lower_limit,x_upper_limit, y_lower_bound)
            return jsonify({"probability": probability})
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred"}), 500
    
    def _get_sla_status(self, current_value, range_min, range_max):
        return range_min > float(current_value) or range_max < float(current_value)