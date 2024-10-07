import re
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
from handlers.aliexpress_handler import expand_aliexpress_short_link, ALIEXPRESS_SHORT_URL_PATTERN  # Import the function
from data.config import ADMITAD_PUBLISHER_ID, ADMITAD_ADVERTISERS, MSG_AFFILIATE_LINK_MODIFIED, MSG_REPLY_PROVIDED_BY_USER, MSG_ALIEXPRESS_DISCOUNT, ALIEXPRESS_DISCOUNT_CODES

# Pattern to detect Admitad store links
ADMITAD_URL_PATTERN = r"(https?://(?:[\w\-]+\.)?({})/[\w\d\-\./?=&%]+)".format(
    "|".join([domain.replace(".", r"\.") for domain in ADMITAD_ADVERTISERS.keys()])
)

# Pattern to detect existing Admitad affiliate links
ADMITAD_AFFILIATE_PATTERN = r"(https?://(?:[\w\-]+\.)?ad\.admitad\.com/g/[\w\d]+/[\w\d]+/[\w\d\-\./?=&%]+)"

def convert_to_admitad_affiliate_link(url, store_domain):
    """Converts a store link into an Admitad affiliate link."""
    encoded_url = quote_plus(url)
    advcampaignid = ADMITAD_ADVERTISERS.get(store_domain)

    if advcampaignid:
        return f"https://ad.admitad.com/g/{advcampaignid}/{ADMITAD_PUBLISHER_ID}/?ulp={encoded_url}"
    
    return url  # Return the original URL if no advertiser is found

def modify_existing_admitad_link(url):
    """Modifies an existing Admitad affiliate link to use the correct publisher ID."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Replace the current 'advcampaignid' and 'publisher_id' with your own
    path_segments = parsed_url.path.split('/')
    if len(path_segments) >= 4:
        path_segments[2] = ADMITAD_ADVERTISERS.get(path_segments[2], path_segments[2])  # Update advcampaignid
        path_segments[3] = ADMITAD_PUBLISHER_ID  # Update publisher_id

    new_path = '/'.join(path_segments)
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, new_path, parsed_url.params, new_query, parsed_url.fragment))

    return new_url
	
async def handle_admitad_links(message) -> bool:
    """Handles Admitad-managed store links in the message."""
    # Detect short AliExpress links and expand them
    short_links = re.findall(ALIEXPRESS_SHORT_URL_PATTERN, message.text)

    new_text = message.text
    if short_links:
        for short_link in short_links:
            full_link = await expand_aliexpress_short_link(short_link)
            new_text = new_text.replace(short_link, full_link)

    # Detect and process Admitad links
    admitad_links = re.findall(ADMITAD_URL_PATTERN, new_text)  # Detect store links managed by Admitad
    admitad_affiliate_links = re.findall(ADMITAD_AFFILIATE_PATTERN, new_text)  # Detect existing affiliate links

    # Convert store links to Admitad affiliate links
    if admitad_links:
        for link, store_domain in admitad_links:
            affiliate_link = convert_to_admitad_affiliate_link(link, store_domain)
            new_text = new_text.replace(link, affiliate_link)

            # Append AliExpress discount codes if the store is AliExpress
            if "aliexpress" in store_domain:
                new_text += f"\n\n{MSG_ALIEXPRESS_DISCOUNT}{ALIEXPRESS_DISCOUNT_CODES}"

    # Modify existing Admitad affiliate links
    if admitad_affiliate_links:
        for link in admitad_affiliate_links:
            modified_link = modify_existing_admitad_link(link)
            new_text = new_text.replace(link, modified_link)

    # If modifications were made, send a new message
    if new_text != message.text:
        reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
        polite_message = f"{MSG_REPLY_PROVIDED_BY_USER} @{message.from_user.username}:\n\n{new_text}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        await message.delete()
        await message.chat.send_message(text=polite_message, reply_to_message_id=reply_to_message_id)
        return True

    return False
