import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_B2Bro_TOKEN")
DB_PATH = 'speaker_sizes.db'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")