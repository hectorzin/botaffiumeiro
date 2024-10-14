import logging
import requests

from abc import ABC, abstractmethod
from telegram import Message
from urllib.parse import ParseResult,urlparse,parse_qs,urlencode


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

    def _expand_shortened_url_from_list(self, url: str, domains: list[str]) -> str:
        """
        Expands shortened URLs by following redirects if the domain matches one of the given domains.
        
        Args:
            url (str): The shortened URL to expand.
            domains (list): A list of domains for which the URL should be expanded.

        Returns:
            str: The expanded URL if the domain matches, or the original URL otherwise.
        """
        parsed_url = urlparse(url)
        
        # Check if the domain is in the list of provided domains
        if any(domain in parsed_url.netloc for domain in domains):
            # Call the superclass method to expand the URL
            url = self._expand_shortened_url(parsed_url)
        
        return url

    def generate_affiliate_url(self, original_url: str, format_template: str, affiliate_tag: str, affiliate_id: str) -> str:
        """
        Converts a product URL into an affiliate link based on the provided format template.

        Args:
            original_url (str): The original product URL.
            format_template (str): The template for the affiliate URL, e.g., '{domain}/{path_before_query}?{affiliate_tag}={affiliate_id}'.
            affiliate_tag (str): The query parameter for the affiliate ID (e.g., 'tag', 'aff_id').
            affiliate_id (str): The affiliate ID for the platform.
            additional_params (dict): Additional query parameters to be included in the final URL.

        Returns:
            str: The URL with the affiliate tag added according to the template.
        """
        # Parse the original URL
        parsed_url = urlparse(original_url)

        # Extract domain, path before the query, and full URL
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_before_query = parsed_url.path
        full_url = f"{domain}{parsed_url.path}"

        # Parse existing query parameters
        query_params = parse_qs(parsed_url.query)

        # Add or update affiliate tag
        query_params[affiliate_tag] = [affiliate_id]


        # Build the new query string
        new_query = urlencode(query_params, doseq=True)

        # Format the output using the provided format_template
        affiliate_url = format_template.format(
            domain=domain,
            path_before_query=path_before_query,
            full_url=full_url,
            affiliate_tag=affiliate_tag,
            affiliate_id=affiliate_id
        )

        # Check if query params (affiliate tag or additional) are missing from the format_template
        if  '{affiliate_id}' not in format_template:
            if '?' not in affiliate_url:
                affiliate_url += f"?{new_query}"
            else:
                affiliate_url += f"&{new_query}"

        return affiliate_url

    @abstractmethod
    async def handle_links(self, message: Message) -> bool:
        pass
