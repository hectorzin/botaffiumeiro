import unittest

from unittest.mock import AsyncMock, patch

from handlers.base_handler import BaseHandler
from handlers.amazon_handler import AmazonHandler


class TestHandler(BaseHandler):
    def handle_links(self, _):
        pass


class TestHandleAmazonLinks(unittest.IsolatedAsyncioTestCase):

    async def test_no_amazon_link(self):
        """Test that no action is taken if there are no Amazon links in the message."""
        mock_message = AsyncMock()
        mock_message.text = "This is a random message without Amazon links."
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        result = await AmazonHandler().handle_links(mock_message)

        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", None)
    async def test_no_action_when_amazon_affiliate_id_is_none(self):
        """Test that no action is taken if AMAZON_AFFILIATE_ID is None."""

        # Simulamos un mensaje con un enlace de Amazon
        mock_message = AsyncMock()
        mock_message.text = (
            "Check out this product: https://www.amazon.es/dp/B08N5WRWNW"
        )
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        # Ejecutar la función
        result = await AmazonHandler().handle_links(mock_message)

        # Asegurarse de que no se haya hecho ninguna modificación ni acción en el mensaje
        mock_message.delete.assert_not_called()
        mock_message.chat.send_message.assert_not_called()

        # Comprobamos que la función devuelve False indicando que no hizo nada
        self.assertFalse(result)

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", "our_affiliate_id")
    @patch("handlers.base_handler.BaseHandler._expand_shortened_url")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_short_amazon_link_message(self, mock_process, mock_expand):
        """Test if short Amazon links are expanded, converted to affiliate links, and original message is deleted when DELETE_MESSAGES is True."""

        mock_expand.return_value = "https://www.amazon.com/dp/B08N5WRWNW"
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/shortlink"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        await AmazonHandler().handle_links(mock_message)

        mock_expand.assert_called_once()
        mock_process.assert_called_with(
            mock_message,
            "Check this out: https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id",
        )

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", "our_affiliate_id")
    @patch("handlers.base_handler.BaseHandler._expand_shortened_url")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_long_amazon_link_without_affiliate(self, mock_process, mock_expand):
        """Test if long Amazon links without affiliate ID are converted to include the affiliate ID."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        await AmazonHandler().handle_links(mock_message)

        mock_expand.assert_not_called()
        mock_process.assert_called_with(
            mock_message,
            "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id",
        )

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", "our_affiliate_id")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_amazon_link_with_affiliate(self, mock_process):
        """Test if Amazon links with an existing affiliate ID are modified to use ours."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=another_affiliate"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        await AmazonHandler().handle_links(mock_message)

        mock_process.assert_called_with(
            mock_message,
            "Here is a product: https://www.amazon.com/dp/B08N5WRWNW?tag=our_affiliate_id",
        )

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", "our_affiliate_id")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_explicit_amazon_link_conversion(self, mock_process):
        """Test explicit case where a shortened Amazon link is expanded and the correct affiliate ID is added."""

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.eu/d/iR6MCth"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        # Call the function
        await AmazonHandler().handle_links(mock_message)

        # Construct expected message using the MSG_REPLY_PROVIDED_BY_USER and MSG_AFFILIATE_LINK_MODIFIED
        expected_message = "Check this out: https://www.amazon.es/Honeywell-T6R-programable-Inteligente-inal%C3%A1mbrico/dp/B01M9ATDY7?tag=our_affiliate_id"

        mock_process.assert_called_with(mock_message, expected_message)

    @patch("handlers.amazon_handler.AMAZON_AFFILIATE_ID", "our_affiliate_id")
    @patch("handlers.base_handler.BaseHandler._expand_shortened_url")
    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_short_link_with_other_affiliate_tag(self, mock_process, mock_expand):
        """Test short Amazon link with another affiliate tag and message deletion."""
        mock_expand.return_value = (
            "https://www.amazon.es/dp/B0CFQFC9MB?tag=unfrikidomoti-21"
        )
        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://amzn.to/3ZFldVh"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser"

        await AmazonHandler().handle_links(mock_message)

        expected_message = (
            "Check this out: https://www.amazon.es/dp/B0CFQFC9MB?tag=our_affiliate_id"
        )

        mock_process.assert_called_with(mock_message, expected_message)


if __name__ == "__main__":
    unittest.main()
