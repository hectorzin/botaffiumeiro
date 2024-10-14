import unittest
from unittest.mock import AsyncMock,patch
from urllib.parse import unquote
from handlers.base_handler import BaseHandler 
from config import (
    MSG_AFFILIATE_LINK_MODIFIED,
    MSG_REPLY_PROVIDED_BY_USER,
)

class TestHandler(BaseHandler):
    def handle_links(self, message):
        pass  # This method is not relevant for the test of generate_affiliate_url

class TestGenerateAffiliateUrl(unittest.TestCase):

    def setUp(self):
        """Set up the TestHandler instance."""
        self.handler = TestHandler()  # Create an instance of the concrete subclass

    def test_amazon_affiliate_url(self):
        """Test Amazon affiliate link generation with a simple format."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21"
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_admitad_affiliate_url_with_store_id(self):
        """Test Admitad affiliate link generation with store ID and affiliate ID."""
        original_url = "https://www.some-admitad-store.com/product"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}?store_id=12345&{affiliate_tag}={affiliate_id}",
            affiliate_tag="aff_id",
            affiliate_id="admitad-21"
        )
        expected_url = "https://www.some-admitad-store.com?store_id=12345&aff_id=admitad-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_existing_affiliate_tag_overwrite(self):
        """Test overwriting an existing affiliate tag in the URL."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=old-affiliate"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="new-affiliate"
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=new-affiliate"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template(self):
        """Test that the query string is appended properly if the template does not include the affiliate tag placeholders."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21"
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_empty_query(self):
        """Test URL without query parameters should add affiliate tag."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21"
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_complex_path(self):
        """Test URL with complex path (multiple slashes and query params) should generate correctly."""
        original_url = "https://www.example.com/store/sub-store/product/12345?color=red"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="aff_id",
            affiliate_id="affiliate-99"
        )
        expected_url = "https://www.example.com/store/sub-store/product/12345?aff_id=affiliate-99"
        self.assertEqual(unquote(affiliate_url), expected_url)

    def test_affiliate_in_path(self):
        """Test affiliate ID being inserted into a path before the query string."""
        original_url = "https://www.example.com/product/12345"
        affiliate_url = self.handler.generate_affiliate_url(
            original_url,
            format_template="{domain}/{affiliate_tag}/{affiliate_id}{path_before_query}",
            affiliate_tag="aff_id",
            affiliate_id="my_affiliate"
        )
        expected_url = "https://www.example.com/aff_id/my_affiliate/product/12345"
        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_url_with_full_url(self):
        """Test affiliate URL generation with the full original URL in the format (like Awin or Admitad)."""
        original_url = "https://www.example.com/product/12345"
        format_template = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid={affiliate_id}&ued={full_url}"
        affiliate_tag = "awinaffid"
        affiliate_id = "affiliate-21"

        expected_url = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid=affiliate-21&ued=https://www.example.com/product/12345"

        affiliate_url = self.handler.generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_tag=affiliate_tag,
            affiliate_id=affiliate_id,
        )

        self.assertEqual(affiliate_url, expected_url)

class TestProcessMessage(unittest.TestCase):

    def setUp(self):
        """Set up the TestHandler instance."""
        self.handler = TestHandler()  # Create an instance of the concrete subclass

    @patch('config.DELETE_MESSAGES', True)
    async def test_send_message_and_delete_original(self):
        """Test when DELETE_MESSAGES is True, the original message should be deleted and a new one sent."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"
        
        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that a new message was sent
        mock_message.chat.send_message.assert_called_once_with(text=expected_message)

    @patch('config.DELETE_MESSAGES', False)
    async def test_send_message_without_delete(self):
        """Test when DELETE_MESSAGES is False, the original message should not be deleted, and the bot replies to it."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"
        
        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, 
            reply_to_message_id=mock_message.message_id
        )

    @patch('config.DELETE_MESSAGES', True)
    async def test_send_message_is_reply_and_delete(self):
        """Test when DELETE_MESSAGES is True, and the original message is a reply to another message."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"
        
        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message replies to the same message the original one was replying to
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, 
            reply_to_message_id=mock_message.reply_to_message.message_id
        )

    @patch('config.DELETE_MESSAGES', False)
    async def test_send_message_is_reply_without_delete(self):
        """Test when DELETE_MESSAGES is False, and the original message is a reply to another message."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"
        
        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the new message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, 
            reply_to_message_id=mock_message.message_id
        )

    @patch('config.DELETE_MESSAGES', True)
    async def test_send_message_without_username(self):
        """Test when the user has no username, use the first name instead."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = None
        mock_message.message_id = 102
        mock_message.text = "Original message"
        mock_message.reply_to_message = None  # Not replying to any message

        new_text = "This is the modified affiliate message"
        
        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @Jane:\n\n"
            f"{new_text}\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message is sent without replying
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message
        )

if __name__ == '__main__':
    unittest.main()
