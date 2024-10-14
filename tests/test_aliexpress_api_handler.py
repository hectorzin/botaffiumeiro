import unittest
from unittest.mock import AsyncMock, patch, ANY
from handlers.aliexpress_api_handler import handle_aliexpress_api_links
from config import MSG_REPLY_PROVIDED_BY_USER, MSG_AFFILIATE_LINK_MODIFIED, ALIEXPRESS_DISCOUNT_CODES

class TestHandleAliExpressLinks(unittest.IsolatedAsyncioTestCase):

    @patch('handlers.aliexpress_api_handler.DELETE_MESSAGES', True)
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.aliexpress_api_handler.expand_aliexpress_short_link')
    @patch('handlers.aliexpress_api_handler.convert_to_aliexpress_affiliate')
    async def test_short_aliexpress_link_delete_message(self, mock_convert, mock_expand):
        """Test if short AliExpress links are expanded, converted to affiliate links, and original message is deleted when DELETE_MESSAGES is True."""
        
        # Mock the expansion and conversion functions
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_someShortLink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        # Call the function being tested
        await handle_aliexpress_api_links(mock_message)

        # Ensure the short link was expanded and converted
        mock_expand.assert_called_with("https://s.click.aliexpress.com/e/_someShortLink")
        mock_convert.assert_called_with("https://www.aliexpress.com/item/1005002958205071.html")
        
        # Ensure the message is deleted and a new one is sent
        mock_message.delete.assert_called_once()
        mock_message.chat.send_message.assert_called_once()

    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', None)
    async def test_aliexpress_no_app_key(self):
        """Test if no action is taken when ALIEXPRESS_APP_KEY is empty."""
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_someShortLink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        # Call the function being tested
        result = await handle_aliexpress_api_links(mock_message)

        # Ensure no action is taken when ALIEXPRESS_APP_KEY is empty
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    async def test_no_aliexpress_link(self):
        """Test that no action is taken if there are no AliExpress links in the message."""
        
        mock_message = AsyncMock()
        mock_message.text = "This is a random message with no AliExpress links."
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        # Call the function being tested
        result = await handle_aliexpress_api_links(mock_message)

        # Ensure no actions are taken
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_api_handler.DELETE_MESSAGES', False)
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.aliexpress_api_handler.expand_aliexpress_short_link')
    @patch('handlers.aliexpress_api_handler.convert_to_aliexpress_affiliate')
    async def test_short_aliexpress_link_no_delete_message(self, mock_convert, mock_expand):
        """Test if short AliExpress links are expanded, converted to affiliate links, and original message is kept when DELETE_MESSAGES is False."""
        
        # Mock the expansion and conversion functions
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_someShortLink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        # Call the function being tested
        await handle_aliexpress_api_links(mock_message)

        # Ensure the short link was expanded and converted
        mock_expand.assert_called_with("https://s.click.aliexpress.com/e/_someShortLink")
        mock_convert.assert_called_with("https://www.aliexpress.com/item/1005002958205071.html")
        
        # Ensure the message is not deleted and a reply is sent
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_called_once()
        mock_message.chat.send_message.assert_called_with(
            text=ANY, reply_to_message_id=mock_message.message_id  # Replying instead of deleting
        )

    @patch('handlers.aliexpress_api_handler.DELETE_MESSAGES', True)
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.aliexpress_api_handler.convert_to_aliexpress_affiliate')
    async def test_long_aliexpress_link_without_affiliate_delete_message(self, mock_convert):
        """Test if long AliExpress links without affiliate ID are converted and original message is deleted when DELETE_MESSAGES is True."""
        
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        await handle_aliexpress_api_links(mock_message)

        # Construct the expected message with proper ordering and structure
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}\n\n"
            "Here is a product: https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}"
        )

        # Extract the actual call arguments to compare
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_called_once()

    @patch('handlers.aliexpress_api_handler.DELETE_MESSAGES', False)
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.aliexpress_api_handler.convert_to_aliexpress_affiliate')
    async def test_long_aliexpress_link_without_affiliate_no_delete(self, mock_convert):
        """Test long AliExpress link without affiliate ID and without message deletion."""
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        await handle_aliexpress_api_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}\n\n"
            "Here is a product: https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_not_called()

if __name__ == '__main__':
    unittest.main()
