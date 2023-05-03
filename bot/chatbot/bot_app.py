import logging
import os
import dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from command_handlers import start, prompt, get_dialogs

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_API_URL = os.getenv('DB_API_URL')


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prompt))
    application.add_handler(CommandHandler('dialogs', get_dialogs))

    application.run_polling()