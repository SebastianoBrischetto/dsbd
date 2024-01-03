from src import WeatherBot
import os

if __name__ == '__main__':
    weather_bot = WeatherBot("6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE", os.environ.get('API_GATEWAY')+"register/", os.environ.get('API_GATEWAY')+"remove/")
    weather_bot.run()
