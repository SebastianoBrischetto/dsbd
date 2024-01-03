from confluent_kafka import Producer
import time

class KafkaProducer:
    def __init__(self, bootstrap_servers = "PLAINTEXT://kafka:9092"):
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = None

        # Aspetta che kafka sia pronto
        while not self.is_kafka_ready():
            print("Waiting for Kafka to be ready...")
            time.sleep(5)

        print("Kafka is ready and so is the producer.")

    def is_kafka_ready(self):
        try:
            self.producer = Producer({'bootstrap.servers': 'PLAINTEXT://kafka:9092'})
            self.producer.list_topics(timeout=5)
            return True
        except Exception as e:
            print(f"Kafka not ready: {str(e)}")
            return False

    def delivery_report(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def produce_message(self, topic, key, value):
        self.producer.produce(topic, key=key, value=value, callback=self.delivery_report)
        self.producer.flush()