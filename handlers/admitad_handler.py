import logging
import re

from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
from handlers.aliexpress_handler import (
    expand_aliexpress_short_link,
    ALIEXPRESS_SHORT_URL_PATTERN,
)
from config import (
    ADMITAD_PUBLISHER_ID,
    ADMITAD_ADVERTISERS,
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
    ALIEXPRESS_DISCOUNT_CODES,
    DELETE_MESSAGES,
)

ADMITAD_AFFILIATE_PATTERN = (
    r"(https?://(?:[\w\-]+\.)?ad\.admitad\.com/g/[\w\d]+/[\w\d]+/[\w\d\-\./?=&%]+)"
)

logger = logging.getLogger(__name__)


def convert_to_admitad_affiliate_link(url, store_domain):
    """Converts a store link into an Admitad affiliate link."""    
    logger.info(f"Converting URL to affiliate link: {url}")
    encoded_url = quote_plus(url)
    advcampaignid = ADMITAD_ADVERTISERS.get(store_domain)

    if advcampaignid:
        affiliate_url = f"https://ad.admitad.com/g/{advcampaignid}/{ADMITAD_PUBLISHER_ID}/?ulp={encoded_url}"
        logger.info(f"Converted URL {url} to affiliate link: {affiliate_url}")
        return affiliate_url

    logger.warning(
        f"No advertiser found for domain: {store_domain}. Returning original URL."
    )
    return url


def modify_existing_admitad_link(url):
    """Modifies an existing Admitad affiliate link to use the correct publisher ID."""    
    logger.info(f"Modifying URL to your affiliate link: {url}")
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    path_segments = parsed_url.path.split("/")
    if len(path_segments) >= 4:
        original_advcampaignid = path_segments[2]
        path_segments[2] = ADMITAD_ADVERTISERS.get(
            original_advcampaignid, original_advcampaignid
        ) 
        path_segments[3] = ADMITAD_PUBLISHER_ID

    new_path = "/".join(path_segments)
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )
    logger.info(f"Modified URL {url} to affiliate link: {new_url}")

    return new_url


async def handle_admitad_links(message) -> bool:
    """Handles Admitad-managed store links in the message."""
    if not ADMITAD_PUBLISHER_ID:
        logger.info("Awin affiliate ID is not set. Skipping processing.")
        return False

    logger.info(f"{message.message_id}: Handling Admitad links in the message...")

    short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)
    new_text = message.text
    if short_links:
        logger.info(
            f"{message.message_id}: Found {len(short_links)} short AliExpress links. Processing..."
        )
        for short_link in short_links:
            full_link = await expand_aliexpress_short_link(short_link)
            new_text = new_text.replace(short_link, full_link)

    ADMITAD_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
        "|".join([domain.replace(".", r"\.") for domain in ADMITAD_ADVERTISERS.keys()])
    )

    admitad_links = re.findall(ADMITAD_URL_PATTERN, new_text)
    admitad_affiliate_links = re.findall(ADMITAD_AFFILIATE_PATTERN, new_text)

    if admitad_affiliate_links:
        logger.info(
            f"{message.message_id}: Found {len(admitad_affiliate_links)} Admitad affiliate links. Processing..."
        )
        for link in admitad_affiliate_links:
            if len(admitad_links) == 0:
                return False         
            modified_link = modify_existing_admitad_link(link)
            new_text = new_text.replace(link, modified_link)
    elif admitad_links:
        logger.info(
            f"{message.message_id}: Found {len(admitad_links)} Admitad links. Processing..."
        )
        for link, store_domain in admitad_links:
            affiliate_link = convert_to_admitad_affiliate_link(link, store_domain)
            new_text = new_text.replace(link, affiliate_link)
            if "aliexpress" in store_domain:
                new_text += f"\n\n{ALIEXPRESS_DISCOUNT_CODES}"
                logger.debug(
                    f"{message.message_id}: Appended AliExpress discount codes."
                )

    if new_text != message.text:
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{message.from_user.username}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"

        if DELETE_MESSAGES:
            reply_to_message_id = (
                message.reply_to_message.message_id if message.reply_to_message else None
            )
            # Deletes the original message and creates a new one
            await message.delete()
            await message.chat.send_message(
                text=polite_message, reply_to_message_id=reply_to_message_id
            )
            logger.info(f"{message.message_id}: Original message deleted annd sent modified message with affiliate links.")
        else:
            # Replies to the original message without deleting it
            await message.chat.send_message(
                text=polite_message, reply_to_message_id=message.message_id
            )
            logger.info(f"{message.message_id}: Replied to the original message with affiliate links.")

        return True

    logger.info(
        f"{message.message_id}: No Admitad links found in the message."
    )
    return False
