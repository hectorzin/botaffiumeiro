import unittest

from unittest.mock import AsyncMock, patch

from handlers.base_handler import BaseHandler
from handlers.aliexpress_handler import AliexpressHandler


class TestHandleAliExpressLinks(unittest.IsolatedAsyncioTestCase):

    async def test_aliexpress_links_without_affiliate(self):
        """Test AliExpress links when they are not in the advertiser list and APP_KEY is empty."""

        mock_message = AsyncMock()
        mock_message.text = (
            "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        )
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        handler = AliexpressHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "aliexpress": {
                    "discount_codes": "💥 AliExpress discount codes: 💰 5% off!",
                    "app_key": "",
                    "app_secret": None,
                    "tracking_id": None,
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        # Check that the message with discount codes is sent
        mock_message.chat.send_message.assert_called_once_with(
            "💥 AliExpress discount codes: 💰 5% off!",
            reply_to_message_id=mock_message.message_id,
        )

    async def test_no_discount_codes(self):
        """Test that no action is taken when ALIEXPRESS_DISCOUNT_CODES is empty."""

        mock_message = AsyncMock()
        mock_message.text = (
            "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        )
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        handler = AliexpressHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "discount_codes": "",
                "app_key": "",
                "app_secret": None,
                "tracking_id": None,
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        # Ensure no message is sent and the function returns True
        mock_message.chat.send_message.assert_not_called()
        self.assertTrue(result)

    async def test_no_aliexpress_links(self):
        """Test that no action is taken when no AliExpress links are present in the message."""

        mock_message = AsyncMock()
        mock_message.text = "This is a random message without AliExpress links."
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        handler = AliexpressHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "aliexpress": {
                    "discount_codes": "💥 AliExpress discount codes: 💰 5% off!",
                    "app_key": "",
                    "app_secret": None,
                    "tracking_id": None,
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        # Ensure no message is sent and the function returns False
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
