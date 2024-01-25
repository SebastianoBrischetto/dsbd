from telegram.ext import ApplicationBuilder
from flask import Flask, jsonify, abort
from .kafka_consumer import KafkaConsumer
import threading
import json

class NotificationService(Flask):
    def __init__(self, bot_token):
        super(NotificationService, self).__init__('notification_service')
        self.bot_token = bot_token
        self.bot = ApplicationBuilder().token(self.bot_token).build()

        self.kafka_consumer = KafkaConsumer('weather-consumer-group', 'users-to-notify', self.process_message, 'PLAINTEXT://kafka:9092')
        kafka_thread = threading.Thread(target=self.kafka_consumer.consume_messages)
        kafka_thread.start()

    async def send_notification(self, chat_id, message):
        await self.bot.send_message(chat_id, text=message)

        

    def process_message(self, kafka_message):
        
        kafka_data = json.loads(kafka_message.value().decode('utf-8'))        
        client_id = kafka_data.get('client_id')
        message_text = kafka_data.get('message_text')       
        self.send_notification(client_id, message_text)