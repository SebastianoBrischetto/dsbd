from confluent_kafka import Consumer, KafkaError
import time

class KafkaConsumer:
    def __init__(self, group_id, topics, bootstrap_servers = "PLAINTEXT://kafka:9092"):
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.topics = topics
        self.consumer = None

        # Aspetta che kafka sia pronto
        while not self.is_kafka_ready():
            print("Waiting for Kafka to be ready...")
            time.sleep(5)

        print("Kafka is ready and so is the consumer.")

    # Controlla se kafka e pronto (True) o meno (False)
    def is_kafka_ready(self):
        try:
            self.consumer = Consumer(self.consumer_config)
            self.consumer.subscribe(self.topics)
            return True
        except KafkaError as e:
            print(f"Kafka not ready: {e}")
            return False

    # Consume message
    def consume_messages(self):
        try:
            while True:
                message = self.consumer.poll(1.0)
                if message is not None:
                    if message.error():
                        print(f'Error: {message.error()}')
                    else:
                        print(f'Message: {message.value().decode("utf-8")}')
        finally:
            if self.consumer:
                self.consumer.close()