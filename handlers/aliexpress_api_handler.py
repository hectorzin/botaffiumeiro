from handlers.base_handler import BaseHandler
from telegram import Message
import re
import time
import hmac
import hashlib
import requests
from handlers.aliexpress_handler import (
    ALIEXPRESS_URL_PATTERN,
    ALIEXPRESS_SHORT_URL_PATTERN,
)
from config import (
    ALIEXPRESS_APP_KEY,
    ALIEXPRESS_APP_SECRET,
    ALIEXPRESS_TRACKING_ID,
    ALIEXPRESS_DISCOUNT_CODES,
    ALIEXPRESS_DISCOUNT_CODES,
)

# API endpoint for generating affiliate links
ALIEXPRESS_API_URL = "https://api-sg.aliexpress.com/sync"


class AliexpressAPIHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    # Function to generate HMAC-SHA256 signature
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

        params = {
            "app_key": ALIEXPRESS_APP_KEY,
            "timestamp": timestamp,
            "sign_method": "hmac-sha256",
            "promotion_link_type": "0",
            "source_values": source_url,
            "tracking_id": ALIEXPRESS_TRACKING_ID,
            "method": "aliexpress.affiliate.link.generate",
        }

        # Generate the signature
        signature = self._generate_signature(ALIEXPRESS_APP_SECRET, params)
        params["sign"] = signature

        # Make the request to the Aliexpress API
        try:
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

    async def handle_links(self, message: Message) -> bool:
        """Handles AliExpress links and converts them using the Aliexpress API."""
        if not ALIEXPRESS_APP_KEY:
            self.logger.info("AliExpress API key is not set. Skipping processing.")
            return False

        self.logger.info(
            f"{message.message_id}: Handling AliExpress links in the message..."
        )

        new_text = message.text
        aliexpress_links = re.findall(ALIEXPRESS_URL_PATTERN, new_text)
        aliexpress_short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, new_text)

        all_aliexpress_links = aliexpress_links + aliexpress_short_links

        if not all_aliexpress_links:
            self.logger.info(
                f"{message.message_id}: No AliExpress links found in the message."
            )
            return False

        self.logger.info(
            f"{message.message_id}: Found {len(all_aliexpress_links)} AliExpress links. Processing..."
        )
        for link in all_aliexpress_links:
            if "s.click.aliexpress" in link:
                link = self._expand_shortened_url_from_list(
                    link, ["s.click.aliexpress.com"]
                )
                self.logger.info(
                    f"{message.message_id}: Expanded short AliExpress link: {link}"
                )

            affiliate_link = await self._convert_to_aliexpress_affiliate(link)
            if affiliate_link:
                new_text = new_text.replace(link, affiliate_link)

        new_text += f"\n\n{ALIEXPRESS_DISCOUNT_CODES}"
        self.logger.debug(f"{message.message_id}: Appended AliExpress discount codes.")

        if new_text != message.text:
            self._process_message(message, new_text)
            return True

        self.logger.info(f"{message.message_id}: No modifications made to the message.")
        return False
