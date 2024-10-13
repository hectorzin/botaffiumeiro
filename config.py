import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join('data', '.env'))

# Accede a las variables del .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
EXCLUDED_USERS = os.getenv("EXCLUDED_USERS").split(",")  # Convierte la lista en una lista de Python
LOG_LEVEL = os.getenv("LOG_LEVEL")

MSG_AFFILIATE_LINK_MODIFIED = os.getenv("MSG_AFFILIATE_LINK_MODIFIED")
MSG_REPLY_PROVIDED_BY_USER = os.getenv("MSG_REPLY_PROVIDED_BY_USER")
MSG_ALIEXPRESS_DISCOUNT = os.getenv("MSG_ALIEXPRESS_DISCOUNT")

AMAZON_AFFILIATE_ID = os.getenv("AMAZON_AFFILIATE_ID")

AWIN_PUBLISHER_ID = os.getenv("AWIN_PUBLISHER_ID")
AWIN_ADVERTISERS = dict(item.split(":") for item in os.getenv("AWIN_ADVERTISERS").split(","))

ADMITAD_PUBLISHER_ID = os.getenv("ADMITAD_PUBLISHER_ID")
ADMITAD_ADVERTISERS = dict(item.split(":") for item in os.getenv("ADMITAD_ADVERTISERS").split(","))


ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
ALIEXPRESS_TRACKING_ID = os.getenv("ALIEXPRESS_TRACKING_ID")
ALIEXPRESS_DISCOUNT_CODES = os.getenv("ALIEXPRESS_DISCOUNT_CODES")
