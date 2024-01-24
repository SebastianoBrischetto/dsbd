from src import WeatherBot
import os

if __name__ == '__main__':
    weather_bot = WeatherBot(
        "6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE", 
        os.environ.get('REGISTER_USER'), 
        os.environ.get('REMOVE_USER'))
    weather_bot.run()
