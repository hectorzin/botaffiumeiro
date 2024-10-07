import re
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
from handlers.aliexpress_handler import expand_aliexpress_short_link, ALIEXPRESS_SHORT_URL_PATTERN  # Import the function
from data.config import AWIN_PUBLISHER_ID, AWIN_ADVERTISERS, MSG_AFFILIATE_LINK_MODIFIED, MSG_REPLY_PROVIDED_BY_USER, MSG_ALIEXPRESS_DISCOUNT, ALIEXPRESS_DISCOUNT_CODES

# Pattern to detect Awin store links
AWIN_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
    "|".join([domain.replace(".", r"\.") for domain in AWIN_ADVERTISERS.keys()])
)

# Pattern to detect existing Awin affiliate links
AWIN_AFFILIATE_PATTERN = r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?[\w\d\-\./?=&%]+)"

def convert_to_awin_affiliate_link(url, store_domain):
    """Converts a store link into an Awin affiliate link."""
    encoded_url = quote_plus(url)
    advertiser_id = AWIN_ADVERTISERS.get(store_domain)

    if advertiser_id:
        return f"https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={AWIN_PUBLISHER_ID}&ued={encoded_url}"
    
    return url  # Return the original URL if no advertiser is found

def modify_existing_awin_link(url):
    """Modifies an existing Awin affiliate link to use the correct publisher ID."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Replace the current 'awinaffid' with your own AWIN_PUBLISHER_ID
    query_params['awinaffid'] = [AWIN_PUBLISHER_ID]

    # Rebuild the query string with the updated affiliate ID
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

    return new_url

async def handle_awin_links(message) -> bool:
    """Handles Awin-managed store links in the message."""
    # Detect short AliExpress links and expand them
    short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)

    new_text = message.text
    if short_links:
        for short_link in short_links:
            full_link = await expand_aliexpress_short_link(short_link)
            new_text = new_text.replace(short_link, full_link)

    # Detect and process Awin links
    awin_links = re.findall(AWIN_URL_PATTERN, new_text)  # Detect store links managed by Awin
    awin_affiliate_links = re.findall(AWIN_AFFILIATE_PATTERN, new_text)  # Detect existing affiliate links

    # Convert store links to Awin affiliate links
    if awin_links:
        for link, store_domain in awin_links:
            affiliate_link = convert_to_awin_affiliate_link(link, store_domain)
            new_text = new_text.replace(link, affiliate_link)

            # Append AliExpress discount codes if the store is AliExpress
            if "aliexpress" in store_domain:
                new_text += f"\n\n{MSG_ALIEXPRESS_DISCOUNT}{ALIEXPRESS_DISCOUNT_CODES}"

    # Modify existing Awin affiliate links
    if awin_affiliate_links:
        for link in awin_affiliate_links:
            modified_link = modify_existing_awin_link(link)
            new_text = new_text.replace(link, modified_link)

    # If modifications were made, send a new message
    if new_text != message.text:
        reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{message.from_user.username}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        await message.delete()
        await message.chat.send_message(text=polite_message, reply_to_message_id=reply_to_message_id)
        return True

    return False
