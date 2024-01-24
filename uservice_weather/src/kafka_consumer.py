from confluent_kafka import Consumer, KafkaError
import time
import logging

class KafkaConsumer:
    def __init__(self, group_id, topics, on_message_callback, bootstrap_servers):
        """
        Inizializza un'instanza del consumer kafka.

        Parameters:
        - group_id: Group ID consumer kafka.
        - topics: Lista dei topic alla quale sottoscriversi.
        - on_message_callback: Callback alla funzione da eseguire alla ricezione di un messaggio.
        - bootstrap_servers: Server bootstrap di kafka.
        """
        self.setupLogger()
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        self.topics = [topics]
        self.consumer = None
        self.on_message_callback = on_message_callback

        while not self.isKafkaReady():
            self.logger.info("Waiting for Kafka to be ready...")
            time.sleep(5)

        self.logger.info("Consumer ready to process messages.")

    def setupLogger(self):
        """
        Configura il logger per la classe Kafka consumer.
        """
        self.logger = logging.getLogger('Kafka consumer')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def isKafkaReady(self):
        """
        Controlla che kafka sia pronto.

        Returns:
        - True se kafka e pronto, False altrimenti.
        """
        try:
            self.consumer = Consumer(self.consumer_config)
            self.consumer.subscribe(self.topics)
            return True
        except KafkaError as e:
            self.logger.info(f"Kafka not ready: {e}")
            return False

    def consumeMessages(self):
        """
        Consuma messaggi dal topic, esegue il callback e dopo aver processato commita.
        """
        try:
            while True:
                message = self.consumer.poll(1.0)
                if message is not None:
                    if message.error():
                        self.logger.error(f'Error: {message.error()}')
                    else:
                        decoded_message = message.value().decode("utf-8")
                        self.logger.info(f'Starting to process message: {decoded_message}')
                        
                        # Execute the callback function with the decoded message
                        self.on_message_callback(decoded_message)
                        
                        self.logger.info('Message processed, committing offset.')
                        
                        # Manually commit offsets
                        self.consumer.commit()
        except KeyboardInterrupt:
            pass
        finally:
            if self.consumer:
                self.consumer.close()