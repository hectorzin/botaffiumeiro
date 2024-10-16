import re

from telegram import Message

from config import AMAZON_AFFILIATE_ID
from handlers.base_handler import BaseHandler

AMAZON_URL_PATTERN = r"(https?://(?:www\.)?(amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)/[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=%]+)"


class AmazonHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        """Handles Amazon links in the message."""
        if not AMAZON_AFFILIATE_ID:
            self.logger.info("Amazon affiliate ID is not set. Skipping processing.")
            return False

        self.logger.info(
            f"{message.message_id}: Handling Amazon links in the message..."
        )
        amazon_links = re.findall(AMAZON_URL_PATTERN, message.text)

        if amazon_links:
            self.logger.info(
                f"{message.message_id}: Found {len(amazon_links)} Amazon links. Processing..."
            )
            new_text = message.text
            for link in amazon_links:
                # Ensure link is a string, extract from tuple if needed
                if isinstance(link, tuple):
                    link = link[0]

                expanded_link = self._expand_shortened_url_from_list(
                    link, ["amzn.to", "amzn.eu"]
                )
                affiliate_link = self._generate_affiliate_url(
                    expanded_link,
                    format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
                    affiliate_tag="tag",
                    affiliate_id=AMAZON_AFFILIATE_ID,
                )
                new_text = new_text.replace(link, affiliate_link)

            await self._process_message(message, new_text)

            return True

        self.logger.info(f"{message.message_id}: No Amazon links found in the message.")
        return False
