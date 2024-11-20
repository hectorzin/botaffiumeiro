"""Main module for managing bot functionalities and modifying affiliate links."""

from __future__ import annotations

import logging
import re
import secrets
import threading
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from config import ConfigurationManager
from handlers.aliexpress_api_handler import AliexpressAPIHandler
from handlers.aliexpress_handler import ALIEXPRESS_PATTERN, AliexpressHandler
from handlers.pattern_handler import PatternHandler
from handlers.patterns import PATTERNS
from publicsuffix2 import get_sld
import requests
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    Defaults,
    MessageHandler,
    filters,
)

if TYPE_CHECKING:
    from telegram import Message, Update, User

DOMAIN_PATTERNS = {
    "aliexpress": ALIEXPRESS_PATTERN,
}

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(
    logger.getEffectiveLevel() + 10
    if logger.getEffectiveLevel() < logging.CRITICAL
    else logging.CRITICAL
)

config_manager = ConfigurationManager()


def is_user_excluded(user: User) -> bool:
    """Check if the user is in the list of excluded users."""
    user_id = user.id
    username = user.username
    logger.debug("Checking if user %s (ID: %s) is excluded.", username, user_id)
    excluded_users = config_manager.excluded_users
    excluded = user_id in excluded_users or (username and username in excluded_users)
    logger.debug("User %s (ID: %s) is excluded: %s", username, user_id, excluded)
    return excluded


def expand_shortened_url(url: str) -> str:
    """Expand shortened URLs by following redirects using a HEAD request."""
    logger.info("Try expanding shortened URL: %s", url)
    # Strip trailing punctuation if present
    stripped_url = url.rstrip(".,")
    punctuation = url[
        len(stripped_url) :
    ]  # Store the punctuation for re-attachment if needed
    try:
        response = requests.get(
            stripped_url, allow_redirects=True, timeout=config_manager.TIMEOUT
        )
        expanded_url = response.url
        logger.info("Expanded URL %s to full link: %s", stripped_url, expanded_url)
        return expanded_url + punctuation
    except requests.RequestException:
        logger.exception("Error expanding shortened URL: %s", url)
    return url


def extract_embedded_url(query_params: dict[str, list[str]]) -> set[str]:
    """Extract any valid URLs embedded in query parameters.

    Args:
    ----
        query_params: A dictionary of query parameters from a URL.

    Returns:
    -------
        A set of embedded domains found in the query parameters.

    """
    embedded_domains = set()
    for values in query_params.values():
        for value in values:
            parsed_url = urlparse(value)
            if parsed_url.scheme in ["http", "https"]:  # Check if it's a valid URL
                domain = get_sld(parsed_url.netloc)
                embedded_domains.add(domain)
    return embedded_domains


def extract_domains_from_message(message_text: str) -> tuple[set, str]:
    """Extract domains from a message using domain patterns and searches for embedded URLs.

    Additionally, expands short URLs and replaces them in the message text.

    Args:
    ----
    message_text: The text of the message to search for domains.

    Returns:
    -------
    A tuple containing:
        - A set of domains found in the message.
        - The modified message text with expanded URLs.

    """
    domains = set()

    urls_in_message = re.findall(r"https?://[^\s]+", message_text)

    for url in urls_in_message:
        expanded_url = expand_shortened_url(url)
        message_text = message_text.replace(url, expanded_url)
        parsed_url = urlparse(expanded_url)
        domain = get_sld(parsed_url.netloc)
        query_params = parse_qs(parsed_url.query)
        embedded_domains = extract_embedded_url(query_params)

        if embedded_domains:
            domains.update(embedded_domains)
        else:
            for pattern in DOMAIN_PATTERNS.values():
                if re.match(pattern, expanded_url):
                    domains.add(domain)
            for config in PATTERNS.values():
                if re.match(config["pattern"], expanded_url):
                    domains.add(domain)
                    break

    return domains, message_text


def select_user_for_domain(domain: str) -> dict | None:
    """Select a user for the given domain based on percentages in domain_percentage_table."""
    domain_data = config_manager.domain_percentage_table.get(domain, [])

    if not domain_data:
        return None

    choices = [(entry["user"], entry["percentage"]) for entry in domain_data]

    rand_choice = secrets.SystemRandom().uniform(0, 100)
    current = 0

    for user, percentage in choices:
        current += percentage
        if rand_choice <= current:
            return config_manager.all_users_configurations.get(user, {})

    return config_manager.all_users_configurations.get(choices[0][0], None)


def choose_users(domains: set[str]) -> dict:
    """Handle the domains and selects users randomly based on domain configurations."""
    selected_users = {}
    for domain in domains:
        selected_user_data = select_user_for_domain(domain)
        if selected_user_data:
            selected_users[domain] = selected_user_data
    return selected_users


def prepare_message(message: Message, default_domains: set[str] | None = None) -> dict:
    """Prepare the message by extracting domains, selecting users, and returning a processing context."""
    if not message or not message.text:
        return {
            "message": message,
            "modified_message": None,
            "selected_users": {},
        }

    message_text = message.text
    if default_domains:
        domains = default_domains
        modified_message = message_text
    else:
        domains, modified_message = extract_domains_from_message(message_text)

    selected_users = choose_users(domains)
    return {
        "message": message,
        "modified_message": modified_message,
        "selected_users": selected_users,
    }


async def process_link_handlers(message: Message) -> None:
    """Process all link handlers for Amazon, Awin, Admitad, and AliExpress."""
    logger.info("Processing link handlers for message ID: %s...", message.message_id)
    context = prepare_message(message)
    processed = await PatternHandler(config_manager).handle_links(context)
    processed |= await AliexpressAPIHandler(config_manager).handle_links(context)

    if not processed:
        await AliexpressHandler(config_manager).handle_links(context)

    logger.info(
        "Finished processing link handlers for message ID: %s.", message.message_id
    )


async def modify_link(update: Update, _: CallbackContext) -> None:
    """Modify Amazon, AliExpress, Awin, and Admitad links in messages."""
    logger.info("Received new update (ID: %s).", update.update_id)

    if not update.message or not update.message.text:
        logger.info(
            "%s: Update with a message without text. Skipping.", update.update_id
        )
        return

    if not update.effective_user:
        logger.info("%s: Update without user. Skipping.", update.update_id)
        return

    if is_user_excluded(update.effective_user):
        logger.info(
            "%s: Update with a message from excluded user %s (ID: %s). Skipping.",
            update.update_id,
            update.effective_user.username,
            update.effective_user.id,
        )
        return

    message = update.message
    logger.info(
        "%s: Processing update message (ID: %s)...",
        update.update_id,
        update.message.message_id,
    )

    await process_link_handlers(message)
    logger.info("%s: Update processed.", update.update_id)


def reload_config_periodically(interval: int) -> None:
    """Reload the configuration periodically every `interval` seconds."""
    config_manager.load_configuration()
    threading.Timer(interval, reload_config_periodically, [interval]).start()


async def handle_discount_command(update: Update, context: dict) -> None:
    """Manage discount codes calling 'show_discount_codes' of AliexpressHandler."""
    logger.info("Processing discount command: %s", update.message.text)

    context = prepare_message(update.message, {"aliexpress.com"})
    await AliexpressHandler(config_manager).show_discount_codes(context)

    logger.info("Discount code shown for command: %s", update.message.text)


def register_discount_handlers(application: Application) -> None:
    """Registry dinamically bot discount commands."""
    for keyword in config_manager.discount_keywords:
        application.add_handler(CommandHandler(keyword, handle_discount_command))


def main() -> None:
    """Start the bot application here."""
    # Initialize ConfigurationManager
    config_manager.load_configuration()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=config_manager.log_level,
    )
    logger.info("Configuring the bot")

    # Program a job to reaload config every day
    reload_thread = threading.Thread(
        target=reload_config_periodically, args=(24 * 60 * 60,), daemon=True
    )
    reload_thread.start()

    defaults = Defaults(parse_mode="HTML")
    application = (
        Application.builder().token(config_manager.bot_token).defaults(defaults).build()
    )

    register_discount_handlers(application)
    application.add_handler(
        MessageHandler(filters.ALL & filters.ChatType.GROUPS, modify_link)
    )

    logger.info("Starting the bot")
    application.run_polling()


if __name__ == "__main__":
    main()
