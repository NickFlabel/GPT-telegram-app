import logging
import os
import dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from .command_handlers import callback
from .callback_classes.callback_classes import Start, MessageCallback, ConversationHandler

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_API_URL = os.getenv('DB_API_URL')


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', Start.get_callback_function())
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, MessageCallback.get_callback_function()))
    application.add_handler(CommandHandler('conversations', ConversationHandler.get_callback_function()))
    application.add_handler(CallbackQueryHandler(callback))

    application.run_polling()