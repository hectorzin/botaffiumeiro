import unittest
from unittest.mock import AsyncMock, patch, ANY
from handlers.amazon_handler import handle_amazon_links
from config import MSG_REPLY_PROVIDED_BY_USER, MSG_AFFILIATE_LINK_MODIFIED

class TestHandleAmazonLinks(unittest.IsolatedAsyncioTestCase):

    @patch('handlers.amazon_handler.DELETE_MESSAGES', True)
    @patch('handlers.amazon_handler.expand_shortened_url')
    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    async def test_short_amazon_link_delete_message(self, mock_convert, mock_expand):
        """Test if short Amazon links are expanded, converted to affiliate links, and original message is deleted when DELETE_MESSAGES is True."""
        
        mock_expand.return_value = "https://www.amazon.com/dp/B08N5WRWNW"
        mock_convert.return_value = "https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id"
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/shortlink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        await handle_amazon_links(mock_message)

        mock_expand.assert_called_with("https://amzn.to/shortlink")
        mock_convert.assert_called_with("https://www.amazon.com/dp/B08N5WRWNW")
        mock_message.delete.assert_called_once()
        mock_message.chat.send_message.assert_called_once()

    @patch('handlers.amazon_handler.DELETE_MESSAGES', False)
    @patch('handlers.amazon_handler.expand_shortened_url')
    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    async def test_short_amazon_link_no_delete_message(self, mock_convert, mock_expand):
        """Test if short Amazon links are expanded, converted to affiliate links, and original message is kept when DELETE_MESSAGES is False."""
        
        mock_expand.return_value = "https://www.amazon.com/dp/B08N5WRWNW"
        mock_convert.return_value = "https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id"
        
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/shortlink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        await handle_amazon_links(mock_message)

        mock_expand.assert_called_with("https://amzn.to/shortlink")
        mock_convert.assert_called_with("https://www.amazon.com/dp/B08N5WRWNW")
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_called_once()
        mock_message.chat.send_message.assert_called_with(
            text=ANY, reply_to_message_id=mock_message.message_id  # Replying instead of deleting
        )

    @patch('handlers.amazon_handler.DELETE_MESSAGES', False)
    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    async def test_long_amazon_link_without_affiliate_no_delete(self, mock_convert):
        """Test if long Amazon links without affiliate IDs are converted, and original message is kept when DELETE_MESSAGES is False."""
        
        mock_convert.return_value = "https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        await handle_amazon_links(mock_message)

        mock_convert.assert_called_with("https://www.amazon.com/dp/B08N5WRWNW")
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_called_once()
        mock_message.chat.send_message.assert_called_with(
            text=ANY, reply_to_message_id=mock_message.message_id  # Replying instead of deleting
        )

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    async def test_long_amazon_link_without_affiliate(self, mock_convert):
        """Test if long Amazon links without affiliate ID are converted to include the affiliate ID."""
        mock_convert.return_value = "https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"
        
        await handle_amazon_links(mock_message)

        mock_convert.assert_called_with("https://www.amazon.com/dp/B08N5WRWNW")
        mock_message.delete.assert_called_once()
        mock_message.chat.send_message.assert_called_once()

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    async def test_amazon_link_with_affiliate(self, mock_convert):
        """Test if Amazon links with an existing affiliate ID are modified to use ours."""
        mock_convert.return_value = "https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id"
        
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=another_affiliate"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"
        
        await handle_amazon_links(mock_message)

        mock_convert.assert_called_with("https://www.amazon.com/dp/B08N5WRWNW?tag=another_affiliate")
        mock_message.delete.assert_called_once()
        mock_message.chat.send_message.assert_called_once()

    async def test_no_amazon_link(self):
        """Test that no action is taken if there are no Amazon links in the message."""
        mock_message = AsyncMock()
        mock_message.text = "This is a random message without Amazon links."
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"
        
        result = await handle_amazon_links(mock_message)

        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch('handlers.amazon_handler.AMAZON_AFFILIATE_ID', "affiliate-21")
    async def test_explicit_amazon_link_conversion(self):
        """Test explicit case where a shortened Amazon link is expanded and the correct affiliate ID is added."""
                
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.eu/d/iR6MCth"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"
        
        # Call the function
        await handle_amazon_links(mock_message)

        # Construct expected message using the MSG_REPLY_PROVIDED_BY_USER and MSG_AFFILIATE_LINK_MODIFIED
        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser:\n\n"
            "Check this out: https://www.amazon.es/dp/B01M9ATDY7?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        # Extract the actual call arguments to compare
        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)

    @patch('handlers.amazon_handler.expand_shortened_url')
    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.logger')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', True)
    async def test_short_link_with_other_affiliate_tag_delete(self, mock_logger, mock_convert, mock_expand):
        """Test short Amazon link with another affiliate tag and message deletion."""
        mock_expand.return_value = "https://www.amazon.es/dp/B0CFQFC9MB"
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/3ZFldVh?tag=unfrikidomoti-21"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser:\n\n"
            "Check this out: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_called_once()

    @patch('handlers.amazon_handler.expand_shortened_url')
    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', False)
    async def test_short_link_with_other_affiliate_tag_no_delete(self, mock_convert, mock_expand):
        """Test short Amazon link with another affiliate tag and without message deletion."""
        mock_expand.return_value = "https://www.amazon.es/dp/B0CFQFC9MB"
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/3ZFldVh?tag=unfrikidomoti-21"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser:\n\n"
            "Check this out: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_not_called()

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.logger')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', True)
    async def test_long_link_without_affiliate_tag_delete(self, mock_logger, mock_convert):
        """Test long Amazon link without affiliate tag and message deletion."""
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB/ref=cm_sw_r_as_gl_api_gl_i_Q4XP46193PGHHDCNRBWS?linkCode=ml1"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_called_once()

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', False)
    async def test_long_link_without_affiliate_tag_no_delete(self, mock_convert):
        """Test long Amazon link without affiliate tag and without message deletion."""
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB/ref=cm_sw_r_as_gl_api_gl_i_Q4XP46193PGHHDCNRBWS?linkCode=ml1"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser2:\n\n"
            "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_not_called()

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', True)
    async def test_long_link_with_affiliate_tag_delete(self, mock_convert):
        """Test long Amazon link with another affiliate tag and message deletion."""
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB/ref=cm_sw_r_as_gl_api_gl_i_Q4XP46193PGHHDCNRBWS?linkCode=ml1&tag=unfrikidomoti-21&th=1"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser3:\n\n"
            "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_called_once()

    @patch('handlers.amazon_handler.convert_to_affiliate_link')
    @patch('handlers.amazon_handler.DELETE_MESSAGES', False)
    async def test_long_link_with_affiliate_tag_no_delete(self, mock_convert):
        """Test long Amazon link with another affiliate tag and without message deletion."""
        mock_convert.return_value = "https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21"

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB/ref=cm_sw_r_as_gl_api_gl_i_Q4XP46193PGHHDCNRBWS?linkCode=ml1&tag=unfrikidomoti-21&th=1"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        await handle_amazon_links(mock_message)

        expected_message = (
            f"{MSG_REPLY_PROVIDED_BY_USER} @testuser3:\n\n"
            "Here is a product: https://www.amazon.es/dp/B0CFQFC9MB?tag=affiliate-21\n\n"
            f"{MSG_AFFILIATE_LINK_MODIFIED}"
        )

        actual_call_args = mock_message.chat.send_message.call_args.kwargs
        self.assertEqual(actual_call_args['text'], expected_message)
        mock_message.delete.assert_not_called()

    @patch('handlers.amazon_handler.AMAZON_AFFILIATE_ID', None)
    async def test_no_action_when_amazon_affiliate_id_is_none(self):
        """Test that no action is taken if AMAZON_AFFILIATE_ID is None."""
        
        # Simulamos un mensaje con un enlace de Amazon
        mock_message = AsyncMock()
        mock_message.text = "Check out this product: https://www.amazon.es/dp/B08N5WRWNW"
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        # Ejecutar la función
        result = await handle_amazon_links(mock_message)

        # Asegurarse de que no se haya hecho ninguna modificación ni acción en el mensaje
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()

        # Comprobamos que la función devuelve False indicando que no hizo nada
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
