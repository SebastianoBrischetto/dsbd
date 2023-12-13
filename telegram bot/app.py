import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="welcome to the weather report service, use /help to show a list of commands")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    cities = context.args
    if not cities:
        await context.bot.send_message(chat_id, text="Devi registrarti ad almeno una città")
    else:
        requests.get("http://127.0.0.1:5000/register", {'chat_id': chat_id, 'cities[]': context.args})

if __name__ == '__main__':
    application = ApplicationBuilder().token('6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE').build()
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.run_polling()