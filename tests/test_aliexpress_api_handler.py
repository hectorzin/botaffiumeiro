import unittest

from unittest.mock import AsyncMock, patch

from handlers.base_handler import BaseHandler
from handlers.aliexpress_api_handler import AliexpressAPIHandler


class TestHandler(BaseHandler):
    def handle_links(self, _):
        pass


class TestHandleAliExpressAPILinks(unittest.IsolatedAsyncioTestCase):
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_aliexpress_no_app_key(self, mock_process):
        """Test: No action is taken if AliExpress app_key is empty in selected_users."""

        # Mock selected_users without AliExpress app_key
        mock_selected_users = {"aliexpress": {"app_key": None}}
        aliexpress_handler = AliexpressAPIHandler()

        mock_message = AsyncMock()
        mock_message.text = (
            "Check this out: https://s.click.aliexpress.com/e/_someShortLink"
        )
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await aliexpress_handler.handle_links(context)

        # Ensure no action is taken when the app_key is empty
        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_no_aliexpress_link(self, mock_process):
        """Test: No action is taken if there are no AliExpress links in the message."""

        mock_selected_users = {"aliexpress": {"app_key": "some_app_key"}}
        aliexpress_handler = AliexpressAPIHandler()

        mock_message = AsyncMock()
        mock_message.text = "This is a random message with no AliExpress links."
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await aliexpress_handler.handle_links(context)

        # Ensure no actions are taken
        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._expand_shortened_url_from_list")
    @patch(
        "handlers.aliexpress_api_handler.AliexpressAPIHandler._convert_to_aliexpress_affiliate"
    )
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_long_aliexpress_link(self, mock_process, mock_convert, mock_expand):
        """Test: Long AliExpress links."""

        aliexpress_handler = AliexpressAPIHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "aliexpress": {
                    "app_key": "some_app_key",
                    "discount_codes": "Here is your discount code!",
                }
            }
        }

        # No need to expand long links
        mock_expand.return_value = (
            "https://www.aliexpress.com/item/1005002958205071.html"
        )
        mock_convert.return_value = (
            "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        )

        mock_message = AsyncMock()
        mock_message.text = (
            "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        )
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await aliexpress_handler.handle_links(context)

        expected_message = (
            "Here is a product: https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21\n\n"
            "Here is your discount code!"
        )

        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
