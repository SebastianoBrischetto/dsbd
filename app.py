import logging
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="hello")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    request = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    await context.bot.send_message(chat_id=update.message.chat_id, text=f"User {user_id} registered!")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE').build()
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.run_polling()

#register registra l'utente a una citta
#delete cancella la registrazione a una citta
#unsubscribe cancella tutto
#help ritorna i comandi