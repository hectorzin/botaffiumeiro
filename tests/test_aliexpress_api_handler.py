import unittest
from unittest.mock import AsyncMock, patch, ANY
from handlers.base_handler import BaseHandler
from handlers.aliexpress_api_handler import AliexpressAPIHandler
from config import MSG_REPLY_PROVIDED_BY_USER, MSG_AFFILIATE_LINK_MODIFIED, ALIEXPRESS_DISCOUNT_CODES


class TestHandler(BaseHandler):
    def handle_links(self, message):
        pass

class TestHandleAliExpressAPILinks(unittest.IsolatedAsyncioTestCase):


    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', None)
    async def test_aliexpress_no_app_key(self):
        """Test if no action is taken when ALIEXPRESS_APP_KEY is empty."""
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_someShortLink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        result = await AliexpressAPIHandler().handle_links(mock_message)

        # Ensure no action is taken when ALIEXPRESS_APP_KEY is empty
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    async def test_no_aliexpress_link(self):
        """Test that no action is taken if there are no AliExpress links in the message."""
        
        mock_message = AsyncMock()
        mock_message.text = "This is a random message with no AliExpress links."
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        result = await AliexpressAPIHandler().handle_links(mock_message)

        # Ensure no actions are taken
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_DISCOUNT_CODES', "Here is your discount code!")
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.base_handler.BaseHandler._expand_shortened_url_from_list')
    @patch('handlers.aliexpress_api_handler.AliexpressAPIHandler._convert_to_aliexpress_affiliate')
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_long_aliexpress_link_without_affiliate(self,  mock_process, mock_convert, mock_expand):
        """Test if long AliExpress links without affiliate ID are converted."""
        
        # No need to expand long links
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        # Call the function being tested
        await AliexpressAPIHandler().handle_links(mock_message)

        expected_message = (
            "Here is a product: https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21\n\n"
            "Here is your discount code!"
        )

        mock_process.assert_called_with(mock_message, expected_message)

    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_DISCOUNT_CODES', "Here is your discount code!")
    @patch('handlers.aliexpress_api_handler.ALIEXPRESS_APP_KEY', 'some_app_key')
    @patch('handlers.base_handler.BaseHandler._expand_shortened_url_from_list')
    @patch('handlers.aliexpress_api_handler.AliexpressAPIHandler._convert_to_aliexpress_affiliate')
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_short_aliexpress_link(self, mock_process, mock_convert, mock_expand):
        """Test if short AliExpress links are expanded, converted to affiliate links, and original message is deleted when DELETE_MESSAGES is True."""
        
        # Mock the expansion and conversion functions
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21"
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_someShortLink I hope you like it!"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        result = await AliexpressAPIHandler().handle_links(mock_message)

        # Ensure the short link was expanded and converted
        mock_expand.assert_called_with("https://s.click.aliexpress.com/e/_someShortLink",["s.click.aliexpress.com"])
        mock_convert.assert_called_with("https://www.aliexpress.com/item/1005002958205071.html")
        
        expected_message = (
            "Check this out: https://www.aliexpress.com/item/1005002958205071.html?aff_id=affiliate_21 I hope you like it!\n\n"
            "Here is your discount code!"
        )

        mock_process.assert_called_with(mock_message, expected_message)


if __name__ == '__main__':
    unittest.main()
