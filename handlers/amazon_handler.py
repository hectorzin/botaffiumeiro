import logging
import re
import requests

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from config import (
    AMAZON_AFFILIATE_ID,
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
    DELETE_MESSAGES,
)

AMAZON_URL_PATTERN = r"(https?://(?:www\.)?(amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)/[\w\d\-\./?=&%]+)"

logger = logging.getLogger(__name__)


def expand_shortened_url(url):
    """Expands shortened URLs like amzn.to or amzn.eu by following redirects."""
    logger.info(f"Try expanding shortened URL: {url}")
    parsed_url = urlparse(url)
    if "amzn.to" in parsed_url.netloc or "amzn.eu" in parsed_url.netloc:
        try:
            response = requests.get(url, allow_redirects=True)
            logger.debug(f"Expanded URL {url} to full link: {response.url}")
            return response.url
        except requests.RequestException as e:
            logger.error(f"Error expanding shortened URL {url}: {e}")
            return url
    return url


def convert_to_affiliate_link(url):
    """Convert an Amazon link to an affiliate link."""
    logger.info(f"Converting URL to affiliate link: {url}")
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params.pop("tag", None)
    query_params["tag"] = [AMAZON_AFFILIATE_ID]

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
    logger.info(f"Converted URL {url} to affiliate link: {new_url}")

    return new_url


async def handle_amazon_links(message) -> bool:
    """Handles Amazon links in the message."""
    logger.info(f"{message.message_id}: Handling Amazon links in the message...")
    amazon_links = re.findall(AMAZON_URL_PATTERN, message.text)

    if amazon_links:
        logger.info(
            f"{message.message_id}: Found {len(amazon_links)} Amazon links. Processing..."
        )
        new_text = message.text
        for link in amazon_links:
            # Ensure link is a string, extract from tuple if needed
            if isinstance(link, tuple):
                link = link[0]

            expanded_link = expand_shortened_url(link)
            affiliate_link = convert_to_affiliate_link(expanded_link)
            new_text = new_text.replace(link, affiliate_link)

        user_first_name = message.from_user.first_name
        user_username = message.from_user.username
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"

        if DELETE_MESSAGES:
            # remove original message and creates a new one
            await message.delete()
            await message.chat.send_message(text=polite_message)
            logger.info(f"{message.message_id}: Original message deleted annd sent modified message with affiliate links.")
        else:
            # Answers the original message
            reply_to_message_id = message.message_id
            await message.chat.send_message(text=polite_message, reply_to_message_id=reply_to_message_id)
            logger.info(f"{message.message_id}: Replied to message with affiliate links.")

        return True

    logger.info(f"{message.message_id}: No Amazon links found in the message.")
    return False
