from src import ConditionCheck, KafkaConsumer
import os

kafka_consumer = KafkaConsumer('weather-consumer-group', 'weather-topic', 'PLAINTEXT://kafka:9092')
app = ConditionCheck(
    "https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/", 
    os.environ.get('API_GATEWAY') + "users_db/", 
    os.environ.get('API_GATEWAY') + "cities_db/",
    kafka_consumer,
    __name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')