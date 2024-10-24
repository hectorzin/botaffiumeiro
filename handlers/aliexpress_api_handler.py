import hmac
import hashlib
import re
import requests
import time

from handlers.base_handler import BaseHandler
from handlers.aliexpress_handler import ALIEXPRESS_PATTERN

# API endpoint for generating affiliate links
ALIEXPRESS_API_URL = "https://api-sg.aliexpress.com/sync"


class AliexpressAPIHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _generate_signature(self, secret, params):
        """Generates HMAC-SHA256 signature."""
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
        self.logger.debug(f"Generated signature: {signature}")
        return signature

    async def _convert_to_aliexpress_affiliate(self, source_url):
        """Converts a regular AliExpress link into an affiliate link using the Aliexpress API."""
        self.logger.info(f"Converting AliExpress link to affiliate link: {source_url}")
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
            self.logger.info(f"User choosen: {user}")
            response = requests.get(ALIEXPRESS_API_URL, params=params)
            self.logger.info(f"API request sent. Status code: {response.status_code}")
            data = response.json()

            resp_result = data.get(
                "aliexpress_affiliate_link_generate_response", {}
            ).get("resp_result", {})
            if resp_result.get("resp_code") == 200:
                result = resp_result.get("result", {})
                promotion_links = result.get("promotion_links", {}).get(
                    "promotion_link", []
                )
                if promotion_links:
                    promotion_link = promotion_links[0].get("promotion_link")
                    self.logger.info(
                        f"Successfully retrieved affiliate link: {promotion_link}"
                    )
                    return promotion_link
                else:
                    self.logger.warning("No promotion links found in the response.")
            else:
                self.logger.error(
                    f"API error. Code: {resp_result.get('resp_code')}, Message: {resp_result.get('resp_msg')}"
                )
        except Exception as e:
            self.logger.error(f"Error converting link to affiliate: {e}")

        return None

    async def handle_links(self, context) -> bool:
        """Handles AliExpress links and converts them using the Aliexpress API."""

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
            f"{message.message_id}: Handling AliExpress links in the message..."
        )

        new_text = modified_text

        # Find AliExpress links in the message text
        aliexpress_links = re.findall(ALIEXPRESS_PATTERN, new_text)

        if not aliexpress_links:
            self.logger.info(
                f"{message.message_id}: No AliExpress links found in the message."
            )
            return False

        self.logger.info(
            f"{message.message_id}: Found {len(aliexpress_links)} AliExpress links. Processing..."
        )

        # Convert the links to affiliate links
        for link in aliexpress_links:
            affiliate_link = await self._convert_to_aliexpress_affiliate(link)
            if affiliate_link:
                new_text = new_text.replace(link, affiliate_link)

        # Add discount codes if they are configured
        if discount_codes:
            new_text += f"\n\n{discount_codes}"
            self.logger.debug(
                f"{message.message_id}: Appended AliExpress discount codes."
            )

        # Process the message if modifications were made
        if new_text != modified_text:
            await self._process_message(message, new_text)
            return True

        self.logger.info(f"{message.message_id}: No modifications made to the message.")
        return False
