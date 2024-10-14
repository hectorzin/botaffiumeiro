import re

from config import (
    AMAZON_AFFILIATE_ID,
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
    DELETE_MESSAGES,
)
from handlers.base_handler import BaseHandler
from telegram import Message
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

AMAZON_URL_PATTERN = r"(https?://(?:www\.)?(amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)/[\w\d\-\./?=&%]+)"


class AmazonHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _expand_shortened_url(self, url):
        """Expands shortened URLs like amzn.to or amzn.eu by following redirects."""
        self.logger.info(f"Try expanding shortened URL: {url}")
        parsed_url = urlparse(url)
        if "amzn.to" in parsed_url.netloc or "amzn.eu" in parsed_url.netloc:
            url = super()._expand_shortened_url(parsed_url)
        return url


    async def handle_links(self, message: Message) -> bool:
        """Handles Amazon links in the message."""
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

                expanded_link = self._expand_shortened_url_from_list(link, ["amzn.to", "amzn.eu"])
                affiliate_link = self.generate_affiliate_url(
                    expanded_link,
                    format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
                    affiliate_tag="tag",
                    affiliate_id=AMAZON_AFFILIATE_ID
                )
                new_text = new_text.replace(link, affiliate_link)

            user_first_name = message.from_user.first_name
            user_username = message.from_user.username
            polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"

            if DELETE_MESSAGES:
                # remove original message and creates a new one
                await message.delete()
                await message.chat.send_message(text=polite_message)
                self.logger.info(
                    f"{message.message_id}: Original message deleted annd sent modified message with affiliate links."
                )
            else:
                # Answers the original message
                reply_to_message_id = message.message_id
                await message.chat.send_message(
                    text=polite_message, reply_to_message_id=reply_to_message_id
                )
                self.logger.info(
                    f"{message.message_id}: Replied to message with affiliate links."
                )

            return True

        self.logger.info(f"{message.message_id}: No Amazon links found in the message.")
        return False
