from telegram import Message

from handlers.base_handler import BaseHandler
from config import ADMITAD_PUBLISHER_ID, ADMITAD_ADVERTISERS

ADMITAD_AFFILIATE_PATTERN = r"(https?://(?:[\w\-]+\.)?wextap\.com/g/[\w\d\-\._]+/?.*)"


class AdmitadHandler(BaseHandler):

    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        """Handles Admitad-managed store links in the message."""

        admitad_url_pattern = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
            "|".join([k.replace(".", r"\.") for k in ADMITAD_ADVERTISERS.keys()])
        )
        return await self._process_store_affiliate_links(
            message=message,
            publisher_id=ADMITAD_PUBLISHER_ID,
            advertisers=ADMITAD_ADVERTISERS,
            url_pattern=admitad_url_pattern,
            affiliate_pattern=ADMITAD_AFFILIATE_PATTERN,
            format_template="https://wextap.com/g/{advertiser_id}/?ulp={full_url}",
            affiliate_tag=None,
        )
