from src import DataFormatter, KafkaProducer
import os

kafka_producer = KafkaProducer("PLAINTEXT://kafka:9092")
app = DataFormatter(os.environ.get('API_GATEWAY') + "cities_db/", kafka_producer, __name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')