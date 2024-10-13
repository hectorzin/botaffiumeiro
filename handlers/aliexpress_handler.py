import logging
import httpx
import re

from config import (
    ALIEXPRESS_DISCOUNT_CODES,
    ALIEXPRESS_APP_KEY,
    MSG_ALIEXPRESS_DISCOUNT,
    AWIN_ADVERTISERS,
    ADMITAD_ADVERTISERS,
)

ALIEXPRESS_URL_PATTERN = r"(https?://(?:[a-z]{2,3}\.)?aliexpress\.[a-z]{2,3}(?:\.[a-z]{2})?/(?:[\w\d\-\./?=&%]+))"
ALIEXPRESS_SHORT_URL_PATTERN = r"https?://s\.click\.aliexpress\.com/e/[\w\d_]+"

logger = logging.getLogger(__name__)

async def expand_aliexpress_short_link(short_url):
    """Expands a short AliExpress link into its full URL by following redirects."""
    logger.info(f"Try expanding shortened URL: {short_url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(short_url)
            expanded_url = (
                str(response.url) if response.status_code == 200 else short_url
            )
            logger.debug(f"Expanded URL {short_url} to full link: {response.url}")
            return expanded_url
    except Exception as e:
        logger.error(f"Error expanding short URL {short_url}: {e}")
        return short_url

async def handle_aliexpress_links(message) -> bool:
    # Check if discount codes and message are not empty before proceeding
    if not MSG_ALIEXPRESS_DISCOUNT or not ALIEXPRESS_DISCOUNT_CODES:
        logger.info(
            f"{message.message_id}: Discount message or codes are empty. Skipping reply."
        )
        return True  # Exit the function if both variables are empty

    """Handles both long and short AliExpress links in the message."""
    logger.info(f"{message.message_id}: Handling AliExpress links in the message...")

    aliexpress_links = re.findall(ALIEXPRESS_URL_PATTERN, message.text)
    aliexpress_short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)
    all_aliexpress_links = aliexpress_links + aliexpress_short_links

    if all_aliexpress_links:
        logger.info(
            f"{message.message_id}: Found {len(all_aliexpress_links)} AliExpress links. Processing..."
        )
        if (
            "aliexpress.com" in AWIN_ADVERTISERS
            or "aliexpress.com" in ADMITAD_ADVERTISERS
            or ALIEXPRESS_APP_KEY != ""
        ):
            logger.info(
                f"{message.message_id}: AliExpress links found in advertisers. Skipping processing."
            )
            return False

        logger.info(
            f"{message.message_id}: No advertiser found for AliExpress. Sending discount codes."
        )
        await message.chat.send_message(
            f"{MSG_ALIEXPRESS_DISCOUNT}{ALIEXPRESS_DISCOUNT_CODES}",
            reply_to_message_id=message.message_id,
        )
        logger.info(
            f"{message.message_id}: Sent modified message with affiliate links."
        )
        return True

    logger.info(f"{message.message_id}: No AliExpress links found in the message.")
    return False
