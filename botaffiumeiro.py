import logging

from config import LOG_LEVEL, BOT_TOKEN, EXCLUDED_USERS
from telegram import Update, User
from telegram.ext import Application, MessageHandler, filters

from handlers.admitad_handler import AdmitadHandler
from handlers.aliexpress_api_handler import AliexpressAPIHandler
from handlers.aliexpress_handler import AliexpressHandler
from handlers.amazon_handler import AmazonHandler
from handlers.awin_handler import AwinHandler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL,
)
logger = logging.getLogger(__name__)


def is_user_excluded(user: User) -> bool:
    """Checks if the user is in the list of excluded users."""

    user_id = user.id
    username = user.username
    logger.debug(f"Checking if user {username} (ID: {user_id}) is excluded.")
    excluded = user_id in EXCLUDED_USERS or (username and username in EXCLUDED_USERS)
    logger.debug(f"User {username} (ID: {user_id}) is excluded: {excluded}")
    return excluded

async def process_link_handlers(message) -> None:
    """Process all link handlers for Amazon, Awin, Admitad, and AliExpress."""

    logger.info(f"Processing link handlers for message ID: {message.message_id}...")

    await AmazonHandler().handle_links(message)
    await AwinHandler().handle_links(message)
    await AdmitadHandler().handle_links(message)
    await AliexpressAPIHandler().handle_links(message)
    await AliexpressHandler().handle_links(message)

    logger.info(f"Finished processing link handlers for message ID: {message.message_id}.")


async def modify_link(update: Update, context) -> None:
    """Modifies Amazon, AliExpress, Awin, and Admitad links in messages."""

    logger.info(f"Received new update (ID: {update.update_id}).")

    if not update.message or not update.message.text:
        logger.info(
            f"{update.update_id}: Update with a message without text. Skipping."
        )
        return

    if not update.effective_user:
        logger.info(f"{update.update_id}: Update without user. Skipping.")
        return

    if is_user_excluded(update.effective_user):
        logger.info(
            f"{update.update_id}: Update with a message from excluded user {update.effective_user.username} (ID: {update.effective_user.id}). Skipping."
        )
        return

    message = update.message

    logger.info(
        f"{update.update_id}: Processing update message (ID: {update.message.message_id})..."
    )

    await process_link_handlers(message)

    logger.info(f"{update.update_id}: Update processed.")


def main() -> None:
    """Start the bot with python-telegram-bot"""

    logger.info("Configuring the bot")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.ALL & filters.ChatType.GROUPS, modify_link)
    )

    logger.info("Starting the bot")
    application.run_polling()


if __name__ == "__main__":
    main()
