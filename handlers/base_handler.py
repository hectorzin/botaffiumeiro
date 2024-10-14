import logging
import requests

from abc import ABC, abstractmethod
from telegram import Message
from urllib.parse import ParseResult


class BaseHandler(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _expand_shortened_url(self, url: ParseResult):
        """Expands shortened URLs by following redirects."""
        self.logger.info(f"Try expanding shortened URL: {url}")
        try:
            response = requests.get(url, allow_redirects=True)
            self.logger.debug(f"Expanded URL {url} to full link: {response.url}")
            return response.url
        except requests.RequestException as e:
            self.logger.error(f"Error expanding shortened URL {url}: {e}")
            return url

    @abstractmethod
    async def handle_links(self, message: Message) -> bool:
        pass
