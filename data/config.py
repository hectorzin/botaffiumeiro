# --------------------------- CONFIGURATION --------------------------- #

# API and bot credentials
BOT_TOKEN = "your_bot_token_here"  # Replace with your bot token

# List of users (by username or ID) who are excluded from Amazon link modification
EXCLUDED_USERS = [
    "HectorziN",
    "User2",
]  # Replace with the usernames or Telegram IDs of excluded users

# --------------------------- AMAZON --------------------------- #
# Set your Amazon Affiliate ID
AMAZON_AFFILIATE_ID = "botaffiumeiro_cofee-21"  # Replace with your Amazon Affiliate ID

# --------------------------- AWIN --------------------------- #
# Set your Awin Publisher ID (for PcComponentes)
AWIN_PUBLISHER_ID = "1639881"  # Replace with your Awin Publisher ID
# Awin stores and their advertiser IDs
AWIN_ADVERTISERS = {
    "pccomponentes.com": "20982",
    "leroymerlin.es": "20598",
}

# --------------------------- ADMITAD --------------------------- #
# Admitad Publisher ID
ADMITAD_PUBLISHER_ID = "2306205"  # Reemplaza con tu Publisher ID de Admitad

# Admitad Advertisers (store_domain: advcampaignid)
ADMITAD_ADVERTISERS = {
    "aliexpress.com": "1e8d114494873a1e301416525dc3e8",  # Reemplaza con el ID de campaña correspondiente
    "giftmio.com": "93fd4vbk6c873a1e3014d68450d763",
    # Añade más tiendas con sus IDs de campaña
}

# --------------------------- ALIEXPRESS --------------------------- #
# AliExpress discount codes (changeable)
ALIEXPRESS_DISCOUNT_CODES = """💰2$ off for purchases over 20$:【IFPTKOH】
💰5$ off for purchases over 50$:【IFPT35D】
💰25$ off for purchases over 200$:【IFPQDMH】
💰50$ off for purchases over 400$:【IFP5RIN】"""

# --------------------------- MESSAGES --------------------------- #
# Messages used by the bot in its responses
MSG_AFFILIATE_LINK_MODIFIED = (
    "Here is the modified link with our affiliate program:"
)
MSG_REPLY_PROVIDED_BY_USER = "Reply provided by"
MSG_ALIEXPRESS_DISCOUNT = "💥 AliExpress discount codes:\n\n"
