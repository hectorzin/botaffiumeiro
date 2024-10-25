from handlers.base_handler import BaseHandler, PATTERN_URL_QUERY

ADMITAD_PATTERN = r"(https?://(?:[\w\-]+\.)?wextap\.com/g" + PATTERN_URL_QUERY + ")"


class AdmitadHandler(BaseHandler):

    def __init__(self):
        super().__init__()

    async def handle_links(self, context) -> bool:
        """Handles Admitad-managed store links in the message."""

        return await self._process_store_affiliate_links(
            context=context,
            affiliate_platform="admitad",
            format_template="https://wextap.com/g/{advertiser_id}/?ulp={full_url}",
            affiliate_tag=None,
        )
