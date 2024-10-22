from telegram import Message

from handlers.base_handler import BaseHandler,PATTERN_URL_QUERY

AWIN_PATTERN= r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?"+PATTERN_URL_QUERY+")"

class AwinHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, context) -> bool:
        """Handles Awin-managed store links in the message."""

        message, modified_text, self.selected_users = self._unpack_context(context)
        awin_url_pattern = self._build_affiliate_url_pattern("awin")
        return await self._process_store_affiliate_links(
            message=message,
            text=modified_text,
            url_pattern=awin_url_pattern,
            affiliate_platform="awin",
            affiliate_pattern=AWIN_PATTERN,
            format_template="https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={affiliate_id}&ued={full_url}",
            affiliate_tag="awinaffid",
        )
