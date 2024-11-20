"""Handler for processing AliExpress affiliate links using the AliExpress API."""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, unquote, urlparse, urlunparse

from config import ConfigurationManager
import httpx
from requests.exceptions import RequestException  # type: ignore[import-untyped]

from handlers.aliexpress_handler import ALIEXPRESS_PATTERN
from handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from config import ConfigurationManager

# API endpoint for generating affiliate links
ALIEXPRESS_API_URL = "https://api-sg.aliexpress.com/sync"
SUCCESS_CODE = 200


class AliexpressAPIHandler(BaseHandler):
    """Handler for processing AliExpress links and generating affiliate links using the AliExpress API."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialize the AliexpressAPIHandler.

        Args:
        ----
            config_manager (ConfigurationManager): The configuration manager instance.

        """
        super().__init__(config_manager)

    def _generate_signature(self, secret: str, params: dict) -> str:
        """Generate HMAC-SHA256 signature for AliExpress API request.

        Args:
        ----
            secret (str): The API secret key.
            params (dict): The parameters for the API request.

        Returns:
        -------
            str: The generated signature.

        """
        self.logger.info("Generating HMAC-SHA256 signature for API request.")
        sorted_params = sorted((k, v) for k, v in params.items() if k != "sign")
        concatenated_params = "".join(f"{k}{v}" for k, v in sorted_params)
        signature = (
            hmac.new(
                secret.encode("utf-8"),
                concatenated_params.encode("utf-8"),
                hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        self.logger.debug("Generated signature: %s", signature)
        return signature

    async def _convert_to_aliexpress_affiliate(self, source_url: str) -> str | None:
        """Convert AliExpress link into affiliate link using the AliExpress API.

        Args:
        ----
            source_url (str): The original AliExpress link.

        Returns:
        -------
            str | None: The converted affiliate link or None if conversion fails.

        """
        self.logger.info("Converting AliExpress link to affiliate link: %s", source_url)
        parsed_url = urlparse(source_url)
        source_url = urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", "")
        )
        timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds

        # Get AliExpress-specific configuration from self.selected_users
        aliexpress_config = self.selected_users.get("aliexpress.com", {}).get(
            "aliexpress", {}
        )
        app_key = aliexpress_config.get("app_key")
        app_secret = aliexpress_config.get("app_secret")
        tracking_id = aliexpress_config.get("tracking_id")

        # Ensure required AliExpress configurations are present
        if not all([app_key, app_secret, tracking_id]):
            self.logger.error("Missing AliExpress API credentials in selected_users.")
            return None

        params = {
            "app_key": app_key,
            "timestamp": timestamp,
            "sign_method": "hmac-sha256",
            "promotion_link_type": "0",
            "source_values": source_url,
            "tracking_id": tracking_id,
            "method": "aliexpress.affiliate.link.generate",
        }

        # Generate the signature
        signature = self._generate_signature(app_secret, params)
        params["sign"] = signature

        # Make the request to the Aliexpress API
        try:
            user = self.selected_users.get("aliexpress.com", {}).get("user", {})
            self.logger.info("User choosen: %s", user)
            async with httpx.AsyncClient() as client:
                response = await client.get(ALIEXPRESS_API_URL, params=params)

            self.logger.info("API request sent. Status code: %s", response.status_code)
            data = response.json()

            resp_result = data.get(
                "aliexpress_affiliate_link_generate_response", {}
            ).get("resp_result", {})
            if resp_result.get("resp_code") == SUCCESS_CODE:
                result = resp_result.get("result", {})
                promotion_links = result.get("promotion_links", {}).get(
                    "promotion_link", []
                )
                if promotion_links:
                    promotion_link = promotion_links[0].get("promotion_link")
                    self.logger.info(
                        "Successfully retrieved affiliate link: %s", promotion_link
                    )
                    return promotion_link
                self.logger.warning("No promotion links found in the response.")
            else:
                self.logger.error(
                    "API error. Code: %s, Message: %s",
                    resp_result.get("resp_code"),
                    resp_result.get("resp_msg"),
                )
        except RequestException:
            self.logger.exception("Error converting link to affiliate")

        return None

    def _get_real_url(self, link: str) -> str:
        """Check for a 'redirectUrl' parameter in the given link and extracts its value if present.

        If no 'redirectUrl' is found, returns the original link.

        Args:
        ----
          link: The original URL to analyze.

        Returns:
        -------
          A string representing the resolved URL or the original link if no redirect exists.

        """
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        # Check if the 'redirectUrl' parameter exists in the query
        if "redirectUrl" in query_params:
            redirect_url = query_params["redirectUrl"][0]  # Extract the first value
            return unquote(redirect_url)  # Decode the URL
        return link  # Return the original link if no redirectUrl exists

    def _resolve_redirects(self, message_text: str) -> dict[str, str]:
        """Resolve redirected URLs from a message.

        Args:
        ----
            message_text (str): The message containing URLs.

        Returns:
        -------
            dict[str, str]: A mapping of original URLs to resolved URLs.

        """
        urls_in_message = re.findall(r"https?://[^\s]+", message_text)

        original_to_resolved = {}
        for url in urls_in_message:
            resolved_url = self._get_real_url(url)  # Resolve redirectUrl if present
            original_to_resolved[url] = resolved_url

        return original_to_resolved

    async def handle_links(self, context: dict) -> bool:
        """Handle AliExpress links and convert them to affiliate links using the API.

        Args:
        ----
            context (dict): The processing context containing message and user configurations.

        Returns:
        -------
            bool: True if any links were modified, False otherwise.

        """
        message, modified_text, self.selected_users = self._unpack_context(context)

        # Retrieve the AliExpress configuration from self.selected_users
        aliexpress_config = self.selected_users.get("aliexpress.com", {}).get(
            "aliexpress", {}
        )
        app_key = aliexpress_config.get("app_key")
        discount_codes = aliexpress_config.get("discount_codes", "")

        # Check if the AliExpress API key is set
        if not app_key:
            self.logger.info("AliExpress API key is not set. Skipping processing.")
            return False

        self.logger.info(
            "%s: Handling AliExpress links in the message...",
            message.message_id,
        )

        # Map original links (with redirectUrl) to resolved links
        original_to_resolved = self._resolve_redirects(modified_text)

        # Extract resolved URLs that match the pattern
        aliexpress_links = [
            resolved
            for original, resolved in original_to_resolved.items()
            if re.match(ALIEXPRESS_PATTERN, resolved)
        ]

        if not aliexpress_links:
            self.logger.info(
                "%s: No AliExpress links found in the message.",
                message.message_id,
            )
            return False

        self.logger.info(
            "%s: Found %d AliExpress links. Processing...",
            message.message_id,
            len(aliexpress_links),
        )

        # Map original links to their affiliate counterparts
        updated_links = {}

        # Convert the resolved links to affiliate links
        for original, resolved in original_to_resolved.items():
            if resolved in aliexpress_links:
                affiliate_link = await self._convert_to_aliexpress_affiliate(resolved)
                if affiliate_link:
                    updated_links[original] = (
                        affiliate_link  # Replace the original link
                    )

        # Replace original links with their affiliate counterparts
        new_text = modified_text
        for original, affiliate in updated_links.items():
            new_text = new_text.replace(original, affiliate)

        # Add discount codes if they are configured
        if discount_codes:
            new_text += f"\n\n{discount_codes}"
            self.logger.debug(
                "%s: Appended AliExpress discount codes.",
                message.message_id,
            )

        # Process the message if modifications were made
        if new_text != modified_text:
            await self._process_message(message, new_text)
            return True

        self.logger.info(
            "%s: No modifications made to the message.",
            message.message_id,
        )
        return False
