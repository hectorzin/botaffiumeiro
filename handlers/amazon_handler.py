import re
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from data.config import AMAZON_AFFILIATE_ID, MSG_AFFILIATE_LINK_MODIFIED, MSG_REPLY_PROVIDED_BY_USER

# Regular expression for detecting Amazon links (both long and short)
AMAZON_URL_PATTERN = r"(https?://(?:www\.)?(amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)/[\w\d\-\./?=&%]+)"

async def handle_amazon_links(message) -> bool:
    """Handles Amazon links in the message."""
    amazon_links = re.findall(AMAZON_URL_PATTERN, message.text)

    if amazon_links:
        new_text = message.text
        for link in amazon_links:
            # Ensure link is a string, extract from tuple if needed
            if isinstance(link, tuple):
                link = link[0]
                
            expanded_link = expand_shortened_url(link)  # Expand shortened URLs
            affiliate_link = convert_to_affiliate_link(expanded_link)  # Convert to affiliate link
            new_text = new_text.replace(link, affiliate_link)

        user_first_name = message.from_user.first_name
        user_username = message.from_user.username
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{user_username if user_username else user_first_name}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"

        # Delete original message
        await message.delete()

        # Send modified message
        await message.chat.send_message(text=polite_message)

        return True  # The Amazon link was handled

    return False  # No Amazon links were found

def expand_shortened_url(url):
    """Expands shortened URLs like amzn.to or amzn.eu by following redirects."""
    parsed_url = urlparse(url)
    if "amzn.to" in parsed_url.netloc or "amzn.eu" in parsed_url.netloc:
        try:
            # Follow the redirection to get the full link
            response = requests.get(url, allow_redirects=True)
            return response.url  # Return the expanded URL
        except requests.RequestException as e:
            print(f"Error expanding shortened URL: {e}")
            return url  # Return the original shortened URL if expansion fails
    return url  # Return the original URL if it's not shortened

def convert_to_affiliate_link(url):
    """Convert an Amazon link to an affiliate link."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Remove original affiliate tag if it exists
    query_params.pop('tag', None)

    # Add your Amazon affiliate ID
    query_params['tag'] = [AMAZON_AFFILIATE_ID]

    # Rebuild the full URL with the affiliate tag
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))
    
    return new_url
