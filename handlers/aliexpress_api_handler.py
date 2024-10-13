import logging
import re
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from handlers.aliexpress_handler import expand_aliexpress_short_link, ALIEXPRESS_URL_PATTERN, ALIEXPRESS_SHORT_URL_PATTERN 
from config import (
    ALIEXPRESS_APP_KEY,
    ALIEXPRESS_APP_SECRET,
    ALIEXPRESS_TRACKING_ID,
    MSG_REPLY_PROVIDED_BY_USER,
    MSG_AFFILIATE_LINK_MODIFIED,
    ALIEXPRESS_DISCOUNT_CODES
)

# Initialize logger
logger = logging.getLogger(__name__)

# API endpoint for generating affiliate links
ALIEXPRESS_API_URL = "https://api-sg.aliexpress.com/sync"

# Function to generate HMAC-SHA256 signature
def generate_signature(secret, params):
    """Generates HMAC-SHA256 signature."""
    logger.info("Generating HMAC-SHA256 signature for API request.")
    sorted_params = sorted((k, v) for k, v in params.items() if k != 'sign')
    concatenated_params = ''.join(f"{k}{v}" for k, v in sorted_params)
    signature = hmac.new(secret.encode('utf-8'), concatenated_params.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    logger.debug(f"Generated signature: {signature}")
    return signature

async def convert_to_aliexpress_affiliate(source_url):
    """Converts a regular AliExpress link into an affiliate link using the Aliexpress API."""
    logger.info(f"Converting AliExpress link to affiliate link: {source_url}")
    timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds

    params = {
        'app_key': ALIEXPRESS_APP_KEY,
        'timestamp': timestamp,
        'sign_method': 'hmac-sha256',
        'promotion_link_type': '0',
        'source_values': source_url,
        'tracking_id': ALIEXPRESS_TRACKING_ID,
        'method': 'aliexpress.affiliate.link.generate',
    }

    # Generate the signature
    signature = generate_signature(ALIEXPRESS_APP_SECRET, params)
    params['sign'] = signature

    # Make the request to the Aliexpress API
    try:
        response = requests.get(ALIEXPRESS_API_URL, params=params)
        logger.info(f"API request sent. Status code: {response.status_code}")
        data = response.json()

        resp_result = data.get('aliexpress_affiliate_link_generate_response', {}).get('resp_result', {})
        if resp_result.get('resp_code') == 200:
            result = resp_result.get('result', {})
            promotion_links = result.get('promotion_links', {}).get('promotion_link', [])
            if promotion_links:
                promotion_link = promotion_links[0].get('promotion_link')
                logger.info(f"Successfully retrieved affiliate link: {promotion_link}")
                return promotion_link
            else:
                logger.warning("No promotion links found in the response.")
        else:
            logger.error(f"API error. Code: {resp_result.get('resp_code')}, Message: {resp_result.get('resp_msg')}")
    except Exception as e:
        logger.error(f"Error converting link to affiliate: {e}")

    return None

async def handle_aliexpress_api_links(message):
    """Handles AliExpress links and converts them using the Aliexpress API."""
    if not ALIEXPRESS_APP_KEY:
        logger.info("AliExpress API key is not set. Skipping processing.")
        return False

    logger.info(f"{message.message_id}: Handling AliExpress links in the message...")

    new_text = message.text
    aliexpress_links = re.findall(ALIEXPRESS_URL_PATTERN, new_text)
    aliexpress_short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, new_text)

    all_aliexpress_links = aliexpress_links + aliexpress_short_links

    if not all_aliexpress_links:
        logger.info(f"{message.message_id}: No AliExpress links found in the message.")
        return False

    logger.info(f"{message.message_id}: Found {len(all_aliexpress_links)} AliExpress links. Processing...")
    for link in all_aliexpress_links:
        if "s.click.aliexpress" in link:
            link = await expand_aliexpress_short_link(link)
            logger.info(f"{message.message_id}: Expanded short AliExpress link: {link}")

        affiliate_link = await convert_to_aliexpress_affiliate(link)
        if affiliate_link:
            new_text = new_text.replace(link, affiliate_link)

    new_text += f"\n\n{ALIEXPRESS_DISCOUNT_CODES}"
    logger.debug(f"{message.message_id}: Appended AliExpress discount codes.")

    if new_text != message.text:
        reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{message.from_user.username}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        await message.delete()
        logger.info(f"{message.message_id}: Original message deleted.")

        await message.chat.send_message(text=polite_message, reply_to_message_id=reply_to_message_id)
        logger.info(f"{message.message_id}: Sent modified message with affiliate links.")
        return True

    logger.info(f"{message.message_id}: No modifications made to the message.")
    return False
