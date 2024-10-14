from handlers.base_handler import BaseHandler,ALIEXPRESS_SHORT_URL_PATTERN
from telegram import Message
import logging
import httpx
import re

from config import (
    ALIEXPRESS_DISCOUNT_CODES,
    ALIEXPRESS_APP_KEY,
    AWIN_ADVERTISERS,
    ADMITAD_ADVERTISERS,
)

ALIEXPRESS_URL_PATTERN = r"(https?://(?:[a-z]{2,3}\.)?aliexpress\.[a-z]{2,3}(?:\.[a-z]{2})?/(?:[\w\d\-\./?=&%]+))"

class AliexpressAPIHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        # Check if discount codes and message are not empty before proceeding
        if not ALIEXPRESS_DISCOUNT_CODES:
            self.logger.info(
                f"{message.message_id}: Discount message or codes are empty. Skipping reply."
            )
            return True  # Exit the function if both variables are empty

        """Handles both long and short AliExpress links in the message."""
        self.logger.info(f"{message.message_id}: Handling AliExpress links in the message...")

        aliexpress_links = re.findall(ALIEXPRESS_URL_PATTERN, message.text)
        aliexpress_short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)
        all_aliexpress_links = aliexpress_links + aliexpress_short_links

        if all_aliexpress_links:
            self.logger.info(
                f"{message.message_id}: Found {len(all_aliexpress_links)} AliExpress links. Processing..."
            )
            if (
                "aliexpress.com" in AWIN_ADVERTISERS
                or "aliexpress.com" in ADMITAD_ADVERTISERS
                or ALIEXPRESS_APP_KEY != ""
            ):
                self.logger.info(
                    f"{message.message_id}: AliExpress links found in advertisers. Skipping processing."
                )
                return False

            self.logger.info(
                f"{message.message_id}: No advertiser found for AliExpress. Sending discount codes."
            )
            await message.chat.send_message(
                f"{ALIEXPRESS_DISCOUNT_CODES}",
                reply_to_message_id=message.message_id,
            )
            self.logger.info(
                f"{message.message_id}: Sent modified message with affiliate links."
            )
            return True

        self.logger.info(f"{message.message_id}: No AliExpress links found in the message.")
        return False
