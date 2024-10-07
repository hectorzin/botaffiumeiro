import re
import httpx
from data.config import ALIEXPRESS_DISCOUNT_CODES, MSG_ALIEXPRESS_DISCOUNT, AWIN_ADVERTISERS, ADMITAD_ADVERTISERS

# Pattern to detect long AliExpress links
ALIEXPRESS_URL_PATTERN = r"(https?://(?:[a-z]{2,3}\.)?aliexpress\.[a-z]{2,3}(?:\.[a-z]{2})?/(?:[\w\d\-\./?=&%]+))"

# Pattern to detect short AliExpress links
ALIEXPRESS_SHORT_URL_PATTERN = r"https?://s\.click\.aliexpress\.com/e/[\w\d_]+"

async def expand_aliexpress_short_link(short_url):
    """Expands a short AliExpress link into its full URL by following redirects."""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(short_url)
            return str(response.url) if response.status_code == 200 else short_url
    except Exception as e:
        print(f"Error expanding short URL {short_url}: {e}")
        return short_url

async def handle_aliexpress_links(message) -> bool:
    """Handles both long and short AliExpress links in the message."""
    # Detect both long and short AliExpress links
    aliexpress_links = re.findall(ALIEXPRESS_URL_PATTERN, message.text)
    aliexpress_short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)

    # Combine both short and long links into a single list
    all_aliexpress_links = aliexpress_links + aliexpress_short_links

    # If there are any AliExpress links in the message
    if all_aliexpress_links:
        # Check if aliexpress.com is in AWIN_ADVERTISERS or ADMITAD_ADVERTISERS
        if "aliexpress.com" in AWIN_ADVERTISERS or "aliexpress.com" in ADMITAD_ADVERTISERS:
            # If it's in either list, do nothing because the other handlers will process it
            return False

        # If not in any advertiser list, send the discount codes
        await message.chat.send_message(
            f"{MSG_ALIEXPRESS_DISCOUNT}{ALIEXPRESS_DISCOUNT_CODES}",
            reply_to_message_id=message.message_id
        )
        return True

    # Return False if no AliExpress links were found
    return False
