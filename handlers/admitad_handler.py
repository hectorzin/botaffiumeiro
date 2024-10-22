from telegram import Message

from handlers.base_handler import BaseHandler,PATTERN_URL_QUERY

ADMITAD_PATTERN=  r"(https?://(?:[\w\-]+\.)?wextap\.com/g"+PATTERN_URL_QUERY+")"

class AdmitadHandler(BaseHandler):

    def __init__(self):
        super().__init__()

    async def handle_links(self, context) -> bool:
        """Handles Admitad-managed store links in the message."""

        message, modified_text, self.selected_users = self._unpack_context(context)
        admitad_url_pattern = self._build_affiliate_url_pattern("admitad")

        return await self._process_store_affiliate_links(
            message=message,
            text=modified_text,
            url_pattern=admitad_url_pattern,
            affiliate_platform="admitad",
            affiliate_pattern=ADMITAD_PATTERN,
            format_template="https://wextap.com/g/{advertiser_id}/?ulp={full_url}",
            affiliate_tag=None,
        )
