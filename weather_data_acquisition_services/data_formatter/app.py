from src import DataFormatter
import os

app = DataFormatter(os.environ.get('API_GATEWAY') + "cities_db/", __name__)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')