<h1 style="display: flex; align-items: center;">
  <img src="https://raw.githubusercontent.com/hectorzin/botaffiumeiro/main/docs/assets/logo_botaffiumeiro.png" width="40" style="margin-right: 10px;"/>
  Botaffiumeiro addon for Home Assistant
</h1>

Modify Telegram links for affiliate programs and manage them across multiple platforms, such as Amazon, AliExpress, Awin, and Admitad.

## How to Configure

The add-on supports multiple configuration options that allow you to manage how Telegram messages are handled and how affiliate links are generated for different platforms.

## Configuration Fields

Below is a breakdown of all the available configuration fields, including examples for list-based fields.

### 1. Telegram Settings

- **bot_token**: Your Telegram bot token obtained from BotFather. This is required to use the bot. For information about creating a bot with BotFather look at the BotAffiumeiro repository: https://github.com/hectorzin/botaffiumeiro
- **delete_messages**: Whether to delete the original Telegram message or simply reply with the modified message.
- **excluded_users**: List of Telegram users whose messages should not be modified by the bot. This is useful for excluding admins or users whose messages should remain unchanged. It is a list of user objects with the following structure:

  ```yaml
  - id: "Username1"
  - id: "Username2"
  ```

  **NOTE**: If you want to leave the list empty you must write []

- **discount_keywords**: List of keywords that trigger the bot to display AliExpress discount codes when used in a message. You can define multiple keywords in a list format using the following structure:

  ```yaml
  - key: "discounts"
  - key: "bonus"
  - key: "bonuses"
  - key: "aliexpress"
  ```

**NOTE**: If you want to leave the list empty you must write []

### 2. Message settings

- **msg_affiliate_link_modified**: The message that will be sent when a Telegram message has been modified with an affiliate link.
- **msg_reply_provided_by_user**: The message that indicates which user provided the original message with the affiliate link.

### 3. Amazon settings

A list of domains and ids per domain:

```yaml
- domain: amazon.es
  id: botaffiumeiro_cofee-21
- domain: amazon.com
  id: hectorzindomo-20
```

### 4. Aliexpress settings

- **aliexpress_app_key**: Your AliExpress App Key, used for API requests to generate affiliate links.
- **aliexpress_app_secret**: Your AliExpress App Secret, used for signing API requests.
- **aliexpress_tracking_id**: Your AliExpress Tracking ID, used for affiliate tracking.
- **aliexpress_discount_codes**: List of AliExpress discount codes that will be sent with each message. You can provide multiple discount codes in a list format, with each code being a separate line with the following structure:

  ```yaml
  - line: "Here are your discount codes!"
  - line: "💥 2$ off for purchases over 20$: 【CODE1】"
  - line: "💰 5$ off for purchases over 50$: 【CODE2】"
  ```

  **NOTE**: If you want to leave the list empty you must write []

### 5. Awin Settings

- **awin_publisher_id**: Your Awin Publisher ID, which will be used to manage affiliate links for Awin-supported stores.
- **awin_advertisers**: A list of Awin-supported stores and their respective advertiser IDs. These IDs are required to generate affiliate links for specific stores. You must use the following structure:

  ```yaml
  - domain: "store1.com"
    id: "advertiser_id_1"
  - domain: "store2.com"
    id: "advertiser_id_2"
  ```

  **NOTE**: If you want to leave the list empty you must write []

### 6. Admitad Settings

- **admitad_publisher_id**: Your Admitad Publisher ID, used to manage affiliate links for Admitad-supported stores.
- **admitad_advertisers**: A list of Admitad-supported stores and their respective advertiser IDs, required to generate affiliate links for specific stores. You must use the following structure:

  ```yaml
  - domain: "store1.com"
    id: "campaign_id_1"
  - domain: "store2.com"
    id: "campaign_id_2"
  ```

  **NOTE**: If you want to leave the list empty you must write []

### 7. Tradedoubler Settings

- **tradedoubler_publisher_id**: Your Tradedoubler Publisher ID, used to manage affiliate links for Tradedoubler-supported stores.
- **tradedoubler_advertisers**: A list of Tradedoubler-supported stores and their respective advertiser IDs, required to generate affiliate links for specific stores. You must use the following structure:

  ```yaml
  - domain: "store1.com"
    id: "campaign_id_1"
  - domain: "store2.com"
    id: "campaign_id_2"
  ```

  **NOTE**: If you want to leave the list empty you must write []

### 8. Support for creators

- **creator_affiliate_percentage**: This parameter allows you to define what percentage of the links shared in Telegram groups will be replaced with affiliate links belonging to the software creators. However, there are a few important conditions to keep in mind:
  1. **Available Affiliate Links**: Only links that the software creators have affiliate programs for will be eligible to be replaced.

  2. **Affiliate Priority**: If the user does not have an affiliate link for a specific domain, but the creators of the software do, the creators' affiliate link will be used instead.

  You can define this percentage in the following format:

  ```yaml
  creator_affiliate_percentage: 10 # Example: 10%
  ```

### 9. LOG

- **log_level**: Set the logging level for the bot. Options include: _DEBUG_, _INFO_, _WARN_, _ERROR_, and _CRITICAL_.

## More information

For more information look at the Botafumeiro repository https://github.com/hectorzin/botaffiumeiro

## Spanish tutorial

[![Watch the video](https://github.com/hectorzin/botaffiumeiro/raw/main/docs/assets/spanish_video_thumbnail.png)](https://youtu.be/qr_WBQIQmUQ)
