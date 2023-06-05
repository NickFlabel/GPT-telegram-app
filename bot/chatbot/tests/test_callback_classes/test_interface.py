from telegram import Update
from telegram.ext import ContextTypes
from ..fixtures import update, context, urls
from ...data_api import User
import pytest
from ..utils import URLDirector
import dotenv
import os
import json

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')
