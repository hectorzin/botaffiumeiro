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

        return await self._process_store_affiliate_links(
            context=context,
            affiliate_platform="amazon",
            format_template="{domain}{path_before_query}?tag={advertiser_id}",
            affiliate_tag=None,
        )
