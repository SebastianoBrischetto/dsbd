from flask import Flask
from .kafka_consumer import KafkaConsumer
import threading
import json
import requests

class Notifier(Flask):
    def __init__(self, bot_token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token
        self.last_notification = None 

        self.kafka_consumer = KafkaConsumer('notifications-consumers-group', 'notifications-topic', self.process_message, 'PLAINTEXT://kafka:9092')
        kafka_thread = threading.Thread(target=self.kafka_consumer.consume_messages)
        kafka_thread.start()

    def process_message(self, kafka_data):
        self.last_notification = kafka_data  
        if self.last_notification:                  
            notifications_dict = json.loads(self.last_notification)        
            client_id = notifications_dict.get('user')
            message_text = notifications_dict.get('message')
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {'chat_id': client_id, 'text': message_text}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                print("Message sent successfully")
            else:
                print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        else:
            print("No notification to send")