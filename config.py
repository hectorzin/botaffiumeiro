import yaml

CONFIG_PATH = 'data/config.yaml'

with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config_data = yaml.safe_load(file)

# Telegram settings
BOT_TOKEN = config_data.get('telegram', {}).get('bot_token', None)  # None if not set
EXCLUDED_USERS = config_data.get('telegram', {}).get('excluded_users', [])

# Messages
MSG_AFFILIATE_LINK_MODIFIED = config_data.get('messages', {}).get('affiliate_link_modified', 'Here is the modified link with our affiliate program:')
MSG_REPLY_PROVIDED_BY_USER = config_data.get('messages', {}).get('reply_provided_by_user', 'Reply provided by')

# Amazon settings
AMAZON_AFFILIATE_ID = config_data.get('amazon', {}).get('affiliate_id', None)

# Awin settings
AWIN_PUBLISHER_ID = config_data.get('awin', {}).get('publisher_id', None)
AWIN_ADVERTISERS = config_data.get('awin', {}).get('advertisers', {})

# Admitad settings
ADMITAD_PUBLISHER_ID = config_data.get('admitad', {}).get('publisher_id', None)
ADMITAD_ADVERTISERS = config_data.get('admitad', {}).get('advertisers', {})

# AliExpress settings
ALIEXPRESS_APP_KEY = config_data.get('aliexpress', {}).get('app_key', None)
ALIEXPRESS_APP_SECRET = config_data.get('aliexpress', {}).get('app_secret', None)
ALIEXPRESS_TRACKING_ID = config_data.get('aliexpress', {}).get('tracking_id', None)
ALIEXPRESS_DISCOUNT_CODES = config_data.get('aliexpress', {}).get('discount_codes', 'No discount codes available')

# Logging Level
LOG_LEVEL = config_data.get('log_level', 'INFO')
