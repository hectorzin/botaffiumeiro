import unittest
from unittest.mock import AsyncMock, patch, ANY
from handlers.admitad_handler import handle_admitad_links
from config import MSG_REPLY_PROVIDED_BY_USER, MSG_AFFILIATE_LINK_MODIFIED, ALIEXPRESS_DISCOUNT_CODES

class TestHandleAdmitadLinks(unittest.IsolatedAsyncioTestCase):

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.ADMITAD_PUBLISHER_ID', None)
    async def test_no_action_when_admitad_publisher_id_is_none(self):
        """Test that no action is taken if ADMITAD_PUBLISHER_ID is None."""
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser1"
        
        result = await handle_admitad_links(mock_message)

        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()

        self.assertFalse(result)

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.convert_to_admitad_affiliate_link')
    @patch('handlers.admitad_handler.DELETE_MESSAGES', True)
    async def test_admitad_link_delete_message(self, mock_convert):
        """Test Admitad links conversion when DELETE_MESSAGES is True. New message must match the original reply structure."""
        mock_convert.return_value = "https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10

        await handle_admitad_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], 10)

        mock_message.delete.assert_called_once()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.convert_to_admitad_affiliate_link')
    @patch('handlers.admitad_handler.DELETE_MESSAGES', True)
    async def test_admitad_link_delete_message_not_a_reply(self, mock_convert):
        """Test Admitad links conversion when DELETE_MESSAGES is True, but the message is not a reply."""
        mock_convert.return_value = "https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        mock_message.reply_to_message = None

        await handle_admitad_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertIsNone(actual_call_args['reply_to_message_id'])

        mock_message.delete.assert_called_once()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.convert_to_admitad_affiliate_link')
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_link_no_delete_message(self, mock_convert):
        """Test Admitad links conversion when DELETE_MESSAGES is False. The bot should reply to the original message."""
        mock_convert.return_value = "https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10

        await handle_admitad_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://ad.admitad.com/g/20982/?ulp=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)

        mock_message.delete.assert_not_called()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.ADMITAD_PUBLISHER_ID', "my_admitad")
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_affiliate_link_from_list(self):
        """Test if an existing Admitad affiliate link is modified when the store is in our list of Admitad advertisers."""
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://ad.admitad.com/g/20982/old_affiliate/?ulp=https://www.pccomponentes.com/some-product"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        await handle_admitad_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser3:\n\n"
            "Here is a product: https://ad.admitad.com/g/20982/my_admitad/?ulp=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)

        mock_message.delete.assert_not_called()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.admitad_handler.ADMITAD_PUBLISHER_ID', "my_admitad")
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_affiliate_link_not_in_list(self):
        """Test that an existing Admitad affiliate link is NOT modified when the store is NOT in our list of Admitad advertisers."""
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://ad.admitad.com/g/nonexistent/?ulp=https://www.unknownstore.com/product"
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        await handle_admitad_links(mock_message)

        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'aliexpress.com': '11640'})
    @patch('handlers.admitad_handler.ADMITAD_PUBLISHER_ID', "my_admitad")
    @patch('handlers.admitad_handler.DELETE_MESSAGES', True)
    @patch('handlers.admitad_handler.expand_aliexpress_short_link')
    @patch('handlers.admitad_handler.convert_to_admitad_affiliate_link')
    async def test_admitad_short_aliexpress_link_with_discount(self, mock_convert, mock_expand):
        """Test short AliExpress link in Admitad list, adding discount codes when applicable."""
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://ad.admitad.com/g/11640/my_admitad/?ulp=https://www.aliexpress.com/item/1005002958205071.html"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_shortLink"
        mock_message.message_id = 5
        mock_message.from_user.username = "testuser"
        mock_message.reply_to_message = None

        await handle_admitad_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser:\n\n"
            "Check this out: https://ad.admitad.com/g/11640/my_admitad/?ulp=https://www.aliexpress.com/item/1005002958205071.html\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message includes the discount codes
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertIsNone(actual_call_args['reply_to_message_id'])  # No reply-to when not a reply

        # Verify that the original message was deleted
        mock_message.delete.assert_called_once()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'aliexpress.com': '11640'})
    @patch('handlers.admitad_handler.convert_to_admitad_affiliate_link')
    @patch('handlers.admitad_handler.ADMITAD_PUBLISHER_ID', "my_admitad")
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_long_aliexpress_link_with_discount(self, mock_convert):
        """Test long AliExpress link in Admitad list, adding discount codes when applicable."""
        # Mock the conversion of the long link
        mock_convert.return_value = "https://ad.admitad.com/g/11640/my_admitad/?ulp=https://www.aliexpress.com/item/1005002958205071.html"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        # Test case: message is not a reply (reply_to_message is None)
        mock_message.reply_to_message = None

        # Call the function
        await handle_admitad_links(mock_message)

        # Expected message with discount codes appended
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Here is a product: https://ad.admitad.com/g/11640/my_admitad/?ulp=https://www.aliexpress.com/item/1005002958205071.html\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message does not reply to any other message
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)

        # Verify that the original message was not deleted because DELETE_MESSAGES is False
        mock_message.delete.assert_not_called()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {'pccomponentes.com': '20982'})  # with elements configured (no Aliexpress)
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_aliexpress_link_no_admitad_config(self):
        """Test AliExpress link when AliExpress is NOT in the Admitad list and discount codes should NOT be added."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Call the function
        await handle_admitad_links(mock_message)

        # Verify that no message was modified or sent
        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()

    @patch('handlers.admitad_handler.ADMITAD_ADVERTISERS', {})  # no elements configured
    @patch('handlers.admitad_handler.DELETE_MESSAGES', False)
    async def test_admitad_aliexpress_link_admitad_config_empty_list(self):
        """Test AliExpress link when AliExpress is NOT in the Admitad list and discount codes should NOT be added."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Call the function
        await handle_admitad_links(mock_message)

        # Verify that no message was modified or sent
        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()
