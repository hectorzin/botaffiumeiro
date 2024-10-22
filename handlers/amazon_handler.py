import re

from telegram import Message
from handlers.base_handler import BaseHandler,PATTERN_URL_QUERY

AMAZON_PATTERN=r"(https?://(?:www\.)?(?:amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)"+PATTERN_URL_QUERY+")"

class AmazonHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links2(self, context) -> bool:
        """Handles Amazon links in the message."""
        message, modified_text, self.selected_users = self._unpack_context(context)
        amazon_affiliate_id = self.selected_users.get("amazon", {}).get("affiliate_id", "")
        if not amazon_affiliate_id:
            self.logger.info("Amazon affiliate ID is not set. Skipping processing.")
            return False

        self.logger.info(
            f"{message.message_id}: Handling Amazon links in the message..."
        )
        amazon_links = re.findall(AMAZON_PATTERN, modified_text)

        if amazon_links:
            self.logger.info(
                f"{message.message_id}: Found {len(amazon_links)} Amazon links. Processing..."
            )
            new_text = modified_text
            for link in amazon_links:
                # Ensure link is a string, extract from tuple if needed
                if isinstance(link, tuple):
                    link = link[0]

                selected_affiliate_data = self.selected_users.get("amazon", {})
                affiliate_id = selected_affiliate_data.get("affiliate_id", None)
                affiliate_link = self._generate_affiliate_url(
                    link,
                    format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
                    affiliate_tag="tag",
                    affiliate_id=affiliate_id,
                )
                new_text = new_text.replace(link, affiliate_link)

            await self._process_message(message, new_text)

            return True

        self.logger.info(f"{message.message_id}: No Amazon links found in the message.")
        return False

    async def handle_links(self, context) -> bool:
        """Handles Admitad-managed store links in the message."""

        message, modified_text, self.selected_users = self._unpack_context(context)
        amazon_url_pattern = self._build_affiliate_url_pattern("amazon")

        return await self._process_store_affiliate_links(
            message=message,
            text=modified_text,
            url_pattern=amazon_url_pattern,
            affiliate_platform="amazon",
            affiliate_pattern=AMAZON_PATTERN,
            format_template="{domain}{path_before_query}?tag={advertiser_id}",
            affiliate_tag=None,
        )
