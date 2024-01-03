from src import WeatherData
import os

app = WeatherData("464c00ac0bbe3174a13b4ac72cdae20f", os.environ.get('API_GATEWAY') + "users_db/", os.environ.get('API_GATEWAY') + "data_formatter/", __name__)

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
