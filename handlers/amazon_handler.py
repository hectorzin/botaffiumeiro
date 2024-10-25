import re

from handlers.base_handler import BaseHandler, PATTERN_URL_QUERY

AMAZON_PATTERN = (
    r"(https?://(?:www\.)?(?:amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)"
    + PATTERN_URL_QUERY
    + ")"
)


class AmazonHandler(BaseHandler):
    def __init__(self):
        super().__init__()

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
