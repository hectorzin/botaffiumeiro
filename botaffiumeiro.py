import logging
import random
import re
import requests
import threading

from publicsuffix2 import get_sld
from telegram import Update, User
from telegram.ext import Application, CommandHandler, Defaults, filters, MessageHandler
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from handlers.admitad_handler import AdmitadHandler, ADMITAD_PATTERN
from handlers.aliexpress_api_handler import AliexpressAPIHandler
from handlers.aliexpress_handler import AliexpressHandler, ALIEXPRESS_PATTERN
from handlers.amazon_handler import AmazonHandler, AMAZON_PATTERN
from handlers.awin_handler import AwinHandler, AWIN_PATTERN
from config import (
    config_data,
    domain_percentage_table,
    all_users_configurations,
    load_configuration,
)

SHORT_URL_DOMAINS = ["amzn.to", "s.click.aliexpress.com", "bit.ly", "tinyurl.com"]
DOMAIN_PATTERNS = {
    "amazon": AMAZON_PATTERN,
    "aliexpress": ALIEXPRESS_PATTERN,
    "awin": AWIN_PATTERN,
    "admitad": ADMITAD_PATTERN,
}
#    "aliexpress_short_url_pattern": r"https?://s\.click\.aliexpress\.com/e/[\w\d_]+",

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=config_data["LOG_LEVEL"],
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(
    logger.getEffectiveLevel() + 10
    if logger.getEffectiveLevel() < logging.CRITICAL
    else logging.CRITICAL
)


def is_user_excluded(user: User) -> bool:
    """Checks if the user is in the list of excluded users."""

    user_id = user.id
    username = user.username
    logger.debug(f"Checking if user {username} (ID: {user_id}) is excluded.")
    excluded_users = config_data["EXCLUDED_USERS"]
    excluded = user_id in excluded_users or (username and username in excluded_users)
    logger.debug(f"User {username} (ID: {user_id}) is excluded: {excluded}")
    return excluded


def expand_shortened_url(url: str):
    """Expands shortened URLs by following redirects using a HEAD request."""
    logger.info(f"Try expanding shortened URL: {url}")
    try:
        # Utilizamos HEAD para seguir las redirecciones sin descargar todo el contenido
        response = requests.head(url, allow_redirects=True)
        logger.info(f"Expanded URL {url} to full link: {response.url}")
        return response.url
    except requests.RequestException as e:
        logger.error(f"Error expanding shortened URL {url}: {e}")
    return url


def extract_embedded_url(query_params):
    """
    Extracts any valid URLs embedded in query parameters.

    Parameters:
    - query_params: A dictionary of query parameters from a URL.

    Returns:
    - A set of embedded domains found in the query parameters.
    """
    embedded_domains = set()
    for key, values in query_params.items():
        for value in values:
            # Check if the value contains a valid URL
            parsed_url = urlparse(value)
            if parsed_url.scheme in ["http", "https"]:  # Check if it's a valid URL
                domain = get_sld(parsed_url.netloc)
                embedded_domains.add(domain)
    return embedded_domains


def is_short_url(url: str) -> bool:
    """
    Checks if the given URL belongs to a known short URL domain.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc in SHORT_URL_DOMAINS


def extract_domains_from_message(message_text: str) -> Tuple[set, str]:
    """
    Extracts domains from a message using domain patterns and searches for embedded URLs.
    Additionally, expands short URLs and replaces them in the message text.

    Parameters:
    - message_text: The text of the message to search for domains.

    Returns:
    - A tuple containing:
        - A set of domains found in the message.
        - The modified message text with expanded URLs.
    """
    domains = set()

    # Find all URLs in the message (this can be expanded to handle more complex URL detection)
    urls_in_message = re.findall(r"https?://[^\s]+", message_text)

    for url in urls_in_message:
        # If it's a short URL, expand it
        if is_short_url(url):
            expanded_url = expand_shortened_url(url)
            # Replace the short URL with the expanded URL in the message text
            message_text = message_text.replace(url, expanded_url)
        else:
            expanded_url = url

        # Now extract the domain from the expanded URL
        parsed_url = urlparse(expanded_url)
        # uses a external library to extract the domain, detecting things lik amazon.co.uk, etc.
        domain = get_sld(parsed_url.netloc)

        # Parse the query parameters and check if any of them contains an embedded URL
        query_params = parse_qs(parsed_url.query)
        embedded_domains = extract_embedded_url(query_params)

        # If embedded domains exist, use them instead of the main domain
        if embedded_domains:
            domains.update(embedded_domains)
        else:
            # Loop through the patterns for each platform
            for platform, pattern in DOMAIN_PATTERNS.items():
                if re.match(pattern, expanded_url):
                    domains.add(domain)

    return domains, message_text


def select_user_for_domain(domain):
    """
    Selects a user for the given domain based on percentages in domain_percentage_table.

    Parameters:
    - domain: The domain to select the user for (e.g., "amazon")

    Returns:
    - The user_data for the selected user, or the first user's data if no random selection occurs.
    """
    # Get the domain data from the table
    domain_data = domain_percentage_table.get(domain, [])

    if not domain_data:
        return None  # No entries for this domain

    # Prepare the list of users and their percentages for selection
    choices = [(entry["user"], entry["percentage"]) for entry in domain_data]

    # Generate a random number and select based on percentages
    rand_choice = random.uniform(0, 100)  # Random number between 0 and 100
    current = 0

    for user, percentage in choices:
        current += percentage
        if rand_choice <= current:
            # Return the user data for the selected user
            return all_users_configurations.get(user, {})

    # If no match was found (which shouldn't happen), return the first user's data
    return all_users_configurations.get(choices[0][0], None)


def choose_users(domains) -> dict:
    """
    Handles the domains and selects users randomly based on domain configurations.

    Parameters:
    - domains: List of domains extracted from the message.

    Returns:
    - A dictionary of selected users mapped by their respective domains.
    """
    selected_users = {}

    # Loop through each domain and select a user for that domain
    for domain in domains:
        selected_user_data = select_user_for_domain(domain)
        if selected_user_data:
            selected_users[domain] = selected_user_data

    return selected_users


def prepare_message(message, default_domains=None) -> dict:
    """
    Prepares the message by extracting domains, selecting users, and returning a processing context.

    Parameters:
    - message: The message object containing the text with links.
    - default_domains: An optional list of domains to consider if the message is a command or lacks domains.

    Returns:
    - A dictionary (context) containing:
        - The original message (or None if not provided).
        - The modified message text with expanded URLs (or None if not applicable).
        - A dictionary of selected users mapped to their respective domains (or empty if no users).
    """
    if not message or not message.text:
        return {
            "message": message,  # Original message (None if not provided)
            "modified_message": None,  # No modification since there was no valid message
            "selected_users": {},  # No users selected as there are no domains
        }

    message_text = message.text
    # Extract domains and the modified message text
    if default_domains:
        domains = default_domains
        modified_message = message_text
    else:
        domains, modified_message = extract_domains_from_message(message_text)

    # Select users for each domain
    selected_users = choose_users(domains)

    # Create the processing context
    context = {
        "message": message,  # Original message
        "modified_message": modified_message,  # Message with expanded URLs (if applicable)
        "selected_users": selected_users,  # Dictionary of selected users by domain
    }

    return context


async def process_link_handlers(message) -> None:
    """Process all link handlers for Amazon, Awin, Admitad, and AliExpress."""

    logger.info(f"Processing link handlers for message ID: {message.message_id}...")

    context = prepare_message(message)

    await AmazonHandler().handle_links(context)
    await AwinHandler().handle_links(context)
    await AdmitadHandler().handle_links(context)
    await AliexpressAPIHandler().handle_links(context)
    await AliexpressHandler().handle_links(context)

    logger.info(
        f"Finished processing link handlers for message ID: {message.message_id}."
    )


async def modify_link(update: Update, context) -> None:
    """Modifies Amazon, AliExpress, Awin, and Admitad links in messages."""

    logger.info(f"Received new update (ID: {update.update_id}).")

    if not update.message or not update.message.text:
        logger.info(
            f"{update.update_id}: Update with a message without text. Skipping."
        )
        return

    if not update.effective_user:
        logger.info(f"{update.update_id}: Update without user. Skipping.")
        return

    if is_user_excluded(update.effective_user):
        logger.info(
            f"{update.update_id}: Update with a message from excluded user {update.effective_user.username} (ID: {update.effective_user.id}). Skipping."
        )
        return

    message = update.message

    logger.info(
        f"{update.update_id}: Processing update message (ID: {update.message.message_id})..."
    )

    await process_link_handlers(message)

    logger.info(f"{update.update_id}: Update processed.")


def reload_config_periodically(interval):
    """
    Function to reload the configuration periodically every `interval` seconds.
    """
    load_configuration()
    threading.Timer(interval, reload_config_periodically, [interval]).start()


async def handle_discount_command(update: Update, context) -> None:
    """
    Maneja los comandos de descuento llamando a la función 'show_discount_codes' de AliexpressHandler.
    """
    logger.info(f"Processing discount command: {update.message.text}")

    context = prepare_message(update.message, ["aliexpress.com"])
    await AliexpressHandler().show_discount_codes(context)

    logger.info(f"Discount code shown for command: {update.message.text}")


def register_discount_handlers(application):
    """
    Registra dinámicamente todos los comandos de descuento en el bot.
    """
    for keyword in config_data["DISCOUNT_KEYWORDS"]:
        application.add_handler(CommandHandler(keyword, handle_discount_command))


def main() -> None:
    """Start the bot with python-telegram-bot"""
    load_configuration()
    logger.info("Configuring the bot")

    # Program a job to reaload config every day
    reload_thread = threading.Thread(
        target=reload_config_periodically, args=(24 * 60 * 60,), daemon=True
    )
    reload_thread.start()

    defaults = Defaults(parse_mode="HTML")
    application = (
        Application.builder().token(config_data["BOT_TOKEN"]).defaults(defaults).build()
    )

    register_discount_handlers(application)
    application.add_handler(
        MessageHandler(filters.ALL & filters.ChatType.GROUPS, modify_link)
    )

    logger.info("Starting the bot")
    application.run_polling()


if __name__ == "__main__":
    main()
