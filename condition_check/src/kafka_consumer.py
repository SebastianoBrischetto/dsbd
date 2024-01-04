from confluent_kafka import Consumer, KafkaError
import time, logging

class KafkaConsumer:
    def __init__(self, group_id, topics, bootstrap_servers="PLAINTEXT://kafka:9092"):
        self.setupLogger()
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # Disable automatic offset commits
        }
        self.topics = [topics]
        self.consumer = None

        # Wait for Kafka to be ready
        while not self.isKafkaReady():
            self.logger.info("Waiting for Kafka to be ready...")
            time.sleep(5)

        self.logger.info("Kafka is ready, and so is the consumer.")

    def setupLogger(self):
        self.logger = logging.getLogger('Kafka consumer')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    # Check if Kafka is ready (True) or not (False)
    def isKafkaReady(self):
        try:
            self.consumer = Consumer(self.consumer_config)
            self.consumer.subscribe(self.topics)
            return True
        except KafkaError as e:
            self.logger.info(f"Kafka not ready: {e}")
            return False

    # Consume message, print it immediately, and manually commit offsets
    def consumeMessages(self):
        try:
            while True:
                message = self.consumer.poll(1.0)
                if message is not None:
                    if message.error():
                        self.logger.error(f'Error: {message.error()}')
                    else:
                        self.logger.info(f'Message: {message.value().decode("utf-8")}')
                        self.consumer.commit()
        except KeyboardInterrupt:
            pass
        finally:
            if self.consumer:
                self.consumer.close()