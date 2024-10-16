from telegram import Message

from config import (
    AWIN_PUBLISHER_ID,
    AWIN_ADVERTISERS,
)
from handlers.base_handler import BaseHandler

AWIN_AFFILIATE_PATTERN = r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=%]+)"


class AwinHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def handle_links(self, message: Message) -> bool:
        """Handles Awin-managed store links in the message."""
        awin_url_pattern = r"(https?://(?:[\w\-]+\.)?({})/[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=%]+)".format(
            "|".join([k.replace(".", r"\.") for k in AWIN_ADVERTISERS.keys()])
        )
        
        return await self._process_store_affiliate_links(
            message=message,
            publisher_id=AWIN_PUBLISHER_ID,
            advertisers=AWIN_ADVERTISERS,
            url_pattern=awin_url_pattern,
            affiliate_pattern=AWIN_AFFILIATE_PATTERN,
            format_template="https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={affiliate_id}&ued={full_url}",
            affiliate_tag="awinaffid",
        )
