from handlers.base_handler import BaseHandler
from telegram import Message

from config import (
    AWIN_PUBLISHER_ID,
    AWIN_ADVERTISERS,
)

AWIN_AFFILIATE_PATTERN = (
    r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?[\w\d\-\./?=&%:]+)"
)

class AwinHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        """Handles Awin-managed store links in the message."""
        """Handles Awin-managed store links in the message."""
        AWIN_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
            "|".join([domain.replace(".", r"\.") for domain in AWIN_ADVERTISERS.keys()])
        )
        return await self._process_store_affiliate_links(
            message=message,
            publisher_id=AWIN_PUBLISHER_ID,
            advertisers=AWIN_ADVERTISERS,
            url_pattern=AWIN_URL_PATTERN,
            affiliate_pattern=AWIN_AFFILIATE_PATTERN,
            format_template="https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={affiliate_id}&ued={full_url}",
            affiliate_tag="awinaffid",
        )