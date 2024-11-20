"""Module to handle bot configuration and affiliate link processing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
from typing import Any

import requests
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Class to manage bot configuration and affiliate link processing."""

    CONFIG_PATH = Path("data/config.yaml")
    CREATORS_CONFIG_PATH = Path("creators_affiliates.yaml")
    TIMEOUT = 10

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        # Telegram settings
        self.bot_token: str = ""
        self.delete_messages: bool = True
        self.excluded_users: list[str] = []
        self.discount_keywords: list[str] = []

        # Messages
        self.msg_affiliate_link_modified: str = ""
        self.msg_reply_provided_by_user: str = ""

        # Affiliate settings
        self.creator_percentage: int = 10

        # Logging
        self.log_level: str = "INFO"

        # Internal data
        self.domain_percentage_table: dict[str, list[dict[str, Any]]] = {}
        self.all_users_configurations: dict[str, dict] = {}
        self.last_load_time: datetime | None = None

    def _load_user_configuration(
        self, user: str, creator_percentage: int, user_data: dict
    ) -> dict:
        """Load user-specific configuration for affiliate programs and settings.

        Args:
        ----
            user (str): User ID.
            creator_percentage (int): Percentage of creator's influence.
            user_data (dict): User-specific configuration data.

        Returns:
        -------
            dict: Processed user configuration.

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
            "tradedoubler": {
                "publisher_id": user_data.get("tradedoubler", {}).get(
                    "publisher_id", None
                ),
                "advertisers": user_data.get("tradedoubler", {}).get("advertisers", {}),
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

    def _load_user_configuration_from_url(
        self, user_id: str, percentage: int, url: str
    ) -> dict | None:
        """Load user-specific configuration from a URL.

        Args:
        ----
            user_id (str): ID of the user.
            percentage (int): User's affiliate percentage.
            url (str): URL to fetch the user's configuration YAML file.

        Returns:
        -------
            dict | None: User configuration data or None if an error occurs.

        """
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            user_data = yaml.safe_load(response.text)
            return self._load_user_configuration(
                user_id, percentage, user_data.get("configuration", {})
            )
        except requests.RequestException:
            logger.exception("Error loading configuration for %s from %s", user_id, url)
            return None

    def _add_to_domain_table(
        self, domain: str, user_id: str, affiliate_id: str | None, percentage: int
    ) -> None:
        """Add a user to the domain percentage table.

        Args:
        ----
            domain (str): Domain name (e.g., "amazon").
            user_id (str): User ID (e.g., "user", "HectorziN").
            affiliate_id (str | None): Affiliate ID for the domain.
            percentage (int): User's percentage share for the domain.

        """
        if affiliate_id:
            if domain not in self.domain_percentage_table:
                self.domain_percentage_table[domain] = []

            if not any(
                entry["user"] == user_id
                for entry in self.domain_percentage_table[domain]
            ):
                self.domain_percentage_table[domain].append(
                    {"user": user_id, "percentage": percentage}
                )

    def _add_affiliate_stores_domains(
        self,
        user_id: str,
        advertisers: dict[str, str],
        platform_key: str,
        percentage: int,
    ) -> None:
        """Process multiple domains for affiliate platforms.

        Args:
        ----
            user_id (str): User ID.
            advertisers (dict[str, str]): Advertiser data.
            platform_key (str): Platform key (e.g., "awin").
            percentage (int): User's percentage share.

        """
        if not advertisers:
            logger.info("No advertisers for %s. Skipping %s.", platform_key, user_id)
            return

        for domain, affiliate_id in advertisers.items():
            if affiliate_id:
                self._add_to_domain_table(domain, user_id, affiliate_id, percentage)

    def _add_user_to_domain_percentage_table(
        self, user_id: str, user_data: dict, percentage: int
    ) -> None:
        """Add a user to the domain percentage table based on their affiliate configurations.

        Args:
        ----
            user_id (str): User ID (e.g., "HectorziN").
            user_data (dict): User-specific configuration data.
            percentage (int): Percentage of user influence.

        """
        logger.debug("Adding %s with percentage %s", user_id, percentage)

        if user_data.get("aliexpress", {}).get("discount_codes", None):
            self._add_to_domain_table(
                "aliexpress.com",
                user_id,
                "Discount",
                percentage,
            )
        self._add_to_domain_table(
            "aliexpress.com",
            user_id,
            user_data.get("aliexpress", {}).get("app_key", None),
            percentage,
        )
        self._add_affiliate_stores_domains(
            user_id,
            user_data.get("amazon", {}).get("advertisers", {}),
            "amazon",
            percentage,
        )
        self._add_affiliate_stores_domains(
            user_id,
            user_data.get("awin", {}).get("advertisers", {}),
            "awin",
            percentage,
        )
        self._add_affiliate_stores_domains(
            user_id,
            user_data.get("admitad", {}).get("advertisers", {}),
            "admitad",
            percentage,
        )
        self._add_affiliate_stores_domains(
            user_id,
            user_data.get("tradedoubler", {}).get("advertisers", {}),
            "tradedoubler",
            percentage,
        )

    def _adjust_domain_affiliate_percentages(
        self, domain: str, creator_percentage: int
    ) -> None:
        """Adjust percentages in domain_percentage_table to ensure they sum to 100%.

        Args:
        ----
            domain (str): Domain name (e.g., "amazon").
            creator_percentage (int): Percentage allocated to creators.

        """
        logger.debug("Adjusting percentages for domain: %s", domain)
        domain_data = self.domain_percentage_table.get(domain, [])
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
            logger.debug(
                "Set user percentage for domain %s to %s", domain, user_percentage
            )
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
                    "Set creator percentage for domain %s to %s",
                    domain,
                    weighted_creator_percentage,
                )
        elif user_entry:
            user_entry["percentage"] = 100
        index_offset = 0
        if user_entry:
            domain_data[0] = user_entry
            index_offset = 1
        for i in range(len(creator_entries)):
            domain_data[i + index_offset] = creator_entries[i]

        log_message = f"Adjusted percentages for domain {domain}: "

        # log percentages in a unique line for easy reding
        log_entries = [
            f"{entry['user']}:{entry['percentage']:.2f}%" for entry in domain_data
        ]

        log_message += " ".join(log_entries)
        logger.info(log_message)

    def _should_reload_configuration(self) -> bool:
        """Check if the configuration should be reloaded.

        Returns
        -------
            bool: True if the configuration should be reloaded, False otherwise.

        """
        if self.last_load_time is None:
            return True  # Cargar si nunca se ha cargado
        return datetime.now(timezone.utc) - self.last_load_time >= timedelta(seconds=60)

    def load_configuration(self) -> None:
        """Load and process the configuration files."""
        if not self._should_reload_configuration():
            return
        logger.info("Loading configuration")
        self.domain_percentage_table.clear()
        self.all_users_configurations.clear()
        with self.CONFIG_PATH.open(encoding="utf-8") as file:
            config_file_data = yaml.safe_load(file)

        with self.CREATORS_CONFIG_PATH.open(encoding="utf-8") as file:
            creators_file_data = yaml.safe_load(file)

        # Telegram settings
        telegram_config = config_file_data.get("telegram", {})
        self.bot_token = telegram_config.get("bot_token", "")
        self.delete_messages = telegram_config.get("delete_messages", True)
        self.excluded_users = telegram_config.get("excluded_users", [])
        self.discount_keywords = telegram_config.get("discount_keywords", [])

        # Messages
        messages_config = config_file_data.get("messages", {})
        self.msg_affiliate_link_modified = messages_config.get(
            "affiliate_link_modified",
            "Here is the modified link with our affiliate program:",
        )
        self.msg_reply_provided_by_user = messages_config.get(
            "reply_provided_by_user", "Reply provided by"
        )

        # Affiliate settings
        affiliate_settings = config_file_data.get("affiliate_settings", {})
        self.creator_percentage = affiliate_settings.get(
            "creator_affiliate_percentage", 10
        )

        # Logging
        self.log_level = config_file_data.get("log_level", "INFO")

        # Load user configurations
        self.all_users_configurations["main"] = self._load_user_configuration(
            "main", 100 - self.creator_percentage, config_file_data
        )
        for creator in creators_file_data.get("users", []):
            creator_id = creator.get("id")
            creator_percentage = creator.get("percentage", 0)
            creator_url = creator.get(
                "url"
            )  # Assuming you have a field 'url' for each creator
            if creator_url:
                user_data = self._load_user_configuration_from_url(
                    creator_id, creator_percentage, creator_url
                )
                if user_data:
                    self.all_users_configurations[creator_id] = user_data

        # Add users to the domain percentage table
        for user_id, user_data in self.all_users_configurations.items():
            user_percentage = user_data.get("percentage", 0)
            self._add_user_to_domain_percentage_table(
                user_id, user_data, user_percentage
            )

        # Adjust percentages for each domain
        for domain in self.domain_percentage_table:
            self._adjust_domain_affiliate_percentages(domain, self.creator_percentage)
        self.last_load_time = datetime.now(timezone.utc)
