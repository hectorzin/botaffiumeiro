import logging
import yaml
import requests

from datetime import datetime, timedelta

# Rutas a los archivos de configuración
CONFIG_PATH = "data/config.yaml"
CREATORS_CONFIG_PATH = "creators_affiliates.yaml"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

domain_percentage_table = {}
all_users_configurations = {}

config_data = {
    # Telegram
    "BOT_TOKEN": "",
    "DELETE_MESSAGES": "",
    "EXCLUDED_USERS": "",
    # Messages
    "MSG_AFFILIATE_LINK_MODIFIED": "",
    "MSG_REPLY_PROVIDED_BY_USER": "",
    # feed the authors
    "CREATOR_PERCENTAGE": "",
    # Logging Level
    "LOG_LEVEL": "",
}


last_load_time = None


def load_user_configuration(user, creator_percentage, user_data):
    """
    Load user-specific configuration for affiliate programs and settings
    without including global items like API tokens or messages.
    """
    return {
        "user": user,
        "percentage": creator_percentage,
        "amazon": {
            "advertisers": user_data.get("amazon", {}),
        },
        "awin": {
            "publisher_id": user_data.get("awin", {}).get("publisher_id", None),
            "advertisers": user_data.get("awin", {}).get("advertisers", {}),
        },
        "admitad": {
            "publisher_id": user_data.get("admitad", {}).get("publisher_id", None),
            "advertisers": user_data.get("admitad", {}).get("advertisers", {}),
        },
        "aliexpress": {
            "discount_codes": user_data.get("aliexpress", {}).get(
                "discount_codes", None
            ),
            "app_key": user_data.get("aliexpress", {}).get("app_key", None),
            "app_secret": user_data.get("aliexpress", {}).get("app_secret", None),
            "tracking_id": user_data.get("aliexpress", {}).get("tracking_id", None),
        },
    }


def load_user_configuration_from_url(user_id, percentage, url):
    """
    Load user-specific configuration from a URL.

    Parameters:
    - user_id: ID of the user.
    - url: URL to fetch the user's configuration YAML file.

    Returns:
    - Dictionary containing user configuration data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        user_data = yaml.safe_load(response.text)
        return load_user_configuration(
            user_id, percentage, user_data.get("configuration", {})
        )
    except Exception as e:
        logger.error(f"Error loading configuration for {user_id} from {url}: {e}")
        return None


def add_to_domain_table(domain, user_id, affiliate_id, percentage):
    """
    Adds a user to the domain percentage table if they have an ID for the given domain.

    Parameters:
    - domain: The domain name to add to the table (e.g., "amazon", "aliexpress").
    - user_id: The ID of the user (e.g., "user", "HectorziN").
    - affiliate_id: The affiliate ID for the given domain.
    - percentage: The percentage of time this user should be selected for the domain.
    """
    if affiliate_id:
        if domain not in domain_percentage_table:
            domain_percentage_table[domain] = []

        domain_percentage_table[domain].append(
            {"user": user_id, "percentage": percentage}
        )


def add_affiliate_stores_domains(user_id, advertisers, platform_key, percentage):
    """
    Processes multiple domains for networks like Awin or Admitad.

    Parameters:
    - user_id: The ID of the user (e.g., "user", "HectorziN")
    - advertisers: A dictionary of advertisers for the given platform (e.g., Awin or Admitad)
    - platform_key: The key indicating the platform (e.g., "awin", "admitad")
    - percentage: The percentage of time this user should be selected for these domains
    """
    if not advertisers:
        logger.info(f"No advertisers for {platform_key}. Skipping {user_id}.")
        return

    for domain, affiliate_id in advertisers.items():
        if affiliate_id:
            add_to_domain_table(domain, user_id, affiliate_id, percentage)


def add_user_to_domain_percentage_table(user_id, user_data, percentage):
    """
    Adds a user to the domain percentage table based on their affiliate configurations.

    Parameters:
    - user_id: ID of the user (e.g., "user", "HectorziN")
    - user_data: Configuration data of the user (structured as amazon, awin, admitad, aliexpress)
    - percentage: Percentage of time this user should be selected for each domain
    """
    logger.debug(f"Adding {user_id} with percentage {percentage}")

    add_to_domain_table(
        "aliexpress.com",
        user_id,
        user_data.get("aliexpress", {}).get("app_key", None),
        percentage,
    )
    add_affiliate_stores_domains(
        user_id,
        user_data.get("amazon", {}).get("advertisers", {}),
        "amazon",
        percentage,
    )
    add_affiliate_stores_domains(
        user_id, user_data.get("awin", {}).get("advertisers", {}), "awin", percentage
    )
    add_affiliate_stores_domains(
        user_id,
        user_data.get("admitad", {}).get("advertisers", {}),
        "admitad",
        percentage,
    )


def adjust_domain_affiliate_percentages(domain, creator_percentage):
    """
    Adjusts the percentages of users in a given domain within domain_percentage_table, ensuring they sum to 100%.

    Parameters:
    - domain: The domain (e.g., "amazon", "aliexpress") to adjust in domain_percentage_table.
    - creator_percentage: The percentage of total influence given to creators by the user.
    """
    logger.debug(f"Adjusting percentages for domain: {domain}")
    domain_data = domain_percentage_table.get(domain, [])
    user_entry = None
    creator_entries = []

    for entry in domain_data:
        if entry["user"] == "main":
            user_entry = entry
        else:
            creator_entries.append(entry)

    user_percentage = 100 - creator_percentage
    if user_entry:
        user_entry["percentage"] = user_percentage
        logger.debug(f"Set user percentage for domain {domain} to {user_percentage}")
    else:
        user_percentage = 0
        creator_percentage = 100

    total_creator_percentage = sum(entry["percentage"] for entry in creator_entries)
    if total_creator_percentage > 0:
        for creator_entry in creator_entries:
            weighted_creator_percentage = creator_entry["percentage"] * (
                creator_percentage / total_creator_percentage
            )
            creator_entry["percentage"] = weighted_creator_percentage
            logger.debug(
                f"Set creator percentage for domain {domain} to {weighted_creator_percentage}"
            )
    else:
        user_entry["percentage"] = 100
    index_offset = 0
    if user_entry:
        domain_data[0] = user_entry
        index_offset = 1
    for i in range(len(creator_entries)):
        domain_data[i + index_offset] = creator_entries[i]

    # for entry in domain_data:
    #     entry["percentage"] = (entry["percentage"] / total_percentage) * 100
    #     logger.debug(
    #         f"Normalized percentage for user {entry['user']} to {entry['percentage']}"
    #     )
    log_message = f"Adjusted percentages for domain {domain}: "
    log_entries = []

    # log percentages in a unique line for easy reding
    for entry in domain_data:
        log_entries.append(f"{entry['user']}:{entry['percentage']:.2f}%")
    log_message += " ".join(log_entries)
    logger.info(log_message)


def should_reload_configuration():
    global last_load_time
    if last_load_time is None:
        return True  # Cargar si nunca se ha cargado
    return datetime.now() - last_load_time >= timedelta(seconds=60)


def load_configuration():
    global last_load_time
    if not should_reload_configuration():
        return
    logger.info("Loading configuration")
    domain_percentage_table.clear()
    all_users_configurations.clear()
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config_file_data = yaml.safe_load(file)

    with open(CREATORS_CONFIG_PATH, "r", encoding="utf-8") as file:
        creators_file_data = yaml.safe_load(file)

    # Telegram settings
    config_data["BOT_TOKEN"] = config_file_data.get("telegram", {}).get(
        "bot_token", None
    )  # None if not set
    config_data["DELETE_MESSAGES"] = config_file_data.get("telegram", {}).get(
        "delete_messages", True
    )
    config_data["EXCLUDED_USERS"] = config_file_data.get("telegram", {}).get(
        "excluded_users", []
    )

    # Messages
    config_data["MSG_AFFILIATE_LINK_MODIFIED"] = config_file_data.get(
        "messages", {}
    ).get(
        "affiliate_link_modified",
        "Here is the modified link with our affiliate program:",
    )
    config_data["MSG_REPLY_PROVIDED_BY_USER"] = config_file_data.get(
        "messages", {}
    ).get("reply_provided_by_user", "Reply provided by")

    # feed the authors
    config_data["CREATOR_PERCENTAGE"] = config_file_data.get(
        "affiliate_settings", {}
    ).get("creator_affiliate_percentage", 10)

    # Logging Level
    config_data["LOG_LEVEL"] = config_file_data.get("log_level", "INFO")

    # Load user configurations
    all_users_configurations["main"] = load_user_configuration(
        "main", 100 - config_data["CREATOR_PERCENTAGE"], config_file_data
    )
    for creator in creators_file_data.get("users", []):
        creator_id = creator.get("id")
        creator_percentage = creator.get("percentage", 0)
        creator_url = creator.get(
            "url"
        )  # Assuming you have a field 'url' for each creator
        if creator_url:
            user_data = load_user_configuration_from_url(
                creator_id, creator_percentage, creator_url
            )
            if user_data:
                all_users_configurations[creator_id] = user_data

    # Add users to the domain percentage table
    for user_id, user_data in all_users_configurations.items():
        user_percentage = user_data.get("percentage", 0)
        add_user_to_domain_percentage_table(user_id, user_data, user_percentage)

    # Adjust percentages for each domain
    for domain in domain_percentage_table:
        adjust_domain_affiliate_percentages(domain, config_data["CREATOR_PERCENTAGE"])
    last_load_time = datetime.now()
