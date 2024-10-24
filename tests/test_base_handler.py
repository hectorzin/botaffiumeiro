import unittest

from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import unquote
from handlers.base_handler import BaseHandler, PATTERN_AFFILIATE_URL_QUERY
from config import config_data


class TestHandler(BaseHandler):
    def handle_links(self):
        pass


class TestGenerateAffiliateUrl(unittest.TestCase):

    def setUp(self):
        """Set up the TestHandler instance."""
        self.handler = TestHandler()

    def test_amazon_affiliate_url(self):
        """Test Amazon affiliate link generation with a simple format."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_admitad_affiliate_url_with_store_id(self):
        """Test Admitad affiliate link generation with store ID and affiliate ID."""
        original_url = "https://www.some-admitad-store.com/product"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}?store_id=12345&{affiliate_tag}={affiliate_id}",
            affiliate_tag="aff_id",
            affiliate_id="admitad-21",
        )
        expected_url = (
            "https://www.some-admitad-store.com?store_id=12345&aff_id=admitad-21"
        )
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_existing_affiliate_tag_overwrite(self):
        """Test overwriting an existing affiliate tag in the URL."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=old-affiliate"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="new-affiliate",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=new-affiliate"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template_and_affiliate_tag(self):
        """Test that the query string is appended properly if the template does not include the affiliate tag placeholders."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template_and_affiliate_tag_with_url_with_query(self):
        """Test that the query string is appended properly if the template does not include the affiliate tag placeholders."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW?item=5"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?item=5&tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_no_affiliate_tag_in_template_and_not_affiliate_tag(self):
        """Test that the query string is appended properly if the template does not include the affiliate tag id."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}",
            affiliate_tag=None,
            affiliate_id="affiliate-21",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW"
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_empty_query(self):
        """Test URL without query parameters should add affiliate tag."""
        original_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="tag",
            affiliate_id="affiliate-21",
        )
        expected_url = "https://www.amazon.com/dp/B08N5WRWNW?tag=affiliate-21"
        self.assertEqual(affiliate_url, expected_url)

    def test_url_with_complex_path(self):
        """Test URL with complex path (multiple slashes and query params) should generate correctly."""
        original_url = "https://www.example.com/store/sub-store/product/12345?color=red"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}{path_before_query}?{affiliate_tag}={affiliate_id}",
            affiliate_tag="aff_id",
            affiliate_id="affiliate-99",
        )
        expected_url = (
            "https://www.example.com/store/sub-store/product/12345?aff_id=affiliate-99"
        )
        self.assertEqual(unquote(affiliate_url), expected_url)

    def test_affiliate_in_path(self):
        """Test affiliate ID being inserted into a path before the query string."""
        original_url = "https://www.example.com/product/12345"
        affiliate_url = self.handler._generate_affiliate_url(
            original_url,
            format_template="{domain}/{affiliate_tag}/{affiliate_id}{path_before_query}",
            affiliate_tag="aff_id",
            affiliate_id="my_affiliate",
        )
        expected_url = "https://www.example.com/aff_id/my_affiliate/product/12345"
        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_url_with_full_url(self):
        """Test affiliate URL generation with the full original URL in the format (like Awin or Admitad)."""
        original_url = "https://www.example.com/product/12345"
        format_template = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid={affiliate_id}&ued={full_url}"
        affiliate_tag = "awinaffid"
        affiliate_id = "affiliate-21"

        expected_url = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid=affiliate-21&ued=https://www.example.com/product/12345"

        affiliate_url = self.handler._generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_tag=affiliate_tag,
            affiliate_id=affiliate_id,
        )

        self.assertEqual(affiliate_url, expected_url)

    def test_affiliate_and_advertiser_id_update(self):
        """Test that both affiliate_id and advertiser_id are updated correctly in the URL."""

        original_url = "https://www.example.com/product?tag=old_affiliate_id&advertiser_id=old_advertiser_id"
        format_template = "{domain}{path_before_query}?{affiliate_tag}={affiliate_id}&advertiser_id={advertiser_id}"

        # Call the method with new affiliate_id and advertiser_id
        updated_url = self.handler._generate_affiliate_url(
            original_url=original_url,
            format_template=format_template,
            affiliate_tag="tag",
            affiliate_id="new_affiliate_id",
            advertiser_id="new_advertiser_id",
        )

        # Expected URL after updating the affiliate and advertiser IDs
        expected_url = "https://www.example.com/product?tag=new_affiliate_id&advertiser_id=new_advertiser_id"

        # Assert that the updated URL matches the expected URL
        self.assertEqual(updated_url, expected_url)

    def test_affiliate_link_with_advertiser(self):
        """Test affiliate link generation with an advertiser ID."""
        original_url = "https://example.com/product/123"
        format_template = "{domain}{path_before_query}?{affiliate_tag}={affiliate_id}&advertiser_id={advertiser_id}"
        affiliate_tag = "tag"
        affiliate_id = "my_affiliate"
        advertiser_id = "12345"

        expected_url = (
            "https://example.com/product/123?tag=my_affiliate&advertiser_id=12345"
        )

        result = self.handler._generate_affiliate_url(
            original_url, format_template, affiliate_tag, affiliate_id, advertiser_id
        )
        self.assertEqual(result, expected_url)

    def test_affiliate_link_with_url_param_replacement(self):
        """Test affiliate link generation with dynamic replacement of {url} in the format template."""
        original_url = "https://source.com/product?url=https://example.com/product/123"
        format_template = "https://destino.com?url={url}&{affiliate_tag}={affiliate_id}"
        affiliate_tag = "tag"
        affiliate_id = "my_affiliate"

        expected_url = (
            "https://destino.com?url=https://example.com/product/123&tag=my_affiliate"
        )

        result = self.handler._generate_affiliate_url(
            original_url, format_template, affiliate_tag, affiliate_id
        )
        self.assertEqual(result, expected_url)


class TestProcessMessage(unittest.TestCase):

    def setUp(self):
        """Set up the TestHandler instance."""
        self.handler = TestHandler()  # Pasar selected_users al crear la instancia

    @patch(
        "botaffiumeiro.config_data",
        {
            "DELETE_MESSAGES": True,
            "MSG_REPLY_PROVIDED_BY_USER": "Messager provider by user",
            "MSG_AFFILIATE_LINK_MODIFIED": "Affiliate link changed",
        },
    )
    async def test_send_message_and_delete_original(self):
        """Test when DELETE_MESSAGES is True, the original message should be deleted and a new one sent."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"

        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that a new message was sent
        mock_message.chat.send_message.assert_called_once_with(text=expected_message)

    @patch(
        "botaffiumeiro.config_data",
        {
            "DELETE_MESSAGES": False,
            "MSG_REPLY_PROVIDED_BY_USER": "Messager provider by user",
            "MSG_AFFILIATE_LINK_MODIFIED": "Affiliate link changed",
        },
    )
    async def test_send_message_without_delete(self):
        """Test when DELETE_MESSAGES is False, the original message should not be deleted, and the bot replies to it."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "John"
        mock_message.from_user.username = "john_doe"
        mock_message.message_id = 100
        mock_message.text = "Original message"

        new_text = "This is the modified affiliate message"

        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @john_doe:\n\n"
            f"{new_text}\n\n"
            f"{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, reply_to_message_id=mock_message.message_id
        )

    @patch(
        "botaffiumeiro.config_data",
        {
            "DELETE_MESSAGES": True,
            "MSG_REPLY_PROVIDED_BY_USER": "Messager provider by user",
            "MSG_AFFILIATE_LINK_MODIFIED": "Affiliate link changed",
        },
    )
    async def test_send_message_is_reply_and_delete(self):
        """Test when DELETE_MESSAGES is True, and the original message is a reply to another message."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"

        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message replies to the same message the original one was replying to
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message,
            reply_to_message_id=mock_message.reply_to_message.message_id,
        )

    @patch(
        "botaffiumeiro.config_data",
        {
            "DELETE_MESSAGES": False,
            "MSG_REPLY_PROVIDED_BY_USER": "Messager provider by user",
            "MSG_AFFILIATE_LINK_MODIFIED": "Affiliate link changed",
        },
    )
    async def test_send_message_is_reply_without_delete(self):
        """Test when DELETE_MESSAGES is False, and the original message is a reply to another message."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = "jane_doe"
        mock_message.message_id = 101
        mock_message.text = "Original message"
        mock_message.reply_to_message = AsyncMock()
        mock_message.reply_to_message.message_id = 50  # Replying to message ID 50

        new_text = "This is the modified affiliate message"

        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @jane_doe:\n\n"
            f"{new_text}\n\n"
            f"{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"
        )

        # Check that the original message was not deleted
        mock_message.delete.assert_not_called()
        # Check that the new message is sent as a reply to the original message
        mock_message.chat.send_message.assert_called_once_with(
            text=expected_message, reply_to_message_id=mock_message.message_id
        )

    @patch(
        "botaffiumeiro.config_data",
        {
            "DELETE_MESSAGES": True,
            "MSG_REPLY_PROVIDED_BY_USER": "Messager provider by user",
            "MSG_AFFILIATE_LINK_MODIFIED": "Affiliate link changed",
        },
    )
    async def test_send_message_without_username(self):
        """Test when the user has no username, use the first name instead."""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Jane"
        mock_message.from_user.username = None
        mock_message.message_id = 102
        mock_message.text = "Original message"
        mock_message.reply_to_message = None  # Not replying to any message

        new_text = "This is the modified affiliate message"

        await self.handler.process_message(mock_message, new_text)

        expected_message = (
            f"{config_data['MSG_REPLY_PROVIDED_BY_USER']} @Jane:\n\n"
            f"{new_text}\n\n"
            f"{config_data['MSG_AFFILIATE_LINK_MODIFIED']}"
        )

        # Check that the original message was deleted
        mock_message.delete.assert_called_once()
        # Check that the new message is sent without replying
        mock_message.chat.send_message.assert_called_once_with(text=expected_message)


class TestBuildAffiliateUrlPattern(unittest.TestCase):

    def test_admitad_url_pattern(self):
        """
        Test: Verify that admitad_url_pattern is correctly generated from multiple users' domains.
        """
        base_handler = TestHandler()
        base_handler.selected_users = {
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
        admitad_url_pattern = base_handler._build_affiliate_url_pattern("admitad")

        # The expected regex should match example1.com, example2.com, and example3.com
        # The order is not known
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
            admitad_url_pattern == expected_pattern1
            or admitad_url_pattern == expected_pattern2,
            f"Pattern '{admitad_url_pattern}' does not match either of the expected patterns",
        )

    def test_admitad_no_domains(self):
        """
        Test: Verify that None is returned when no Admitad advertisers exist across users.
        """
        base_handler = TestHandler()
        # Generate Admitad URL pattern (should return None as no advertisers are set)
        base_handler.selected_users = {
            "example3.com": {
                "admitad": {"advertisers": {}},
                "awin": {"advertisers": {"example3.com": "affiliate-id-3"}},
            }
        }

        admitad_url_pattern = base_handler._build_affiliate_url_pattern("admitad")
        self.assertIsNone(admitad_url_pattern)

    def test_awin_url_pattern(self):
        """
        Test: Verify that awin_url_pattern is correctly generated from multiple users' domains.
        """
        # Generate Awin URL pattern
        base_handler = TestHandler()
        base_handler.selected_users = {
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

        awin_url_pattern = base_handler._build_affiliate_url_pattern("awin")

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
            awin_url_pattern == expected_pattern1
            or awin_url_pattern == expected_pattern2,
            f"Pattern '{awin_url_pattern}' does not match either of the expected patterns",
        )

    def test_no_users_in_configuration(self):
        """
        Test: Verify that None is returned when there are no users in the configuration.
        """
        # Generate Admitad URL pattern with no users in the configuration
        base_handler = TestHandler()
        base_handler.selected_users = {
            "amazon.es": {"amazon": {"affiliate_id": "affiliate-21"}}
        }

        admitad_url_pattern = base_handler._build_affiliate_url_pattern(
            "admitad_advertisers"
        )
        self.assertIsNone(admitad_url_pattern)


if __name__ == "__main__":
    unittest.main()
