from src import SlaManager
import os

app = SlaManager(os.environ.get('MONGO_DB'), os.environ.get('METRICS'), __name__)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')