import logging
import re

from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
from handlers.aliexpress_handler import (
    expand_aliexpress_short_link,
    ALIEXPRESS_SHORT_URL_PATTERN,
)
from config import (
    AWIN_PUBLISHER_ID,
    AWIN_ADVERTISERS,
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
    MSG_ALIEXPRESS_DISCOUNT,
    ALIEXPRESS_DISCOUNT_CODES,
)

AWIN_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
    "|".join([domain.replace(".", r"\.") for domain in AWIN_ADVERTISERS.keys()])
)
AWIN_AFFILIATE_PATTERN = (
    r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?[\w\d\-\./?=&%]+)"
)

logger = logging.getLogger(__name__)


def convert_to_awin_affiliate_link(url, store_domain):
    """Converts a store link into an Awin affiliate link."""
    logger.info(f"Converting URL to affiliate link: {url}")
    encoded_url = quote_plus(url)
    advertiser_id = AWIN_ADVERTISERS.get(store_domain)

    if advertiser_id:
        affiliate_url = f"https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={AWIN_PUBLISHER_ID}&ued={encoded_url}"
        logger.info(f"Converted URL {url} to affiliate link: {affiliate_url}")
        return affiliate_url

    logger.warning(
        f"No advertiser found for domain: {store_domain}. Returning original URL."
    )
    return url


def modify_existing_awin_link(url):
    """Modifies an existing Awin affiliate link to use the correct publisher ID."""
    logger.info(f"Modifying URL to your affiliate link: {url}")
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Replace the current 'awinaffid' with your own AWIN_PUBLISHER_ID
    query_params["awinaffid"] = [AWIN_PUBLISHER_ID]

    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )
    logger.info(f"Modified URL {url} to affiliate link: {new_url}")

    return new_url


async def handle_awin_links(message) -> bool:
    """Handles Awin-managed store links in the message."""
    logger.info(f"{message.message_id}: Handling Awin links in the message...")

    short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)
    new_text = message.text
    if short_links:
        logger.info(
            f"{message.message_id}: Found {len(short_links)} short AliExpress links. Processing..."
        )
        for short_link in short_links:
            full_link = await expand_aliexpress_short_link(short_link)
            new_text = new_text.replace(short_link, full_link)

    awin_links = re.findall(AWIN_URL_PATTERN, new_text)
    awin_affiliate_links = re.findall(AWIN_AFFILIATE_PATTERN, new_text)

    if awin_links:
        logger.info(
            f"{message.message_id}: Found {len(admitad_links)} Awin links. Processing..."
        )
        for link, store_domain in awin_links:
            affiliate_link = convert_to_awin_affiliate_link(link, store_domain)
            new_text = new_text.replace(link, affiliate_link)
            if "aliexpress" in store_domain:
                new_text += f"\n\n{MSG_ALIEXPRESS_DISCOUNT}{ALIEXPRESS_DISCOUNT_CODES}"
                logger.debug(
                    f"{message.message_id}: Appended AliExpress discount codes."
                )

    if awin_affiliate_links:
        logger.info(
            f"{message.message_id}: Found {len(admitad_affiliate_links)} Awin affiliate links. Processing..."
        )
        for link in awin_affiliate_links:
            modified_link = modify_existing_awin_link(link)
            new_text = new_text.replace(link, modified_link)

    if new_text != message.text:
        reply_to_message_id = (
            message.reply_to_message.message_id if message.reply_to_message else None
        )
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{message.from_user.username}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        await message.delete()
        logger.info(f"{message.message_id}: Original message deleted.")

        await message.chat.send_message(
            text=polite_message, reply_to_message_id=reply_to_message_id
        )
        logger.info(
            f"{message.message_id}: Sent modified message with affiliate links."
        )
        return True

    logger.info(
        f"{message.message_id}: No Awin links found in the message."
    )
    return False