# Botaffiumeiro addon for Home Assistant
Modify Telegram links for affiliate programs and manage them across multiple platforms, such as Amazon, AliExpress, Awin, and Admitad.

## How to Configure
The add-on supports multiple configuration options that allow you to manage how Telegram messages are handled and how affiliate links are generated for different platforms.

## Configuration Fields
Below is a breakdown of all the available configuration fields, including examples for list-based fields.

### 1. Telegram Settings
**bot_token**: Your Telegram bot token obtained from BotFather. This is required to use the bot.

**delete_messages**: Whether to delete the original Telegram message or simply reply with the modified message.

**excluded_users**: List of Telegram users whose messages should not be modified by the bot. This is useful for excluding admins or users whose messages should remain unchanged. It is a list of user objects with the following structure:

```
  - id: "Username1"
  - id: "Username2"
```

### 2. Message settings
**msg_affiliate_link_modified**: The message that will be sent when a Telegram message has been modified with an affiliate link.

**msg_reply_provided_by_user**: The message that indicates which user provided the original message with the affiliate link.


### 3. Amazon settings
**amazon_affiliate_id**: Your Amazon Affiliate ID, which will be appended to Amazon links to generate affiliate URLs.

### 4. Aliexpress settings
**aliexpress_app_key**: Your AliExpress App Key, used for API requests to generate affiliate links.

**aliexpress_app_secret**: Your AliExpress App Secret, used for signing API requests.

**aliexpress_tracking_id**: Your AliExpress Tracking ID, used for affiliate tracking.

**aliexpress_discount_codes**: List of AliExpress discount codes that will be sent with each message. You can provide multiple discount codes in a list format, with each code being a separate line with the following structure:

```
  - line: "Here are your discount codes!"
  - line: "💥 2$ off for purchases over 20$: 【CODE1】"
  - line: "💰 5$ off for purchases over 50$: 【CODE2】"
```


### 5. Awin Settings
**awin_publisher_id**: Your Awin Publisher ID, which will be used to manage affiliate links for Awin-supported stores.

**awin_advertisers**: A list of Awin-supported stores and their respective advertiser IDs. These IDs are required to generate affiliate links for specific stores. You must use the following structure:

```
  - domain: "store1.com"
    id: "advertiser_id_1"
  - domain: "store2.com"
    id: "advertiser_id_2"
```

### 6. Admitad Settings
**admitad_publisher_id**: Your Admitad Publisher ID, used to manage affiliate links for Admitad-supported stores.

**admitad_advertisers**: A list of Admitad-supported stores and their respective advertiser IDs, required to generate affiliate links for specific stores. You must use the following structure:

```
  - domain: "store1.com"
    id: "campaign_id_1"
  - domain: "store2.com"
    id: "campaign_id_2"
```

### 7. LOG
**log_level**: Set the logging level for the bot. Options include: DEBUG, INFO, WARN, ERROR, and CRITICAL.
