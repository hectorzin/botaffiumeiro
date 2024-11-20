"""Module for handling affiliate link patterns."""

from config import ConfigurationManager

from handlers.base_handler import BaseHandler
from handlers.patterns import PATTERNS, PatternConfig


class PatternHandler(BaseHandler):
    """Handler for processing links based on predefined patterns."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialize the PatternHandler.

        Args:
        ----
            config_manager (ConfigurationManager): The configuration manager instance.

        """
        super().__init__(config_manager)

    async def process_affiliate_link(
        self, context: dict, platform: str, data: PatternConfig
    ) -> bool:
        """Process the affiliate link for a given platform.

        Args:
        ----
            context (dict): The context containing the message and user data.
            platform (str): The name of the affiliate platform.
            data (dict): The platform-specific configuration data.

        Returns:
        -------
            bool: True if the affiliate link was processed, False otherwise.

        """
        return await self._process_store_affiliate_links(
            context=context,
            affiliate_platform=platform,  # Usar el nombre de la plataforma
            format_template=data["format_template"],
            affiliate_tag=data["affiliate_tag"],
        )

    async def handle_links(self, context: dict) -> bool:
        """Handle links based on platform-specific patterns.

        Args:
        ----
            context (dict): The context containing the message and user data.

        Returns:
        -------
            bool: True if any links were processed, False otherwise.

        """
        processed = False
        for platform, data in PATTERNS.items():
            processed |= await self.process_affiliate_link(context, platform, data)

        return processed
