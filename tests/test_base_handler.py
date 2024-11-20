"""Tests for the base handler used as parent of all handlers."""
# ruff: noqa: SLF001

import unittest
from unittest.mock import AsyncMock, Mock

from handlers.base_handler import PATTERN_AFFILIATE_URL_QUERY, BaseHandler


class TestHandler(BaseHandler):
    """Dummy handler for testing."""

    async def handle_links(self, _: dict) -> bool:
        """Stub method for handling links."""
        return False


class TestGenerateAffiliateUrl(unittest.TestCase):
    """Tests for the method that generates affiliate URL."""

    def setUp(self) -> None:
        """Set up the TestHandler instance with a mock ConfigurationManager."""
        self.config_manager = Mock()  # Create a mock ConfigurationManager
        self.handler = TestHandler(self.config_manager)

    def test_amazon_affiliate_url(self) -> None:
        """Test Amazon affiliate link generation with a simple format."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_data = {"affiliate_tag": "tag", "affiliate_id": "affiliate-21"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_admitad_affiliate_url_with_store_id(self) -> None:
        """Test Admitad affiliate link generation with store ID and affiliate ID."""
        original_url = "https://www.some-admitad-store.com/product"
        affiliate_data = {"affiliate_tag": "aff_id", "affiliate_id": "admitad-21"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}?store_id=12345&{affiliate_tag}={affiliate_id}",
            affiliate_data=affiliate_data,
        )
        expected_url = (
            "https://www.some-admitad-store.com?store_id=12345&aff_id=admitad-21"
        )
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_existing_affiliate_tag_overwrite(self) -> None:
        """Test overwriting an existing affiliate tag in the URL."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=old-affiliate"
        affiliate_data = {"affiliate_tag": "tag", "affiliate_id": "new-affiliate"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=new-affiliate"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template(self) -> None:
        """Test that the query string is appended properly if the template does not include the affiliate tag placeholders."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_data = {"affiliate_tag": "tag", "affiliate_id": "affiliate-21"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template_and_affiliate_tag_with_url_with_query(
        self,
    ) -> None:
        """Test that the query string is appended properly if the template does not include the affiliate tag placeholders."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW?item=5"
        affiliate_data = {"affiliate_tag": "tag", "affiliate_id": "affiliate-21"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?item=5&tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_in_path(self) -> None:
        """Test affiliate ID being inserted into a path before the query string."""
        original_url = "https://www.example.com/product/12345"
        affiliate_data = {"affiliate_tag": "aff_id", "affiliate_id": "my_affiliate"}
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}/{affiliate_tag}/{affiliate_id}{path_before_query}",
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.example.com/aff_id/my_affiliate/product/12345"
        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_and_advertiser_id_update(self) -> None:
        """Test that both affiliate_id and advertiser_id are updated correctly in the URL."""
        original_url = "https://www.example.com/product?tag=old_affiliate_id&advertiser_id=old_advertiser_id"
        affiliate_data = {
            "affiliate_tag": "tag",
            "affiliate_id": "new_affiliate_id",
            "advertiser_id": "new_advertiser_id",
        }
        format_template = "{domain}{path_before_query}?{affiliate_tag}={affiliate_id}&advertiser_id={advertiser_id}"
        updated_url = self.handler._generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_data=affiliate_data,
        )
        expected_url = "https://www.example.com/product?tag=new_affiliate_id&advertiser_id=new_advertiser_id"
        self.assertEqual(updated_url, expected_url)

    def test_affiliate_url_with_full_url(self) -> None:
        """Test affiliate URL generation with the full original URL in the format."""
        original_url = "https://www.example.com/product/12345"
        format_template = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid={affiliate_id}&ued={full_url}"
        affiliate_data = {"affiliate_tag": "awinaffid", "affiliate_id": "affiliate-21"}
        expected_url = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid=affiliate-21&ued=https://www.example.com/product/12345"

        affiliate_url = self.handler._generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_data=affiliate_data,
        )
        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_link_with_url_param_replacement(self) -> None:
        """Test affiliate link generation with dynamic replacement of {url} in the format template."""
        original_url = "https://source.com/product?url=https://example.com/product/123"
        format_template = "https://destino.com?url={url}&{affiliate_tag}={affiliate_id}"
        affiliate_data = {"affiliate_tag": "tag", "affiliate_id": "my_affiliate"}
        expected_url = (
            "https://destino.com?url=https://example.com/product/123&tag=my_affiliate"
        )
        affiliate_url = self.handler._generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_data=affiliate_data,
        )
        self.assertEqual(affiliate_url, expected_url)


class TestProcessMessage(unittest.IsolatedAsyncioTestCase):
    """Tests for the method _process_message."""

    def setUp(self) -> None:
        """Set up the TestHandler instance with a mock ConfigurationManager."""
        self.config_manager = Mock()
        self.config_manager.delete_messages = True
        self.config_manager.msg_reply_provided_by_user = "Message provided by user"
        self.config_manager.msg_affiliate_link_modified = "Affiliate link changed"
        self.handler = TestHandler(self.config_manager)

    async def test_send_message_and_delete_original(self) -> None:
        """Test when DELETE_MESSAGES is True, the original message should be deleted and a new one sent."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"

        await self.handler._process_message(mock_message, new_text)

        expected_message = (
            f"{self.config_manager.msg_reply_provided_by_user} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{self.config_manager.msg_affiliate_link_modified}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that a new message was sent
        actual_message = mock_message.chat.send_message.call_args[1]["text"]
        self.assertEqual(actual_message, expected_message)

    async def test_send_message_without_delete(self) -> None:
        """Test when DELETE_MESSAGES is False, the original message should not be deleted, and the bot replies to it."""
        self.config_manager.delete_messages = False  # Update config
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"

        await self.handler._process_message(mock_message, new_text)

        expected_message = (
            f"{self.config_manager.msg_reply_provided_by_user} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{self.config_manager.msg_affiliate_link_modified}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, reply_to_message_id=mock_message.message_id
        )

    async def test_send_message_is_reply_and_delete(self) -> None:
        """Test when DELETE_MESSAGES is True, and the original message is a reply to another message."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"

        await self.handler._process_message(mock_message, new_text)

        expected_message = (
            f"{self.config_manager.msg_reply_provided_by_user} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{self.config_manager.msg_affiliate_link_modified}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message replies to the same message the original one was replying to
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message,
            reply_to_message_id=mock_message.reply_to_message.message_id,
        )

    async def test_send_message_is_reply_without_delete(self) -> None:
        """Test when DELETE_MESSAGES is False, and the original message is a reply to another message."""
        self.config_manager.delete_messages = False  # Update config
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"

        await self.handler._process_message(mock_message, new_text)

        expected_message = (
            f"{self.config_manager.msg_reply_provided_by_user} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{self.config_manager.msg_affiliate_link_modified}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the new message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, reply_to_message_id=mock_message.message_id
        )

    async def test_send_message_without_username(self) -> None:
        """Test when the user has no username, use the first name instead."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = None
        mock_message.message_id = 102
        mock_message.text = "Original message"
        mock_message.reply_to_message = None  # Not replying to any message

        new_text = "This is the modified affiliate message"

        await self.handler._process_message(mock_message, new_text)

        expected_message = (
            f"{self.config_manager.msg_reply_provided_by_user} @Jane:\n\n"
            f"{new_text}\n\n"
            f"{self.config_manager.msg_affiliate_link_modified}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message is sent without replying
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, reply_to_message_id=None
        )


class TestBuildAffiliateUrlPattern(unittest.TestCase):
    """Tests for the method _build_affiliate_url_pattern."""

    def setUp(self) -> None:
        """Set up the ConfigurationManager mock and a TestHandler instance for each test."""
        self.config_manager = Mock()
        self.base_handler = TestHandler(self.config_manager)

    def test_admitad_url_pattern(self) -> None:
        """Test: Verify that admitad_url_pattern is correctly generated from multiple users' domains."""
        self.base_handler.selected_users = {
            "example.com": {
                "admitad": {
                    "advertisers": {
                        "example1.com": "12345",
                        "example2.com": "67890",
                    }
                }
            }
        }
        # Generate Admitad URL pattern
        admitad_url_pattern = self.base_handler._build_affiliate_url_pattern("admitad")

        # The expected regex should match example1.com and example2.com
        expected_pattern1 = (
            r"(https?://(?:[\w\-]+\.)?(example1\.com|example2\.com)"
            + PATTERN_AFFILIATE_URL_QUERY
            + ")"
        )
        expected_pattern2 = (
            r"(https?://(?:[\w\-]+\.)?(example2\.com|example1\.com)"
            + PATTERN_AFFILIATE_URL_QUERY
            + ")"
        )
        self.assertTrue(
            admitad_url_pattern in (expected_pattern1, expected_pattern2),
            f"Pattern '{admitad_url_pattern}' does not match either of the expected patterns",
        )

    def test_admitad_no_domains(self) -> None:
        """Test: Verify that None is returned when no Admitad advertisers exist across users."""
        self.base_handler.selected_users = {
            "example3.com": {
                "admitad": {"advertisers": {}},
                "awin": {"advertisers": {"example3.com": "affiliate-id-3"}},
            }
        }

        admitad_url_pattern = self.base_handler._build_affiliate_url_pattern("admitad")
        self.assertIsNone(admitad_url_pattern)

    def test_awin_url_pattern(self) -> None:
        """Test: Verify that awin_url_pattern is correctly generated from multiple users' domains."""
        self.base_handler.selected_users = {
            "example3.com": {
                "admitad": {
                    "advertisers": {
                        "example1.com": "affiliate-id-1",
                        "example2.com": "affiliate-id-2",
                    }
                },
                "awin": {
                    "advertisers": {
                        "example3.com": "affiliate-id-3",
                        "example4.com": "affiliate-id-4",
                    }
                },
            }
        }

        awin_url_pattern = self.base_handler._build_affiliate_url_pattern("awin")

        # The expected regex should match example3.com and example4.com
        expected_pattern1 = (
            r"(https?://(?:[\w\-]+\.)?(example3\.com|example4\.com)"
            + PATTERN_AFFILIATE_URL_QUERY
            + ")"
        )
        expected_pattern2 = (
            r"(https?://(?:[\w\-]+\.)?(example4\.com|example3\.com)"
            + PATTERN_AFFILIATE_URL_QUERY
            + ")"
        )
        self.assertTrue(
            awin_url_pattern in (expected_pattern1, expected_pattern2),
            f"Pattern '{awin_url_pattern}' does not match either of the expected patterns",
        )

    def test_no_users_in_configuration(self) -> None:
        """Test: Verify that None is returned when there are no users in the configuration."""
        self.base_handler.selected_users = {
            "amazon.es": {"amazon": {"affiliate_id": "affiliate-21"}}
        }

        admitad_url_pattern = self.base_handler._build_affiliate_url_pattern(
            "admitad_advertisers"
        )
        self.assertIsNone(admitad_url_pattern)


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
