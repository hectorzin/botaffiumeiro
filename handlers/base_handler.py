from abc import ABC, abstractmethod
import logging
import re
from typing import Tuple
from urllib.parse import parse_qs, urlencode, urlparse

from config import config_data
from publicsuffix2 import get_sld
from telegram import Message

# Known short URL domains for expansion
PATTERN_URL_QUERY = r"?[^\s]+"
PATTERN_AFFILIATE_URL_QUERY = r"/[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=%]+"


class BaseHandler(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.selected_users = {}

    def _unpack_context(
        self, context
    ) -> Tuple[
        Message,
        str,
        dict,
    ]:
        return (
            context["message"],
            context["modified_message"],
            context["selected_users"],
        )

    def _generate_affiliate_url(
        self,
        original_url: str,
        format_template: str,
        affiliate_tag: str,
        affiliate_id: str,
        advertiser_id: str = "",
    ) -> str:
        """Converts a product URL into an affiliate link based on the provided format template.

        Args:
        ----
            original_url (str): The original product URL.
            format_template (str): The template for the affiliate URL, e.g., '{domain}/{path_before_query}?{affiliate_tag}={affiliate_id}'.
            affiliate_tag (str): The query parameter for the affiliate ID (e.g., 'tag', 'aff_id').
            affiliate_id (str): The affiliate ID for the platform.
            advertiser_id (str): The advertiser ID for the platform (optional).

        Returns:
        -------
            str: The URL with the affiliate tag and advertiser ID added according to the template.

        """
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

    async def _process_message(self, message, new_text: str):
        """Send a polite affiliate message, either by deleting the original message or replying to it.

        Args:
        ----
            message (telegram.Message): The message to modify.
            new_text (str): The modified text with affiliate links.

        """
        # Get user information
        user_first_name = message.from_user.first_name
        user_username = message.from_user.username
        polite_message = f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"

        if config_data["DELETE_MESSAGES"]:
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
                f"{message.message_id}: Original message deleted and sent modified message with affiliate links."
            )
        else:
            # Reply to the original message
            reply_to_message_id = message.message_id
            await message.chat.send_message(
                text=polite_message, reply_to_message_id=reply_to_message_id
            )
            self.logger.info(
                f"{message.message_id}: Replied to message with affiliate links."
            )

    def _build_affiliate_url_pattern(self, advertiser_key):
        """Builds a URL pattern for a given affiliate platform (e.g., Admitad, Awin) by gathering all the advertiser domains.

        Parameters
        ----------
        - advertiser_key: The key in selected_users that holds advertisers (e.g., 'admitad', 'awin').

        Returns
        -------
        - A regex pattern string that matches any of the advertiser domains.

        """
        affiliate_domains = set()

        # Loop through selected users to gather all advertiser domains for the given platform
        advertisers = {}

        # extract all domains handled by the current adversiter_key
        for domain, user_data in self.selected_users.items():
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
        """Extracts store URLs directly from the message text or from URLs embedded in query parameters.

        Parameters
        ----------
        - message_text: The text of the message.
        - url_pattern: The regex pattern to match store URLs.

        Returns
        -------
        - A list of tuples (original_url, extracted_url, domain) matching the store pattern.

        """
        extracted_urls = []

        def _extract_and_append(original, extracted):
            """Helper function to parse and append URL and domain."""
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
                for key, values in query_params.items():
                    for value in values:
                        if re.match(url_pattern, value):
                            _extract_and_append(url, value)

        return extracted_urls

    async def _process_store_affiliate_links(
        self,
        context,
        affiliate_platform: str,
        format_template: str,
        affiliate_tag: str,
    ) -> bool:
        """Generic method to handle affiliate links for different platforms."""
        message, text, self.selected_users = self._unpack_context(context)
        url_pattern = self._build_affiliate_url_pattern(affiliate_platform)

        if not url_pattern:
            self.logger.info(f"{message.message_id}: No affiliate list")
            return False

        store_links = self._extract_store_urls(text, url_pattern)

        requires_publisher = "{affiliate_id}" in format_template
        requires_advertiser = "{advertiser_id}" in format_template
        new_text = text
        if store_links:
            self.logger.info(
                f"{message.message_id}: Found {len(store_links)} store links. Processing..."
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
                        f"{message.message_id}: No publisher or adversiter ID defined for this handler. Skipping processing."
                    )
                    continue
                user = self.selected_users.get(store_domain, {}).get("user", {})
                self.logger.info(f"User choosen: {user}")

                affiliate_link = self._generate_affiliate_url(
                    link,
                    format_template=format_template,
                    affiliate_tag=affiliate_tag,
                    affiliate_id=publisher_id,
                    advertiser_id=advertiser_id,
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
                        f"{message.message_id}: Appended AliExpress discount codes."
                    )

        if new_text != text:
            await self._process_message(message, new_text)
            return True

        self.logger.info(f"{message.message_id}: No links found in the message.")
        return False

    @abstractmethod
    async def handle_links(self, message: Message) -> bool:
        pass
