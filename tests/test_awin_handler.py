import unittest
from unittest.mock import AsyncMock, patch, ANY
from handlers.awin_handler import handle_awin_links
from config import MSG_REPLY_PROVIDED_BY_USER, MSG_AFFILIATE_LINK_MODIFIED,ALIEXPRESS_DISCOUNT_CODES

class TestHandleAwinLinks(unittest.IsolatedAsyncioTestCase):

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.AWIN_PUBLISHER_ID', None)
    async def test_no_action_when_awin_publisher_id_is_none(self):
        """Test that no action is taken if AWIN_PUBLISHER_ID is None."""
        
        # Simulating a message with an Awin link
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser1"
        
        # Call the function
        result = await handle_awin_links(mock_message)

        # Ensure no actions were taken
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()

        # Ensure the function returns False indicating no action taken
        self.assertFalse(result)

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    @patch('handlers.awin_handler.DELETE_MESSAGES', True)
    async def test_awin_link_delete_message(self, mock_convert):
        """Test Awin links conversion when DELETE_MESSAGES is True. New message must match the original reply structure."""
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Test case: message is a reply to another message
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10  # Simulating it's a reply to message ID 10

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message content
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Assert that the new message is a reply to the original message's 'reply_to_message_id'
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], 10)  # It should reply to message ID 10

        # Assert that the original message was deleted
        mock_message.delete.assert_called_once()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    @patch('handlers.awin_handler.DELETE_MESSAGES', True)
    async def test_awin_link_delete_message_not_a_reply(self, mock_convert):
        """Test Awin links conversion when DELETE_MESSAGES is True, but the message is not a reply."""
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Test case: message is not a reply (reply_to_message is None)
        mock_message.reply_to_message = None

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message content
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Assert that the new message is not a reply (reply_to_message_id should be None)
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertIsNone(actual_call_args['reply_to_message_id'])  # No reply-to when not a reply

        # Assert that the original message was deleted
        mock_message.delete.assert_called_once()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_link_no_delete_message(self, mock_convert):
        """Test Awin links conversion when DELETE_MESSAGES is False. The bot should reply to the original message."""
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Test case: regardless of whether the message is a reply, the bot should reply to it
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message content
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Assert that the new message is a reply to the original message, not the 'reply_to_message'
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)  # It should reply to the original message

        # Assert that the original message was not deleted
        mock_message.delete.assert_not_called()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    @patch('handlers.awin_handler.DELETE_MESSAGES', True)
    async def test_awin_link_delete_message_is_reply(self, mock_convert):
        """Test Awin link conversion when DELETE_MESSAGES is True and the original message is a reply to another message."""
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Simulate that the original message is a reply to another message (with message_id 100)
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 100

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Check this out: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=valid_publisher_id&ued=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message is a reply to the same message that the original was replying to
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], 100)

        # Verify that the original message was deleted
        mock_message.delete.assert_called_once()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.AWIN_PUBLISHER_ID', "my_awin")
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_affiliate_link_from_list(self):
        """Test if an existing Awin affiliate link is modified when the store is in our list of Awin advertisers."""
        # Simulate that the link is already an Awin affiliate link

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=old_affiliate_id&ued=https://www.pccomponentes.com/some-product"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser3:\n\n"
            "Here is a product: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=my_awin&ued=https://www.pccomponentes.com/some-product\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message replies to the original message
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)

        # Verify that the original message was not deleted because DELETE_MESSAGES is False
        mock_message.delete.assert_not_called()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})
    @patch('handlers.awin_handler.AWIN_PUBLISHER_ID', "my_awin")
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_affiliate_link_not_in_list(self):
        """Test that an existing Awin affiliate link is NOT modified when the store is NOT in our list of Awin advertisers."""
        # The link should not be modified because the store is not in our list

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.awin1.com/cread.php?awinmid=nonexistent&awinaffid=old_affiliate_id&ued=https://www.unknownstore.com/product"
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        # Call the function
        await handle_awin_links(mock_message)

        # Verify that the message was not modified and the bot did not reply
        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'aliexpress.com': '11640'})
    @patch('handlers.awin_handler.AWIN_PUBLISHER_ID', "my_awin")
    @patch('handlers.awin_handler.DELETE_MESSAGES', True)
    @patch('handlers.awin_handler.expand_aliexpress_short_link')
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    async def test_awin_short_aliexpress_link_with_discount(self, mock_convert, mock_expand):
        """Test short AliExpress link in Awin list, adding discount codes when applicable."""
        # Mock the expansion and conversion of the short link
        mock_expand.return_value = "https://www.aliexpress.com/item/1005002958205071.html"
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin&ued=https://www.aliexpress.com/item/1005002958205071.html"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://s.click.aliexpress.com/e/_shortLink"
        mock_message.message_id = 5
        mock_message.from_user.username = "testuser"
        # Test case: message is not a reply (reply_to_message is None)
        mock_message.reply_to_message = None

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser:\n\n"
            "Check this out: https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin&ued=https://www.aliexpress.com/item/1005002958205071.html\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message includes the discount codes
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertIsNone(actual_call_args['reply_to_message_id'])  # No reply-to when not a reply

        # Verify that the original message was deleted
        mock_message.delete.assert_called_once()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'aliexpress.com': '11640'})
    @patch('handlers.awin_handler.convert_to_awin_affiliate_link')
    @patch('handlers.awin_handler.AWIN_PUBLISHER_ID', "my_awin")
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_long_aliexpress_link_with_discount(self, mock_convert):
        """Test long AliExpress link in Awin list, adding discount codes when applicable."""
        # Mock the conversion of the long link
        mock_convert.return_value = "https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin&ued=https://www.aliexpress.com/item/1005002958205071.html"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        # Test case: message is not a reply (reply_to_message is None)
        mock_message.reply_to_message = None

        # Call the function
        await handle_awin_links(mock_message)

        # Expected message with discount codes appended
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Here is a product: https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin&ued=https://www.aliexpress.com/item/1005002958205071.html\n\n"
            f"{ALIEXPRESS_DISCOUNT_CODES}\n\n{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Verify that the new message does not reply to any other message
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        self.assertEqual(actual_call_args['reply_to_message_id'], mock_message.message_id)

        # Verify that the original message was not deleted because DELETE_MESSAGES is False
        mock_message.delete.assert_not_called()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {'pccomponentes.com': '20982'})  # with elements configured (no Aliexpress)
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_aliexpress_link_no_awin_config(self):
        """Test AliExpress link when AliExpress is NOT in the Awin list and discount codes should NOT be added."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Call the function
        await handle_awin_links(mock_message)

        # Verify that no message was modified or sent
        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()

    @patch('handlers.awin_handler.AWIN_ADVERTISERS', {})  # no elements configured
    @patch('handlers.awin_handler.DELETE_MESSAGES', False)
    async def test_awin_aliexpress_link_awin_config_empty_list(self):
        """Test AliExpress link when AliExpress is NOT in the Awin list and discount codes should NOT be added."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        # Call the function
        await handle_awin_links(mock_message)

        # Verify that no message was modified or sent
        mock_message.chat.send_message.assert_not_called()
        mock_message.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()
