import unittest
import re

from unittest.mock import AsyncMock, patch

from handlers.base_handler import BaseHandler
from handlers.pattern_handler import PatternHandler


class TestHandler(BaseHandler):
    def handle_links(self, _):
        pass


class TestHandleAmazonLinks(unittest.IsolatedAsyncioTestCase):
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_no_amazon_link(self, mock_process):
        """Test that no action is taken if there are no Amazon links in the message."""
        mock_selected_users = {
            "amazon.es": {"amazon": {"affiliate_id": "our_affiliate_id"}}
        }
        amazon_handler = PatternHandler()

        mock_message = AsyncMock()
        mock_message.text = "This is a random message without Amazon links."
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"
        amazon_handler.selected_users = mock_selected_users
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await amazon_handler.handle_links(context)

        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_no_action_when_amazon_affiliate_id_is_none(self, mock_process):
        """Test that no action is taken if AMAZON_AFFILIATE_ID is None."""
        mock_selected_users = {"amazon.es": {"amazon": {"affiliate_id": None}}}
        amazon_handler = PatternHandler()

        mock_message = AsyncMock()
        mock_message.text = (
            "Check out this product: https://www.amazon.es/dp/B08N5WRWNW"
        )
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await amazon_handler.handle_links(context)

        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        mock_process.assert_not_called()
        self.assertFalse(result)

    @patch("botaffiumeiro.expand_shortened_url")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_long_amazon_link_without_affiliate(self, mock_process, mock_expand):
        """Test if long Amazon links without affiliate ID are converted to include the affiliate ID."""
        mock_selected_users = {
            "amazon.com": {
                "amazon": {
                    "advertisers": {
                        "amazon.com": "com_affiliate_id",
                        "amazon.es": "es_affiliate_id",
                    }
                }
            }
        }
        amazon_handler = PatternHandler()

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await amazon_handler.handle_links(context)

        mock_expand.assert_not_called()
        mock_process.assert_called_with(
            mock_message,
            "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=com_affiliate_id",
        )
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_amazon_link_with_affiliate(self, mock_process):
        """Test if Amazon links with an existing affiliate ID are modified to use ours."""
        mock_selected_users = {
            "amazon.com": {
                "amazon": {"advertisers": {"amazon.com": "our_affiliate_id"}}
            }
        }
        amazon_handler = PatternHandler()

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=another_affiliate"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await amazon_handler.handle_links(context)

        mock_process.assert_called_with(
            mock_message,
            "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id",
        )
        self.assertTrue(result)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_explicit_amazon_link_conversion(self, mock_process):
        """Test explicit case where a shortened Amazon link is expanded and the correct affiliate ID is added."""
        mock_selected_users = {
            "amazon.es": {"amazon": {"advertisers": {"amazon.es": "our_affiliate_id"}}}
        }
        amazon_handler = PatternHandler()

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.amazon.es/dp/B01M9ATDY7?ref=cm_sw_r_apan_dp_ZYAS38F4N8NR5FHPH886&ref_=cm_sw_r_apan_dp_ZYAS38F4N8NR5FHPH886&social_share=cm_sw_r_apan_dp_ZYAS38F4N8NR5FHPH886&starsLeft=1&skipTwisterOG=1"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }

        result = await amazon_handler.handle_links(context)

        actual_call_args = mock_process.call_args[0][1]
        expected_pattern = r"Check this out: https://www\.amazon\.es(?:/[\w\-]*)?/dp/B01M9ATDY7\?tag=our_affiliate_id"
        self.assertTrue(
            re.match(expected_pattern, actual_call_args),
            f"URL '{actual_call_args}' does not match the expected pattern",
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
