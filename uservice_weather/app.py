from src import WeatherUService, KafkaConsumer
import os

#kafka_producer = KafkaProducer("PLAINTEXT://kafka:9092")
app = WeatherUService(
    os.environ.get('API_KEY'),
    os.environ.get('MONGO_DB'),
    os.environ.get('CITY_CONDITIONS'),
    __name__
)

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
