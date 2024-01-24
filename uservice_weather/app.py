from src import WeatherUService, KafkaConsumer
import os

#kafka_producer = KafkaProducer("PLAINTEXT://kafka:9092")
app = WeatherUService(
    "464c00ac0bbe3174a13b4ac72cdae20f", 
    "mongodb://root:password@mongo_db:27017/weather_report_db?authSource=admin&authMechanism=SCRAM-SHA-256",
    os.environ.get('USER_CONDITIONS'),
    os.environ.get('CITY_CONDITIONS'),
    __name__
)

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
