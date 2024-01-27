from src import WeatherBot
import os

if __name__ == '__main__':
    weather_bot = WeatherBot(
        os.environ.get('BOT_TOKEN'),
        os.environ.get('REGISTER_USER'), 
        os.environ.get('REMOVE_USER'))
    weather_bot.run()
