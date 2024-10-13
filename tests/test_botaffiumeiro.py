import unittest

from botaffiumeiro import is_user_excluded, modify_link
from datetime import datetime
from telegram import Update, User, Message, Chat
from unittest.mock import AsyncMock, patch


class TestBotHandlers(unittest.IsolatedAsyncioTestCase):

    @patch("botaffiumeiro.EXCLUDED_USERS", [12345, "excluded_user"])
    def test_is_user_excluded_in_list(self):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=User(
                    id=12345,
                    is_bot=False,
                    username="fake_user_01",
                    first_name="fake_first_name_01",
                ),
                chat=Chat(id=1, type="group"),
            ),
        )

        result = is_user_excluded(update)

        self.assertTrue(result)

    @patch("botaffiumeiro.EXCLUDED_USERS", [12345, "excluded_user"])
    def test_is_user_excluded_not_in_list(self):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=User(
                    id=67890,
                    is_bot=False,
                    username="fake_user_01",
                    first_name="fake_first_name_01",
                ),
                chat=Chat(id=1, type="group"),
            ),
        )

        result = is_user_excluded(update)

        self.assertFalse(result)

    @patch("botaffiumeiro.EXCLUDED_USERS", [12345, "excluded_user"])
    def test_is_user_excluded_in_list_without_username(self):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=User(
                    id=12345,
                    is_bot=True,
                    first_name="fake_first_name_01",
                ),
                chat=Chat(id=1, type="group"),
            ),
        )

        result = is_user_excluded(update)

        self.assertTrue(result)

    @patch("botaffiumeiro.handle_amazon_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_awin_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_admitad_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_aliexpress_links", new_callable=AsyncMock)
    async def test_modify_link_without_message(
        self,
        mock_handle_aliexpress,
        mock_handle_admitad,
        mock_handle_awin,
        mock_handle_amazon,
    ):
        update = Update(update_id=1)
        context = None

        await modify_link(update, context)

        mock_handle_amazon.assert_not_called()
        mock_handle_awin.assert_not_called()
        mock_handle_admitad.assert_not_called()
        mock_handle_aliexpress.assert_not_called()

    @patch("botaffiumeiro.handle_amazon_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_awin_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_admitad_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_aliexpress_links", new_callable=AsyncMock)
    async def test_modify_link_message_without_text(
        self,
        mock_handle_aliexpress,
        mock_handle_admitad,
        mock_handle_awin,
        mock_handle_amazon,
    ):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=None,
                chat=Chat(id=1, type="group"),
            ),
        )
        context = None

        await modify_link(update, context)

        mock_handle_amazon.assert_not_called()
        mock_handle_awin.assert_not_called()
        mock_handle_admitad.assert_not_called()
        mock_handle_aliexpress.assert_not_called()

    @patch("botaffiumeiro.is_user_excluded", return_value=True)
    @patch("botaffiumeiro.handle_amazon_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_awin_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_admitad_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_aliexpress_links", new_callable=AsyncMock)
    async def test_modify_link_excluded_user(
        self,
        mock_is_user_excluded,
        mock_handle_aliexpress,
        mock_handle_admitad,
        mock_handle_awin,
        mock_handle_amazon,
    ):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=User(id=12345, is_bot=False, first_name="TestUser"),
                chat=Chat(id=1, type="group"),
            ),
        )
        context = None

        await modify_link(update, context)

        mock_handle_amazon.assert_not_called()
        mock_handle_awin.assert_not_called()
        mock_handle_admitad.assert_not_called()
        mock_handle_aliexpress.assert_not_called()

    @patch("botaffiumeiro.is_user_excluded", return_value=False)
    @patch("botaffiumeiro.handle_amazon_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_awin_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_admitad_links", new_callable=AsyncMock)
    @patch("botaffiumeiro.handle_aliexpress_links", new_callable=AsyncMock)
    async def test_modify_link_included_user(
        self,
        mock_is_user_excluded,
        mock_handle_aliexpress,
        mock_handle_admitad,
        mock_handle_awin,
        mock_handle_amazon,
    ):
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(),
                from_user=User(id=67890, is_bot=False, first_name="TestUser"),
                chat=Chat(id=1, type="group"),
                text="Test message",
            ),
        )
        context = None

        await modify_link(update, context)

        mock_handle_amazon.assert_called_once()
        mock_handle_awin.assert_called_once()
        mock_handle_admitad.assert_called_once()
        mock_handle_aliexpress.assert_called_once()
