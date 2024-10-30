import unittest
from unittest.mock import AsyncMock, patch
from handlers.pattern_handler import PatternHandler


class TestHandleAwinLinks(unittest.IsolatedAsyncioTestCase):

    async def test_no_action_when_awin_publisher_id_is_none(self):
        """Test that no action is taken if AWIN_PUBLISHER_ID is None."""

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.pccomponentes.com/some-product I hope you like it"
        mock_message.message_id = 1
        mock_message.from_user.username = "testuser1"
        handler = PatternHandler()
        mock_selected_users = {
            "pccomponentes.com": {
                "awin": {
                    "publisher_id": None,
                    "advertisers": {"pccomponentes.com": "20982"},
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        mock_message.chat.send_message.assert_not_called()
        self.assertFalse(result)

    async def test_awin_aliexpress_link_awin_config_empty_list(self):
        """Test AliExpress link when AliExpress is NOT in the Awin list and discount codes should NOT be added."""
        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        handler = PatternHandler()
        mock_selected_users = {
            "pccomponentes.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {},
                }
            }
        }
        await handler.handle_links(mock_message)
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_awin_link_in_list(self, mock_process):
        """Test Awin links conversion when. New message must match the original reply structure."""

        mock_message = AsyncMock()
        mock_message.text = (
            "Check this out: https://www.giftmio.com/some-product I hope you like it"
        )
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 10

        handler = PatternHandler()
        mock_selected_users = {
            "giftmio.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"giftmio.com": "20982"},
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        expected_message = "Check this out: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=my_awin_id&ued=https://www.giftmio.com/some-product I hope you like it"

        mock_process.assert_called_with(mock_message, expected_message)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_awin_affiliate_link_from_list(self, mock_process):
        """Test if an existing Awin affiliate link is modified when the store is in our list of Awin advertisers."""

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.awin1.com/cread.php?awinmid=other_id_not_mine&awinaffid=other_affiliate_id&ued=https://www.giftmio.com/some-product I hope you like it"
        mock_message.message_id = 3
        mock_message.from_user.username = "testuser3"

        handler = PatternHandler()
        mock_selected_users = {
            "giftmio.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"giftmio.com": "20982"},
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        expected_message = "Here is a product: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=my_awin_id&ued=https://www.giftmio.com/some-product I hope you like it"

        mock_process.assert_called_with(mock_message, expected_message)

    async def test_awin_affiliate_link_not_in_list(self):
        """Test that an existing Awin affiliate link is NOT modified when the store is NOT in our list of Awin advertisers."""

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.awin1.com/cread.php?awinmid=other_id_not_mine&awinaffid=other_affiliate_id&ued=https://www.unknownstore.com/product I hope you like it"
        mock_message.message_id = 4
        mock_message.from_user.username = "testuser4"

        handler = PatternHandler()
        mock_selected_users = {
            "giftmio.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"giftmio.com": "20982"},
                }
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        mock_message.chat.send_message.assert_not_called()

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_awin_aliexpress_link_without_discount(self, mock_process):
        """Test AliExpress link in Awin list, no discount code added."""

        mock_message = AsyncMock()
        mock_message.text = "Check this out: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 5
        mock_message.from_user.username = "testuser"
        mock_message.reply_to_message = None

        handler = PatternHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"aliexpress.com": "11640"},
                },
                "aliexpress": {
                    "discount_codes": None,
                },
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        expected_message = "Check this out: https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin_id&ued=https://www.aliexpress.com/item/1005002958205071.html I hope you like it"

        mock_process.assert_called_with(mock_message, expected_message)

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_awin_aliexpress_link_with_discount(self, mock_process):
        """Test AliExpress link in Awin list, adding discount codes when applicable."""

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        mock_message.reply_to_message = None

        handler = PatternHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"aliexpress.com": "11640"},
                },
                "aliexpress": {
                    "discount_codes": "Here is your discount code!",
                },
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        expected_message = (
            "Here is a product: https://www.awin1.com/cread.php?awinmid=11640&awinaffid=my_awin_id&ued=https://www.aliexpress.com/item/1005002958205071.html I hope you like it\n\n"
            "Here is your discount code!"
        )

        mock_process.assert_called_with(mock_message, expected_message)

    async def test_awin_aliexpress_link_no_awin_config(self):
        """Test AliExpress link when AliExpress is NOT in the Awin list and discount codes should NOT be added."""

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.aliexpress.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 2
        mock_message.from_user.username = "testuser2"

        handler = PatternHandler()
        mock_selected_users = {
            "aliexpress.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"pccomponentes.com": "20982"},
                },
                "aliexpress": {
                    "discount_codes": "Here is your discount code!",
                },
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        mock_message.chat.send_message.assert_not_called()

    @patch("handlers.base_handler.BaseHandler._process_message")
    async def test_awin_no_aliexpress_from_link_with_discount(self, mock_process):
        """Test No AliExpress link in Awin list, the discount should not be applied."""

        mock_message = AsyncMock()
        mock_message.text = "Here is a product: https://www.pccomponentes.com/item/1005002958205071.html I hope you like it"
        mock_message.message_id = 6
        mock_message.from_user.username = "testuser2"
        mock_message.reply_to_message = None

        expected_message = "Here is a product: https://www.awin1.com/cread.php?awinmid=20982&awinaffid=my_awin_id&ued=https://www.pccomponentes.com/item/1005002958205071.html I hope you like it"

        handler = PatternHandler()
        mock_selected_users = {
            "pccomponentes.com": {
                "awin": {
                    "publisher_id": "my_awin_id",
                    "advertisers": {"pccomponentes.com": "20982"},
                },
                "aliexpress": {
                    "discount_codes": "Here is your discount code!",
                },
            }
        }
        context = {
            "message": mock_message,
            "modified_message": mock_message.text,
            "selected_users": mock_selected_users,
        }
        result = await handler.handle_links(context)

        mock_process.assert_called_with(mock_message, expected_message)


if __name__ == "__main__":
    unittest.main()
0
