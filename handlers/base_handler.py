import logging
import requests
import re

from abc import ABC, abstractmethod
from telegram import Message
from urllib.parse import ParseResult,urlparse,parse_qs,urlencode
from config import (
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
    DELETE_MESSAGES,
    ALIEXPRESS_DISCOUNT_CODES,
)

ALIEXPRESS_SHORT_URL_PATTERN = r"https?://s\.click\.aliexpress\.com/e/[\w\d_]+"

class BaseHandler(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _expand_shortened_url(self, url: ParseResult):
        """Expands shortened URLs by following redirects."""
        self.logger.info(f"Try expanding shortened URL: {url}")
        try:
            response = requests.get(url, allow_redirects=True)
            self.logger.debug(f"Expanded URL {url} to full link: {response.url}")
            return response.url
        except requests.RequestException as e:
            self.logger.error(f"Error expanding shortened URL {url}: {e}")
            return url

    def _expand_shortened_url_from_list(self, url: str, domains: list[str]) -> str:
        """
        Expands shortened URLs by following redirects if the domain matches one of the given domains.
        
        Args:
            url (str): The shortened URL to expand.
            domains (list): A list of domains for which the URL should be expanded.

        Returns:
            str: The expanded URL if the domain matches, or the original URL otherwise.
        """
        parsed_url = urlparse(url)
        
        # Check if the domain is in the list of provided domains
        if any(domain in parsed_url.netloc for domain in domains):
            # Call the superclass method to expand the URL
            url = self._expand_shortened_url(parsed_url)
        
        return url

    def _expand_short_links_from_message(self, message_text: str, url_pattern: str, short_domains: list) -> str:
        """
        Expands shortened URLs in a message using a specified pattern and list of short domains.

        Args:
            message_text (str): The text of the message to search for short links.
            url_pattern (str): The regular expression pattern to search for short links.
            short_domains (list): A list of domains to check for short links.

        Returns:
            str: The message text with expanded URLs.
        """
        new_text = message_text
        short_links = re.findall(url_pattern, message_text)

        if short_links:
            self.logger.info(f"Found {len(short_links)} short links. Processing...")

            for short_link in short_links:
                full_link = self._expand_shortened_url_from_list(short_link, short_domains)
                new_text = new_text.replace(short_link, full_link)

        return new_text

    def _expand_aliexpress_links_from_message(self, message_text: str) -> str:
        new_text = self.expand_short_links(
            message_text=message_text,
            url_pattern=ALIEXPRESS_SHORT_URL_PATTERN,
            short_domains=["s.click.aliexpress.com"]
        )
        return new_text

    def _generate_affiliate_url(self, original_url: str, format_template: str, affiliate_tag: str, affiliate_id: str) -> str:
        """
        Converts a product URL into an affiliate link based on the provided format template.

        Args:
            original_url (str): The original product URL.
            format_template (str): The template for the affiliate URL, e.g., '{domain}/{path_before_query}?{affiliate_tag}={affiliate_id}'.
            affiliate_tag (str): The query parameter for the affiliate ID (e.g., 'tag', 'aff_id').
            affiliate_id (str): The affiliate ID for the platform.
            additional_params (dict): Additional query parameters to be included in the final URL.

        Returns:
            str: The URL with the affiliate tag added according to the template.
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


        # Build the new query string
        new_query = urlencode(query_params, doseq=True)

        # Format the output using the provided format_template
        affiliate_url = format_template.format(
            domain=domain,
            path_before_query=path_before_query,
            full_url=full_url,
            affiliate_tag=affiliate_tag,
            affiliate_id=affiliate_id
        )

        # Check if query params (affiliate tag or additional) are missing from the format_template
        if  '{affiliate_id}' not in format_template:
            if '?' not in affiliate_url:
                affiliate_url += f"?{new_query}"
            else:
                affiliate_url += f"&{new_query}"

        return affiliate_url

    async def _process_message(self, message, new_text: str):
        """
        Send a polite affiliate message, either by deleting the original message or replying to it.

        Args:
            message (telegram.Message): The message to modify.
            new_text (str): The modified text with affiliate links.
        """
        # Get user information
        user_first_name = message.from_user.first_name
        user_username = message.from_user.username
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"

        if DELETE_MESSAGES:
            # Delete original message and send a new one
            reply_to_message_id = (
                message.reply_to_message.message_id if message.reply_to_message else None
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

    def _process_store_affiliate_links(
        self,
        message,
        publisher_id: str,
        advertisers: dict,
        url_pattern: str,
        affiliate_pattern: str,
        format_template: str,
        affiliate_tag: str,
    ) -> bool:
        """Generic method to handle affiliate links for different platforms."""

        if not publisher_id:
            self.logger.info(f"{message.message_id}: Affiliate ID is not set. Skipping processing.")
            return False

        new_text = self._expand_aliexpress_links_from_message(message.text)

        # Find regular store links and affiliate links
        store_links = re.findall(url_pattern, new_text)
        affiliate_links = re.findall(affiliate_pattern, new_text)

        if affiliate_links:
            self.logger.info(f"{message.message_id}: Found {len(affiliate_links)} affiliate links. Processing...")
            for link in affiliate_links:
                if len(store_links) == 0:
                    return False
                modified_link = self.generate_affiliate_url(
                    link,
                    format_template="{full_url}",
                    affiliate_tag=affiliate_tag,
                    affiliate_id=publisher_id,
                )
                new_text = new_text.replace(link, modified_link)

        elif store_links:
            self.logger.info(f"{message.message_id}: Found {len(store_links)} store links. Processing...")
            for link, store_domain in store_links:
                advertiser_id = advertisers.get(store_domain)
                if not advertiser_id:
                    continue

                affiliate_link = self.generate_affiliate_url(
                    link,
                    format_template=format_template.format(advertiser_id=advertiser_id),
                    affiliate_tag=affiliate_tag,
                    affiliate_id=publisher_id,
                )
                new_text = new_text.replace(link, affiliate_link)

                if "aliexpress" in store_domain and ALIEXPRESS_DISCOUNT_CODES:
                    new_text += f"\n\n{ALIEXPRESS_DISCOUNT_CODES}"
                    self.logger.debug(f"{message.message_id}: Appended AliExpress discount codes.")

        if new_text != message.text:
            self._process_message(message, new_text)
            return True

        self.logger.info(f"{message.message_id}: No links found in the message.")
        return False


    @abstractmethod
    async def handle_links(self, message: Message) -> bool:
        pass
