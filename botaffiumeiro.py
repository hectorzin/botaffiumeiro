from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from data.config import BOT_TOKEN, EXCLUDED_USERS
from handlers.amazon_handler import handle_amazon_links
from handlers.aliexpress_handler import handle_aliexpress_links
from handlers.awin_handler import handle_awin_links
from handlers.admitad_handler import handle_admitad_links

def is_user_excluded(update: Update) -> bool:
    """Checks if the user is in the list of excluded users."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    return user_id in EXCLUDED_USERS or (username and username in EXCLUDED_USERS)

async def modify_link(update: Update, context) -> None:
    """Modifies Amazon, AliExpress, Awin, and Admitad links in messages."""
    
    if is_user_excluded(update):
        return  # Skip excluded users

    message = update.message

    # Ensure the message contains text before trying to process links
    if message is None or not message.text:
        return  # If there's no text (e.g., it's an image or file), exit the function

    # Handle Amazon links
    await handle_amazon_links(message)

    # Handle Awin-managed stores
    await handle_awin_links(message)

    # Handle Admitad-managed stores
    await handle_admitad_links(message)

    # Handle AliExpress links
    await handle_aliexpress_links(message)

def main() -> None:
    """Start the bot with python-telegram-bot"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the message handler for all group messages
    application.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, modify_link))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
