import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

class WeatherBot:
    def __init__(self, token_bot, register_endpoint, remove_endpoint):
        self.config["token"] = token_bot
        self.config["register"] = register_endpoint
        self.config["remove"] = remove_endpoint

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        self.bot = ApplicationBuilder().token(self.config["token"]).build()
        self.addCommandHandlers()


    async def startAction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, text="Welcome to the weather report service, use /help to show a list of commands")

    async def registerAction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.from_user.id
        data = context.args
        if not data or len(context.args) != 4:
            await context.bot.send_message(chat_id, text="Invalid registration format. Usage: /register <city> <control_type> <condition> <value>")
        else:
            requests.get(self.config["register"] + "register", {'id': chat_id, 'data[]': context.args})

    async def removeAction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.from_user.id
        city = context.args
        if not city:
            await context.bot.send_message(chat_id, text="Invalid command format: Specify the city to stop receiving updates.")
        else:
            requests.get(self.config["remove"] + "remove", {'id': chat_id, 'city': context.args})

    def addCommandHandlers(self):
        start_handler = CommandHandler('start', self.startAction)
        register_handler = CommandHandler('register', self.registerAction)
        remove_handler = CommandHandler('remove', self.removeAction)
        self.bot.add_handler(start_handler)
        self.bot.add_handler(register_handler)
        self.bot.add_handler(remove_handler)

    def run(self):
        self.bot.run_polling()