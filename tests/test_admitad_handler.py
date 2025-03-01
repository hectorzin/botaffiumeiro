"""Tests for Admitad handler in PatternHandler."""

from typing import Any
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from config import ConfigurationManager
from handlers.base_handler import BaseHandler
from handlers.pattern_handler import PatternHandler


class TestHandler(BaseHandler):
    """Dummy handler for testing."""

    async def handle_links(self, _: Any) -> bool:
        """Stub method for handling links."""
        return False


class TestHandleAdmitadLinks(unittest.IsolatedAsyncioTestCase):
    """Tests for handling Admitad links in PatternHandler."""

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_aliexpress_link_admitad_config_empty_list(
        self, mock_process: AsyncMock
    ) -> None:
        """Test AliExpress link when AliExpress is NOT in the Admitad list and discount codes should NOT be added."""
        mock_selected_users = {
            "admitad": {"publisher_id": "my_admitad_id", "advertisers": {}}
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        # Verify that no message was modified or sent
        mock_message.chat.send_message.assert_not_called()
        self.assertEqual(context["modified_message"], mock_message.text)
        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_link_in_list(self, mock_process: AsyncMock) -> None:
        """Test Admitad link conversion when in the list."""
        mock_selected_users: dict = {
            "giftmio.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"giftmio.com": "93fd4vbk6c873a1e3014d68450d763"},
                }
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = (
            "Check this out: https://www.giftmio.com/some-product I hope you like it"
        )
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10
        context: dict = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        expected_message = "Check this out: https://wextap.com/g/93fd4vbk6c873a1e3014d68450d763/?ulp=https://www.giftmio.com/some-product I hope you like it"

        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_affiliate_link_from_list(
        self, mock_process: AsyncMock
    ) -> None:
        """Test if an existing Admitad affiliate link is modified when the store is in our list of Admitad advertisers."""
        mock_selected_users: dict = {
            "giftmio.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"giftmio.com": "93fd4vbk6c873a1e3014d68450d763"},
                }
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://wextap.com/g/other_id_not_mine/?ulp=https://www.giftmio.com/some-product I hope you like it"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"
        mock_message.reply_to_message.message_id = 10
        context: dict = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        expected_message = "Here is a product: https://wextap.com/g/93fd4vbk6c873a1e3014d68450d763/?ulp=https://www.giftmio.com/some-product I hope you like it"
        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_affiliate_link_not_in_list(
        self, mock_process: AsyncMock
    ) -> None:
        """Test that an existing Admitad affiliate link is NOT modified when the store is NOT in our list of Admitad advertisers."""
        mock_selected_users = {
            "giftmio.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"giftmio.com": "93fd4vbk6c873a1e3014d68450d763"},
                }
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://wextap.com/g/other_id_not_mine/?ulp=https://www.unknownstore.com/product I hope you like it"
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_aliexpress_link_without_discount(
        self, mock_process: AsyncMock
    ) -> None:
        """Test AliExpress link in Admitad list, no discount code added."""
        mock_selected_users = {
            "aliexpress.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"aliexpress.com": "11640"},
                }
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 5
        mock_message.from_user.username = "testuser"
        mock_message.reply_to_message = None
        expected_message = "Check this out: https://wextap.com/g/11640/?ulp=https://www.aliexpress.com/item/1005002958205071.html I hope you like it"

        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_aliexpress_link_with_discount(
        self, mock_process: AsyncMock
    ) -> None:
        """Test AliExpress link in Admitad list, adding discount codes when applicable."""
        mock_selected_users = {
            "aliexpress.com": {
                "admitad": {
                    "publisher_id": "my_admitad",
                    "advertisers": {"aliexpress.com": "11640"},
                },
                "aliexpress": {"discount_codes": "Here is your discount code!"},
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        mock_message.reply_to_message = None

        # Expected message with discount codes appended
        expected_message = (
            "Here is a product: https://wextap.com/g/11640/?ulp=https://www.aliexpress.com/item/1005002958205071.html I hope you like it\n\n"
            "Here is your discount code!"
        )

        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_aliexpress_link_no_admitad_config(
        self, mock_process: AsyncMock
    ) -> None:
        """Test AliExpress link when AliExpress is NOT in the Admitad list and discount codes should NOT be added."""
        mock_selected_users = {
            "aliexpress.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"giftmio.com": "93fd4vbk6c873a1e3014d68450d763"},
                }
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_admitad_no_aliexpress_from_link_with_discount(
        self, mock_process: AsyncMock
    ) -> None:
        """Test No AliExpress link in Admitad list, the discount should not be applied."""
        mock_selected_users = {
            "pccomponentes.com": {
                "admitad": {
                    "publisher_id": "my_admitad_id",
                    "advertisers": {"pccomponentes.com": "11640"},
                },
                "aliexpress": {"discount_codes": "Here is your discount code!"},
            }
        }
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        admitad_handler = PatternHandler(mock_config_manager)
        admitad_handler.selected_users = mock_selected_users

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.pccomponentes.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        mock_message.reply_to_message = None

        expected_message = "Here is a product: https://wextap.com/g/11640/?ulp=https://www.pccomponentes.com/item/1005002958205071.html I hope you like it"

        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await admitad_handler.handle_links(context)

        mock_process.assert_called_with(mock_message, expected_message)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
