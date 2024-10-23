import logging
import yaml

# Rutas a los archivos de configuración
CONFIG_PATH = "data/config.yaml"
CREATORS_CONFIG_PATH = "creators_affiliates.yaml"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar configuración del usuario principal (global)
with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config_data = yaml.safe_load(file)

# Cargar configuración de los creadores
with open(CREATORS_CONFIG_PATH, "r", encoding="utf-8") as file:
    creators_data = yaml.safe_load(file)

# Telegram settings
BOT_TOKEN = config_data.get("telegram", {}).get("bot_token", None)  # None if not set
DELETE_MESSAGES = config_data.get("telegram", {}).get("delete_messages", True)
EXCLUDED_USERS = config_data.get("telegram", {}).get("excluded_users", [])

# Messages
MSG_AFFILIATE_LINK_MODIFIED = config_data.get("messages", {}).get(
    "affiliate_link_modified", "Here is the modified link with our affiliate program:"
)
MSG_REPLY_PROVIDED_BY_USER = config_data.get("messages", {}).get(
    "reply_provided_by_user", "Reply provided by"
)

# feed the authors
CREATOR_PERCENTAGE = config_data.get("affiliate_settings", {}).get(
    "creator_affiliate_percentage", 10
)

# Logging Level
LOG_LEVEL = config_data.get("log_level", "INFO")

domain_percentage_table = {}
all_users_configurations = {}


def load_user_configuration(user,creator_percentage,user_data):
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
        user_id, user_data.get("amazon", {}).get("advertisers", {}), "amazon", percentage
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
        user_percentage=0
        creator_percentage=100

    total_creator_percentage = sum(entry["percentage"] for entry in creator_entries)
    if total_creator_percentage>0:
        for creator_entry in creator_entries:
            weighted_creator_percentage = creator_entry["percentage"] * (
                creator_percentage / total_creator_percentage
            )
            creator_entry["percentage"] = weighted_creator_percentage
            logger.debug(
                f"Set creator percentage for domain {domain} to {weighted_creator_percentage}"
            )
    index_offset=0
    if  user_entry:
        domain_data[0]=user_entry
        index_offset=1
    for i in range(len(creator_entries)):
        domain_data[i +index_offset] = creator_entries[i]

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

# Load user configurations
all_users_configurations["main"] = load_user_configuration("main",100 - CREATOR_PERCENTAGE,
    config_data
)
for creator in creators_data.get("users", []):
    creator_id = creator.get("id")
    creator_percentage = creator.get("percentage", 0)
    all_users_configurations[creator_id] = load_user_configuration(creator_id,creator_percentage,
        creator.get("configuration", {})
    )

# Add users to the domain percentage table
for user_id, user_data in all_users_configurations.items():
    user_percentage = user_data.get("percentage", 0)
    add_user_to_domain_percentage_table(user_id, user_data, user_percentage)

# Adjust percentages for each domain
for domain in domain_percentage_table:
    adjust_domain_affiliate_percentages(domain, CREATOR_PERCENTAGE)
