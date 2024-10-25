from handlers.base_handler import BaseHandler, PATTERN_URL_QUERY

AWIN_PATTERN = (
    r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?" + PATTERN_URL_QUERY + ")"
)


class AwinHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, context) -> bool:
        """Handles Awin-managed store links in the message."""

        return await self._process_store_affiliate_links(
            context=context,
            affiliate_platform="awin",
            format_template="https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={affiliate_id}&ued={full_url}",
            affiliate_tag="awinaffid",
        )
