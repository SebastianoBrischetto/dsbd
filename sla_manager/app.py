from src import SlaManager
import os

app = SlaManager(os.environ.get('MONGO_DB'), os.environ.get('METRICS'), __name__)
#app = SlaManager("mongodb://root:password@localhost:27017/weather_report_db?authSource=admin&authMechanism=SCRAM-SHA-256", "http://localhost:5000/metrics", __name__)
if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0')