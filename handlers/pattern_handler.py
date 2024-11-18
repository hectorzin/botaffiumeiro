from handlers.base_handler import BaseHandler
from handlers.patterns import PATTERNS


class PatternHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    async def process_affiliate_link(self, context, platform, data):
        """Processes the affiliate link for the given platform."""
        return await self._process_store_affiliate_links(
            context=context,
            affiliate_platform=platform,  # Usar el nombre de la plataforma
            format_template=data["format_template"],
            affiliate_tag=data["affiliate_tag"],
        )

    async def handle_links(self, context) -> bool:
        """Handles links based on the platform's patterns."""
        processed = False
        for platform, data in PATTERNS.items():
            processed |= await self.process_affiliate_link(context, platform, data)

        return processed
