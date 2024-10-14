from handlers.base_handler import BaseHandler
from telegram import Message

from config import (
    ADMITAD_PUBLISHER_ID,
    ADMITAD_ADVERTISERS,
)

ADMITAD_AFFILIATE_PATTERN = (
    r"(https?://(?:[\w\-]+\.)?ad\.admitad\.com/g/[\w\d]+/[\w\d]+/[\w\d\-\./?=&%]+)"
)

class AdmitadHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        """Handles Awin-managed store links in the message."""
        """Handles Awin-managed store links in the message."""
        ADMITAD_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
            "|".join([domain.replace(".", r"\.") for domain in ADMITAD_ADVERTISERS.keys()])
        )
        return self._process_affiliate_links(
            message=message,
            publisher_id=ADMITAD_PUBLISHER_ID,
            advertisers=ADMITAD_ADVERTISERS,
            url_pattern=ADMITAD_URL_PATTERN,
            affiliate_pattern=ADMITAD_AFFILIATE_PATTERN,
            format_template="https://ad.admitad.com/g/{advertiser_id}/{affiliate_id}/?ulp={full_url}",
            affiliate_tag="subid",
        )
