from flask import Flask
from .kafka_consumer import KafkaConsumer
import threading
import json
import requests
from prometheus_client import start_http_server, Counter

class Notifier(Flask):
    def __init__(self, bot_token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token

        self.kafka_consumer = KafkaConsumer('notifications-consumers-group', 'notifications-topic', self.process_message, 'PLAINTEXT://kafka:9092')
        kafka_thread = threading.Thread(target=self.kafka_consumer.consume_messages)
        kafka_thread.start()

        self.num_of_notifications = Counter('num_of_notifications_received', 'Total number of reads from Kafka notifications-topic')
        start_http_server(8000)

    def process_message(self, kafka_data):        
        notifications_dict = json.loads(kafka_data)        
        client_id = notifications_dict.get('user')
        message_text = notifications_dict.get('message')
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {'chat_id': client_id, 'text': message_text}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            print("Message sent successfully")
            self.num_of_notifications.inc()
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")