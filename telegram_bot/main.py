import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

register_service = os.environ.get('API_GATEWAY' + "register/", 'http://register:5000/')
token_bot = "6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="welcome to the weather report service, use /help to show a list of commands")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    data = context.args
    if not data or len(context.args)!=4:
        await context.bot.send_message(chat_id, text="Formato registrazione errato /register <città> <tipo_controllo> <condizione> <valore>")
    else:
        requests.get(register_service + "register", {'id': chat_id, 'data[]': context.args})

if __name__ == '__main__':
    application = ApplicationBuilder().token(token_bot).build()
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.run_polling()