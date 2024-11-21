"""Base handler module for affiliate link processing."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlencode, urlparse

from publicsuffix2 import get_sld

if TYPE_CHECKING:
    from config import ConfigurationManager
    from telegram import Message

# Known short URL domains for expansion
PATTERN_URL_QUERY = r"?[^\s]+"
PATTERN_AFFILIATE_URL_QUERY = r"/[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=%]+"


class BaseHandler(ABC):
    """Base handler class for affiliate platforms."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialize the BaseHandler with configuration manager.

        Args:
        ----
            config_manager (ConfigurationManager): Configuration manager instance.

        """
        self.logger = logging.getLogger(__name__)
        self.selected_users: dict[str, dict] = {}
        self.config_manager = config_manager

    def _unpack_context(self, context: dict) -> tuple[Message, str, dict]:
        """Unpack the context dictionary into message, modified message, and selected users.

        Args:
        ----
            context (dict): Context dictionary with message data.

        Returns:
        -------
            tuple[Message, str, dict]: Unpacked message, modified message, and selected users.

        """
        return (
            context["message"],
            context["modified_message"],
            context["selected_users"],
        )

    def _generate_affiliate_url(
        self,
        original_url: str,
        format_template: str,
        affiliate_data: dict[str, str],
    ) -> str:
        """Convert a product URL into an affiliate link based on the provided format template.

        Args:
        ----
            original_url (str): The original product URL.
            format_template (str): The template for the affiliate URL, e.g., '{domain}/{path_before_query}?{affiliate_tag}={affiliate_id}'.
            affiliate_data (dict[str, str]): Data containing affiliate_tag, affiliate_id, and advertiser_id.

        Returns:
        -------
            str: The URL with the affiliate tag and advertiser ID added according to the template.

        """
        affiliate_tag = affiliate_data.get("affiliate_tag", "")
        affiliate_id = affiliate_data.get("affiliate_id", "")
        advertiser_id = affiliate_data.get("advertiser_id", "")

        # Parse the original URL
        parsed_url = urlparse(original_url)

        # Extract domain, path before the query, and full URL
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_before_query = parsed_url.path
        full_url = f"{domain}{parsed_url.path}"

        # Parse existing query parameters
        query_params = parse_qs(parsed_url.query)

        # Add or update affiliate tag
        query_params[affiliate_tag] = [affiliate_id]

        # Add or update advertiser ID if provided
        if advertiser_id != "":
            query_params["advertiser_id"] = [advertiser_id]

        # Build the new query string
        new_query = urlencode(query_params, doseq=True)

        # Substitute any placeholders {param_name} in the format_template with actual values from query_params
        for param_name, values in query_params.items():
            if f"{{{param_name}}}" in format_template:
                format_template = format_template.replace(
                    f"{{{param_name}}}", values[0]
                )

        # Format the output using the provided format_template
        affiliate_url = format_template.format(
            domain=domain,
            path_before_query=path_before_query,
            full_url=full_url,
            affiliate_tag=affiliate_tag,
            affiliate_id=affiliate_id,
            advertiser_id=advertiser_id,
        )

        # Check if query params (affiliate tag or additional) are missing from the format_template
        if "{affiliate_id}" not in format_template and affiliate_tag:
            if "?" not in affiliate_url:
                affiliate_url += f"?{new_query}"
            else:
                affiliate_url += f"&{new_query}"

        return affiliate_url

    async def _process_message(self, message: Message, new_text: str) -> None:
        """Send a polite affiliate message, either by deleting the original message or replying to it.

        Args:
        ----
            message (telegram.Message): The message to modify.
            new_text (str): The modified text with affiliate links.

        """
        # Get user information
        user_first_name = message.from_user.first_name
        user_username = message.from_user.username
        polite_message = f"{self.config_manager.msg_reply_provided_by_user} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{self.config_manager.msg_affiliate_link_modified}"

        if self.config_manager.delete_messages:
            # Delete original message and send a new one
            reply_to_message_id = (
                message.reply_to_message.message_id
                if message.reply_to_message
                else None
            )
            await message.delete()
            await message.chat.send_message(
                text=polite_message, reply_to_message_id=reply_to_message_id
            )
            self.logger.info(
                "%s: Original message deleted and sent modified message.",
                message.message_id,
            )
        else:
            # Reply to the original message
            reply_to_message_id = message.message_id
            await message.chat.send_message(
                text=polite_message, reply_to_message_id=reply_to_message_id
            )
            self.logger.info(
                "%s: Replied to message with affiliate links.", message.message_id
            )

    def _build_affiliate_url_pattern(self, advertiser_key: str) -> str | None:
        """Build a URL pattern for a given affiliate platform (e.g., Admitad, Awin) by gathering all the advertiser domains.

        Args:
        ----
          advertiser_key: The key in selected_users that holds advertisers (e.g., 'admitad', 'awin').

        Returns:
        -------
          A regex pattern string that matches any of the advertiser domains.

        """
        affiliate_domains = set()

        # Loop through selected users to gather all advertiser domains for the given platform
        advertisers = {}

        # extract all domains handled by the current adversiter_key
        for user_data in self.selected_users.values():
            advertisers_n = user_data.get(advertiser_key, {}).get("advertisers", {})
            advertisers.update(advertisers_n)

        # Add each domain, properly escaped for regex, to the affiliate_domains set
        for domain in advertisers:
            affiliate_domains.add(domain.replace(".", r"\."))

        # If no domains were found, return None
        if not affiliate_domains:
            return None

        # Join all the domains into a regex pattern
        domain_pattern = "|".join(affiliate_domains)

        # Return the complete URL pattern
        url_pattern_template = (
            r"(https?://(?:[\w\-]+\.)?({})" + PATTERN_AFFILIATE_URL_QUERY + ")"
        )

        return url_pattern_template.format(
            domain_pattern,
        )

    def _extract_store_urls(self, message_text: str, url_pattern: str) -> list:
        """Extract store URLs directly from the message text or from URLs embedded in query parameters.

        Args:
        ----
          message_text: The text of the message.
          url_pattern: The regex pattern to match store URLs.

        Returns:
        -------
        : A list of tuples (original_url, extracted_url, domain) matching the store pattern.

        """
        extracted_urls = []

        def _extract_and_append(original: str, extracted: str) -> None:
            """Parse and append URL and domain."""
            parsed_url = urlparse(extracted)
            domain = get_sld(
                parsed_url.netloc
            )  # Use get_sld to extract domain (handles cases like .co.uk)
            extracted_urls.append((original, extracted, domain))

        # Find all URLs in the message text
        urls_in_message = re.findall(r"https?://[^\s]+", message_text)

        # Process each URL found in the message
        for url in urls_in_message:
            # If the URL matches the store pattern directly, add it to the list
            if re.match(url_pattern, url):
                _extract_and_append(url, url)
            else:
                # Parse the URL to extract query parameters
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)

                # Check if any of the query parameters contains a URL matching the store pattern
                for values in query_params.values():
                    for value in values:
                        if re.match(url_pattern, value):
                            _extract_and_append(url, value)

        return extracted_urls

    async def _process_store_affiliate_links(
        self,
        context: dict,
        affiliate_platform: str,
        format_template: str,
        affiliate_tag: str | None,
    ) -> bool:
        """Handle affiliate links for different platforms."""
        message, text, self.selected_users = self._unpack_context(context)
        url_pattern = self._build_affiliate_url_pattern(affiliate_platform)

        if not url_pattern:
            self.logger.info("%s: No affiliate list", message.message_id)
            return False

        store_links = self._extract_store_urls(text, url_pattern)

        requires_publisher = "{affiliate_id}" in format_template
        requires_advertiser = "{advertiser_id}" in format_template
        new_text = text
        if store_links:
            self.logger.info(
                "%s: Found %d store links. Processing...",
                message.message_id,
                len(store_links),
            )

            for original_url, link, store_domain in store_links:
                selected_affiliate_data = self.selected_users.get(store_domain, {}).get(
                    affiliate_platform, {}
                )
                publisher_id = selected_affiliate_data.get("publisher_id", None)
                advertiser_id = selected_affiliate_data.get("advertisers", {}).get(
                    store_domain, None
                )
                if (requires_publisher and not publisher_id) or (
                    requires_advertiser and not advertiser_id
                ):
                    self.logger.info(
                        "%s: No publisher or advertiser ID defined for this handler. Skipping processing.",
                        message.message_id,
                    )
                    continue
                user = self.selected_users.get(store_domain, {}).get("user", {})
                self.logger.info("User chosen: %s", user)

                affiliate_data = {
                    "affiliate_tag": affiliate_tag,
                    "affiliate_id": publisher_id,
                    "advertiser_id": advertiser_id,
                }
                affiliate_link = self._generate_affiliate_url(
                    link,
                    format_template,
                    affiliate_data,
                )
                new_text = new_text.replace(original_url, affiliate_link)

                aliexpress_discount_codes = (
                    self.selected_users.get(store_domain, {})
                    .get("aliexpress", {})
                    .get("discount_codes", None)
                )
                if "aliexpress" in store_domain and aliexpress_discount_codes:
                    new_text += f"\n\n{aliexpress_discount_codes}"
                    self.logger.debug(
                        "%s: Appended AliExpress discount codes.", message.message_id
                    )
        if new_text != text:
            await self._process_message(message, new_text)
            return True

        self.logger.info("%s: No links found in the message.", message.message_id)
        return False

    @abstractmethod
    async def handle_links(self, message: Message) -> bool:
        """Abstract method to handle links."""
