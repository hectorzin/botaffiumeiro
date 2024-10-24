import re

from handlers.base_handler import BaseHandler, PATTERN_URL_QUERY

ALIEXPRESS_PATTERN = (
    r"(https?://(?:[a-z]{2,3}\.)?aliexpress\.[a-z]{2,3}(?:\.[a-z]{2,3})?"
    + PATTERN_URL_QUERY
    + ")"
)


class AliexpressHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def show_discount_codes(self, context) -> None:
        """Displays the AliExpress discount codes for the user."""
        # Retrieve AliExpress-specific data
        message, modified_text, self.selected_users = self._unpack_context(context)
        aliexpress_data = self.selected_users.get("aliexpress.com", {})

        # Check if there are any discount codes available for AliExpress
        aliexpress_discount_codes = aliexpress_data.get("aliexpress", {}).get("discount_codes", None)

        if not aliexpress_discount_codes:
            self.logger.info(f"{message.message_id}: Discount codes are empty. Skipping reply.")
            return

        # Send the discount codes as a response to the original message
        await message.chat.send_message(
            f"{aliexpress_discount_codes}",
            reply_to_message_id=message.message_id,
        )
        self.logger.info(f"{message.message_id}: Sent AliExpress discount codes.")
        user = aliexpress_data.get("user", {})
        self.logger.info(f"User chosen: {user}")

    async def handle_links(self, context) -> bool:
        """Handles both long and short AliExpress links in the message."""
        message, modified_text, self.selected_users = self._unpack_context(context)
        # Extraemos self.selected_users.get("aliexpress.com", {}) a una variable
        aliexpress_data = self.selected_users.get("aliexpress.com", {})

        aliexpress_links = re.findall(ALIEXPRESS_PATTERN, modified_text)

        if aliexpress_links:
            self.logger.info(
                f"{message.message_id}: Found {len(aliexpress_links)} AliExpress links. Processing..."
            )
            if (
                "aliexpress.com" in aliexpress_data.get("awin", {}).get("advertisers", {})
                or "aliexpress.com" in aliexpress_data.get("admitad", {}).get("advertisers", {})
                or aliexpress_data.get("aliexpress", {}).get("app_key", "")
            ):
                self.logger.info(
                    f"{message.message_id}: AliExpress links found in advertisers. Skipping processing."
                )
                return False

            self.logger.debug(
                f"{message.message_id}: No advertiser found for AliExpress. Sending discount codes."
            )
            await self.show_discount_codes(context)
            return True

        self.logger.info(
            f"{message.message_id}: No AliExpress links found in the message."
        )
        return False
