"""Handler for managing AliExpress links and discount codes."""

import re

from config import ConfigurationManager

from handlers.base_handler import PATTERN_URL_QUERY, BaseHandler

ALIEXPRESS_PATTERN = (
    r"(https?://(?:[a-z]{2,3}\.)?aliexpress\.[a-z]{2,3}(?:\.[a-z]{2,3})?"
    + PATTERN_URL_QUERY
    + ")"
)


class AliexpressHandler(BaseHandler):
    """Handler for managing AliExpress links and discount codes."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialize the AliexpressHandler.

        Args:
        ----
            config_manager (ConfigurationManager): The configuration manager instance.

        """
        super().__init__(config_manager)

    async def show_discount_codes(self, context: dict) -> None:
        """Display the AliExpress discount codes for the user.

        Args:
        ----
            context (Dict): The context containing the message and selected users.

        """
        # Retrieve AliExpress-specific data
        message, modified_text, self.selected_users = self._unpack_context(context)
        aliexpress_data = self.selected_users.get("aliexpress.com", {})

        # Check if there are any discount codes available for AliExpress
        aliexpress_discount_codes = aliexpress_data.get("aliexpress", {}).get(
            "discount_codes", None
        )

        if not aliexpress_discount_codes:
            self.logger.info(
                "%s: Discount codes are empty. Skipping reply.",
                message.message_id,
            )
            return

        # Send the discount codes as a response to the original message
        await message.chat.send_message(
            f"{aliexpress_discount_codes}",
            reply_to_message_id=message.message_id,
        )
        self.logger.info(
            "%s: Sent AliExpress discount codes.",
            message.message_id,
        )
        user = aliexpress_data.get("user", {})
        self.logger.info("User chosen: %s", user)

    async def handle_links(self, context: dict) -> bool:
        """Handle both long and short AliExpress links in the message.

        Args:
        ----
            context (Dict): The context containing the message and selected users.

        Returns:
        -------
            bool: True if links were handled, False otherwise.

        """
        message, modified_text, self.selected_users = self._unpack_context(context)
        # Extraemos self.selected_users.get("aliexpress.com", {}) a una variable
        self.selected_users.get("aliexpress.com", {})

        aliexpress_links = re.findall(ALIEXPRESS_PATTERN, modified_text)

        if aliexpress_links:
            self.logger.info(
                "%s: Found %d AliExpress links. Processing...",
                message.message_id,
                len(aliexpress_links),
            )
            await self.show_discount_codes(context)
            return True

        self.logger.info(
            "%s: No AliExpress links found in the message.",
            message.message_id,
        )
        return False
