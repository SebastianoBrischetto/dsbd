from confluent_kafka import Producer
import time, logging

class KafkaProducer:
    def __init__(self, bootstrap_servers = "PLAINTEXT://kafka:9092"):
        self.setupLogger()
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = None

        # Aspetta che kafka sia pronto
        while not self.isKafkaReady():
            self.logger.info("Waiting for Kafka to be ready...")
            time.sleep(5)

        self.logger.info("Kafka is ready and so is the producer.")

    def setupLogger(self):
        self.logger = logging.getLogger('Kafka producer')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def isKafkaReady(self):
        try:
            self.producer = Producer({'bootstrap.servers': 'PLAINTEXT://kafka:9092'})
            self.producer.list_topics(timeout=5)
            return True
        except Exception as e:
            self.logger.info(f"Kafka not ready: {str(e)}")
            return False

    def deliveryReport(self, err, msg):
        if err is not None:
            self.logger.info('Message delivery failed: {}'.format(err))
        else:
            self.logger.info('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def produceMessage(self, topic, key, value):
        self.producer.produce(topic, key=key, value=value, callback=self.deliveryReport)
        self.producer.flush()