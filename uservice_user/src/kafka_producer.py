from confluent_kafka import Producer
import time
import logging
import json
class KafkaProducer:
    def __init__(self, bootstrap_servers="PLAINTEXT://kafka:9092"):
        """
        Inizializza un'instanza del producer kafka.

        Parameters:
        - bootstrap_servers: Server bootstrap di kafka.
        """
        self.setup_logger()
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = None

        while not self.is_kafka_ready():
            self.logger.info("Waiting for Kafka to be ready...")
            time.sleep(5)

        self.logger.info("Producer ready to publish messages.")

    def setup_logger(self):
        """
        Configura il logger per la classe Kafka producer.
        """
        self.logger = logging.getLogger('Kafka producer')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def is_kafka_ready(self):
        """
        Controlla che kafka sia pronto.

        Returns:
        - True se kafka e pronto, False altrimenti.
        """
        try:
            self.producer = Producer({'bootstrap.servers': self.producer_config['bootstrap.servers']})
            self.producer.list_topics(timeout=5)
            return True
        except Exception as e:
            self.logger.info(f"Kafka not ready: {str(e)}")
            return False

    def delivery_report(self, err, msg):
        """
        Callback sullo stato del messaggio.

        Parameters:
        - err: eventuale errore.
        - msg: messaggio prodotto.
        """
        if err is not None:
            self.logger.info('Message delivery failed: {}'.format(err))
        else:
            self.logger.info('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def produce_message(self, topic, key, value):
        """
        Produce un messaggio sul topic.

        Parameters:
        - topic: Topic Kafka sulla quale verra scritto il messaggio.
        - key: Chiave della coppia key-value.
        - value: Valore della coppia key-value.
        """
        self.producer.produce(topic, key=key, value=json.dumps(value), callback=self.delivery_report)
        self.producer.flush()
