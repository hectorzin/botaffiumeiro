[![GitHub release (latest by date)](https://img.shields.io/github/v/release/hectorzin/botaffiumeiro)](https://github.com/hectorzin/botaffiumeiro/releases)
[![Build](https://img.shields.io/github/actions/workflow/status/hectorzin/botaffiumeiro/deploy.yml)](https://github.com/hectorzin/botaffiumeiro/actions/workflows/deploy.yml)

# botaffiumeiro

botaffiumeiro is a Telegram bot that detects Amazon, Aliexpress and other links shared in Telegram groups and automatically converts them into affiliate links using your custom Amazon Affiliate ID. This is especially useful for those who want to monetize links shared in their communities.

## Features:

- Detects both full URLs and short links (amzn.to, amzn.eu).
- Replaces shared Amazon links with your personalized affiliate links.
- Adds AliExpress discount codes when AliExpress links are detected.
- Allows certain users to be excluded from Amazon link modifications.
- Works seamlessly in group chats.
- Easy to set up and customize.

## Installation

## Docker Installation

#### 1. Create Container

```bash
$ docker create \
  --name=botaffiumeiro \
  -v /path/to/host/data:/app/data \
  --restart unless-stopped \
  ghcr.io/hectorzin/botaffiumeiro
```

#### 2. Modify config.py file

Modify the `/path/to/host/data/config.py` file with your settings.

#### 3. Run the container

```bash
$ docker start botaffiumeiro
```

### Manual Installation

To ensure that the bot works correctly, you need to install Python and the required libraries.

#### 1. Install Python

First, ensure that you have Python installed. You can download Python from the official website: [Python Downloads](https://www.python.org/downloads/).

#### 2. Install the Required Libraries

Once Python is installed, you need to run the following commands to install the required Python libraries:

```bash
pip install -r requirements.txt
```

## How to use:

1. Set up your bot token, API ID, API hash, and your Amazon Affiliate ID.
2. Install Python and the required libraries.
3. Run the bot on a machine with Python by executing the following command: `python botaffiumeiro.py`

Once configured and running, the bot will detect Amazon links in any group it's added to and replace them with your affiliate links, making it easy to earn commissions from shared products.

## How to Get API ID, API Hash, and Bot Token

### 1. Getting the API ID and API Hash

To obtain your **API ID** and **API Hash**, follow these steps:

1. Go to [my.telegram.org](https://my.telegram.org).
2. Log in using the phone number associated with your Telegram account.
3. Once logged in, click on **API Development Tools**.
4. Fill in the required details to create a new app:
   - **App title**: Choose a name for your app (it can be anything).
   - **Short name**: Enter a short identifier for your app.
5. After submitting the form, you'll be provided with your **API ID** and **API Hash**. Save these for later use.

### 2. Getting the Bot Token

To obtain the **Bot Token**, follow these steps:

1. Open Telegram and search for the user **BotFather** or click on this link: [BotFather](https://t.me/BotFather).
2. Start a chat with BotFather and send the command `/start`.
3. Use the command `/newbot` to create a new bot. Follow the prompts to choose a name and username for your bot.
   - The **bot name** can be anything.
   - The **username** must be unique and should end with "bot" (e.g., `YourBotName_bot`).
4. After the bot is created, BotFather will provide a **Bot Token**. Save this token for later use.

### 3. Enable Bot Privacy (Disable Group Privacy)

Telegram has a privacy setting for bots that prevents them from reading messages in groups unless they are mentioned directly, or the admin has configured the bot to run in **No Privacy Mode**. To allow the bot to read all messages, follow these steps:

1. **Go to BotFather**:
   - Open a conversation with **BotFather** in Telegram or click [here](https://t.me/BotFather).
2. **Configure the privacy mode**:
   - Send the command `/mybots` to BotFather.
   - Select your bot from the list.
   - Then select **Bot Settings**.
   - Choose **Group Privacy**.
   - If privacy is enabled, disable it by selecting **Disable Group Privacy**.

This will allow the bot to read all messages in the group, not just the ones where it is mentioned directly.

### 4. Add the Bot to a Group

If your bot will operate in a group, follow these steps to add it:

1. Add the bot to the desired Telegram group.
2. Promote the bot to **Admin** in the group to ensure it has the necessary permissions to read and modify messages.

---

### Example Configuration

Once you have the **API ID**, **API Hash**, and **Bot Token**, replace the placeholders in your code:

```python
BOT_TOKEN = "your_bot_token_here"  # Replace with your bot token
```

### Supported affiliate services
- Amazon
- Awin (this can work for Aliexpress)
- Admitad (this can work for Aliexpress)

### Exclude Certain Users from Link Modification

You can exclude certain users from having their Amazon links modified by the bot. You can do this by defining a list of usernames or Telegram user IDs.

```
EXCLUDED_USERS = ["username1", "username2", 123456789]  # Replace with the usernames or Telegram IDs of excluded users
```

### AliExpress Discount Codes

When the bot detects an AliExpress link, it will automatically reply to the message with the pre-configured discount codes. You can modify these discount codes as needed.

```
ALIEXPRESS_DISCOUNT_CODES = """💰2$ off on purchases over 20$:【IFPTKOH】
💰5$ off on purchases over 50$:【IFPT35D】
💰25$ off on purchases over 200$:【IFPQDMH】
💰50$ off on purchases over 400$:【IFP5RIN】"""
```

### Customizing the Bot

You can also customize the bot's response messages and translate them into different languages. To do this, you can modify the message strings in the code. For example:

```python
# Messages used by the bot
MSG_AFFILIATE_LINK_MODIFIED = "Here is the modified link with our affiliate program:"
MSG_REPLY_PROVIDED_BY_USER = "Reply provided by"
MSG_ALIEXPRESS_DISCOUNT = "💥 Special AliExpress discount codes:\n\n"
```

By changing these variables, you can personalize how the bot interacts with users. This makes it easy to:

1. Translate the bot's messages into any language.
2. Adjust the messaging style to fit your preferences.