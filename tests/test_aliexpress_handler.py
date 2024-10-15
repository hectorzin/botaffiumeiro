import unittest
from unittest.mock import AsyncMock, patch
from handlers.base_handler import BaseHandler
from handlers.aliexpress_handler import AliexpressHandler
from config import ALIEXPRESS_DISCOUNT_CODES

class TestHandler(BaseHandler):
    def handle_links(self, message):
        pass

class TestHandleAliExpressLinks(unittest.IsolatedAsyncioTestCase):

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '💥 AliExpress discount codes: 💰 5% off!')
    @patch('handlers.aliexpress_handler.AWIN_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ADMITAD_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ALIEXPRESS_APP_KEY', "")
    async def test_aliexpress_links_without_affiliate(self):
        """Test AliExpress links when they are not in the advertiser list and APP_KEY is empty."""
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        result = await AliexpressHandler().handle_links(mock_message)

        # Check that the message with discount codes is sent
        mock_message.chat.send_message.assert_called_once_with(
            '💥 AliExpress discount codes: 💰 5% off!',
            reply_to_message_id=mock_message.message_id
        )

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '💥 AliExpress discount codes: 💰 5% off!')
    @patch('handlers.aliexpress_handler.AWIN_ADVERTISERS', {'aliexpress.com': 'some_id'})
    @patch('handlers.aliexpress_handler.ADMITAD_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ALIEXPRESS_APP_KEY', "")
    async def test_aliexpress_in_awin_advertisers(self):
        """Test that no action is taken when AliExpress is in the Awin advertisers list."""
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        result = await AliexpressHandler().handle_links(mock_message)

        # Ensure no message is sent and the function returns False
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '💥 AliExpress discount codes: 💰 5% off!')
    @patch('handlers.aliexpress_handler.AWIN_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ADMITAD_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ALIEXPRESS_APP_KEY', "some_app_key")
    async def test_aliexpress_with_app_key(self):
        """Test that no action is taken when AliExpress APP_KEY is configured."""
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        result = await AliexpressHandler().handle_links(mock_message)

        # Ensure no message is sent and the function returns False
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '💥 AliExpress discount codes: 💰 5% off!')
    @patch('handlers.aliexpress_handler.AWIN_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ADMITAD_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ALIEXPRESS_APP_KEY', "")
    async def test_aliexpress_short_link(self):
        """Test AliExpress short links and check that the short link is expanded."""
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_shortLink"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        result = await AliexpressHandler().handle_links(mock_message)

        # Ensure message is sent with discount codes
        mock_message.chat.send_message.assert_called_once_with(
            '💥 AliExpress discount codes: 💰 5% off!',
            reply_to_message_id=mock_message.message_id
        )

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '')
    @patch('handlers.aliexpress_handler.AWIN_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ADMITAD_ADVERTISERS', {})
    @patch('handlers.aliexpress_handler.ALIEXPRESS_APP_KEY', "")
    async def test_no_discount_codes(self):
        """Test that no action is taken when ALIEXPRESS_DISCOUNT_CODES is empty."""
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        result = await AliexpressHandler().handle_links(mock_message)

        # Ensure no message is sent and the function returns True
        mock_message.chat.send_message.assert_not_called()
        self.assertTrue(result)

    @patch('handlers.aliexpress_handler.ALIEXPRESS_DISCOUNT_CODES', '💥 AliExpress discount codes: 💰 5% off!')
    async def test_no_aliexpress_links(self):
        """Test that no action is taken when no AliExpress links are present in the message."""
        mock_message = AsyncMock()
        mock_message.text = "This is a random message without AliExpress links."
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        result = await AliexpressHandler().handle_links(mock_message)

        # Ensure no message is sent and the function returns False
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
