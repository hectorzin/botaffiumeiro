"""Tests for the main botaffiumeiro functions."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest
from unittest.mock import ANY, AsyncMock, Mock, patch

from telegram import Chat, Message, Update, User
from telegram.ext import CallbackContext

from botaffiumeiro import (
    expand_shortened_url,
    extract_domains_from_message,
    extract_embedded_url,
    is_user_excluded,
    modify_link,
    prepare_message,
    select_user_for_domain,
)


class TestIsUserExcluded(unittest.TestCase):
    """Tests for is_user_excluded function."""

    @patch("botaffiumeiro.config_manager", autospec=True)
    def test_is_user_excluded_in_list(self, mock_config_manager: AsyncMock) -> None:
        """Test is_user_excluded when a user is in the excluded list."""
        mock_config_manager.excluded_users = [12345, "excluded_user"]

        user = User(
            id=12345, is_bot=False, username="fake_user_01", first_name="TestUser"
        )
        result = is_user_excluded(user)

        self.assertTrue(result)

    @patch("botaffiumeiro.config_manager", autospec=True)
    def test_is_user_excluded_not_in_list(self, mock_config_manager: AsyncMock) -> None:
        """Test is_user_excluded when a user isn't in the excluded list."""
        mock_config_manager.excluded_users = [12345, "excluded_user"]

        user = User(
            id=67890, is_bot=False, username="non_excluded_user", first_name="TestUser"
        )
        result = is_user_excluded(user)

        self.assertFalse(result)


class TestModifyLink(unittest.IsolatedAsyncioTestCase):
    """Tests for modify_link function."""

    @patch("botaffiumeiro.is_user_excluded")
    @patch("botaffiumeiro.process_link_handlers", new_callable=AsyncMock)
    async def test_modify_link_without_message(
        self,
        mock_process_link_handlers: AsyncMock,
        mock_is_user_excluded: AsyncMock,
    ) -> None:
        """Test modify_link when the message is empty."""
        update = Update(update_id=1)
        mock_context = CallbackContext(application=None)
        await modify_link(update, mock_context)

        mock_is_user_excluded.assert_not_called()
        mock_process_link_handlers.assert_not_called()

    @patch("botaffiumeiro.is_user_excluded")
    @patch("botaffiumeiro.process_link_handlers", new_callable=AsyncMock)
    async def test_modify_link_message_without_text(
        self,
        mock_process_link_handlers: AsyncMock,
        mock_is_user_excluded: AsyncMock,
    ) -> None:
        """Test modify_link when the message has data bat no text."""
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(timezone.utc),
                from_user=None,
                chat=Chat(id=1, type="group"),
            ),
        )

        mock_context = CallbackContext(application=None)
        await modify_link(update, mock_context)

        mock_is_user_excluded.assert_not_called()
        mock_process_link_handlers.assert_not_called()

    @patch("botaffiumeiro.is_user_excluded", return_value=True)
    @patch("botaffiumeiro.process_link_handlers", new_callable=AsyncMock)
    async def test_modify_link_excluded_user(
        self,
        mock_process_link_handlers: AsyncMock,
        mock_is_user_excluded: AsyncMock,
    ) -> None:
        """Test modify_link when the message has a link but comes froma an excluded user."""
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(timezone.utc),
                from_user=User(id=12345, is_bot=False, first_name="TestUser"),
                chat=Chat(id=1, type="group"),
                text="Test message",
            ),
        )

        mock_context = CallbackContext(application=None)
        await modify_link(update, mock_context)

        mock_is_user_excluded.assert_called_once()
        mock_process_link_handlers.assert_not_called()

    @patch("botaffiumeiro.is_user_excluded", return_value=False)
    @patch("botaffiumeiro.process_link_handlers", new_callable=AsyncMock)
    async def test_modify_link_included_user(
        self,
        mock_process_link_handlers: AsyncMock,
        mock_is_user_excluded: AsyncMock,
    ) -> None:
        """Test modify_link when the message has a link and the user isn't int he excluded list."""
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(timezone.utc),
                from_user=User(id=67890, is_bot=False, first_name="TestUser"),
                chat=Chat(id=1, type="group"),
                text="Test message",
            ),
        )

        mock_context = CallbackContext(application=None)
        await modify_link(update, mock_context)

        mock_is_user_excluded.assert_called_once()
        mock_process_link_handlers.assert_called_once()

    @patch("botaffiumeiro.is_user_excluded")
    @patch("botaffiumeiro.process_link_handlers", new_callable=AsyncMock)
    async def test_modify_link_without_user(
        self,
        mock_process_link_handlers: AsyncMock,
        mock_is_user_excluded: AsyncMock,
    ) -> None:
        """Test modify_link when the message hasn't a user."""
        update = Update(
            update_id=1,
            message=Message(
                message_id=1,
                date=datetime.now(timezone.utc),
                chat=Chat(id=1, type="group"),
                text="Test message",
            ),
        )

        mock_context = CallbackContext(application=None)
        await modify_link(update, mock_context)

        mock_is_user_excluded.asset_not_called()
        mock_process_link_handlers.assert_not_called()


class TestExtractDomainsFromMessage(unittest.TestCase):
    """Tests for extract_domains_from_message function."""

    def test_direct_domain_extraction(self) -> None:
        """Test: Extract domains directly from the message without embedded URLs."""
        message_text = "Check out this link: https://www.amazon.com/someproduct and this: https://aliexpress.com/item/12345"
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn("amazon.com", domains)
        self.assertIn("aliexpress.com", domains)
        self.assertEqual(len(domains), 2)  # Should find 2 unique domains

    def test_embedded_url_excludes_main_domain(self) -> None:
        """Test: If there are embedded URLs, the main domain should be excluded."""
        message_text = (
            "Visit https://awin1.com/cread.php?ulp=https://aliexpress.com/item/12345"
        )

        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn(
            "aliexpress.com", domains
        )  # Only the embedded domain should be included
        self.assertNotIn("awin1.com", domains)  # The main domain should be excluded

    def test_no_embedded_urls(self) -> None:
        """Test: No embedded URLs, only direct domain extraction."""
        message_text = "Check out https://amazon.com/product123"
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn("amazon.com", domains)  # Should extract only amazon.com
        self.assertEqual(len(domains), 1)  # Only one domain should be found

    def test_multiple_direct_and_embedded_urls(self) -> None:
        """Test: Extract multiple direct and embedded URLs."""
        message_text = (
            "Check this product on Amazon: https://www.amazon.com/product?ref=123 "
            "or visit https://aliexpress.com/item/456 "
            "also, visit https://awin1.com/cread.php?ulp=https://amazon.com/ref456"
        )

        # Here, we mock the embedded URL extraction to return amazon.com from awin's ulp parameter
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn("amazon.com", domains)
        self.assertIn("aliexpress.com", domains)
        self.assertEqual(len(domains), 2)  # Should find 3 unique domains

    def test_no_matching_patterns(self) -> None:
        """Test: No matching domains or patterns in the message."""
        message_text = "There are no valid links in this message."
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertEqual(
            domains, set()
        )  # Should return an empty set since no domains are matched

    def test_invalid_urls(self) -> None:
        """Test: Handle invalid URLs that should not be extracted."""
        message_text = "Visit this: ftp://invalid-url.com and this invalid scheme: invalid://nope.com"
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertEqual(
            domains, set()
        )  # Should return an empty set since the URLs are invalid

    @patch(
        "botaffiumeiro.expand_shortened_url",
        return_value="https://www.amazon.com/dp/product123",
    )
    def test_amazon_shortened_url(self, mock_expand: AsyncMock) -> None:
        """Test: Handle shortened Amazon URL (amzn.to) and expand it."""
        message_text = "Check out this product: https://amzn.to/abc123"

        # Simulate the expansion of the shortened URL
        Mock(return_value="https://www.amazon.com/dp/product123")

        domains, modified_message = extract_domains_from_message(message_text)
        mock_expand.assert_called_once_with("https://amzn.to/abc123")

        self.assertIn(
            "amazon.com", domains
        )  # The expanded Amazon domain should be extracted
        self.assertNotIn(
            "amzn.to", domains
        )  # The shortened domain should no longer appear
        self.assertEqual(len(domains), 1)  # Should only find one expanded domain

        # Verify that the shortened URL has been replaced in the message
        self.assertIn("https://www.amazon.com/dp/product123", modified_message)

    @patch(
        "botaffiumeiro.expand_shortened_url",
        return_value="https://www.aliexpress.com/item/1005001234567890.html",
    )
    def test_aliexpress_shortened_url(self, mock_expand: AsyncMock) -> None:
        """Test: Handle shortened AliExpress URL (s.click.aliexpress.com) and expand it."""
        message_text = (
            "Check out this deal: https://s.click.aliexpress.com/e/buyproduct"
        )

        domains, modified_message = extract_domains_from_message(message_text)
        mock_expand.assert_called_once_with(
            "https://s.click.aliexpress.com/e/buyproduct"
        )

        self.assertIn(
            "aliexpress.com", domains
        )  # The expanded AliExpress domain should be extracted
        self.assertNotIn(
            "s.click.aliexpress.com", domains
        )  # The shortened domain should no longer appear
        self.assertEqual(len(domains), 1)  # Should only find one expanded domain

        # Verify that the shortened URL has been replaced in the message
        self.assertIn(
            "https://www.aliexpress.com/item/1005001234567890.html", modified_message
        )

    @patch("botaffiumeiro.expand_shortened_url")
    def test_mixed_full_and_shortened_urls(self, mock_expand: AsyncMock) -> None:
        """Test: Handle a mixture of full and shortened URLs for both platforms."""
        message_text = (
            "Check out this Amazon deal: https://www.amazon.com/dp/product123 "
            "or the shortened version: https://amzn.to/abc123 "
            "and this AliExpress deal: https://s.click.aliexpress.com/e/buyproduct"
        )

        # Simulate the expansion of the shortened URLs
        mock_expand.side_effect = [
            "https://www.amazon.com/dp/product123",  # Long URL link, expands as itself
            "https://www.amazon.com/dp/product456",  # Expanded URL for amzn.to
            "https://www.aliexpress.com/item/1005001234567890.html",  # Expanded URL for aliexpress shortened link
        ]

        # Call the function that processes the message and expands shortened URLs
        domains, modified_message = extract_domains_from_message(message_text)

        # Check that the expand_shortened_url function was called twice with correct URLs
        mock_expand.assert_any_call("https://www.amazon.com/dp/product123")
        mock_expand.assert_any_call("https://amzn.to/abc123")
        mock_expand.assert_any_call("https://s.click.aliexpress.com/e/buyproduct")

        # Ensure the extracted domains include amazon.com and aliexpress.com
        self.assertIn("amazon.com", domains)
        self.assertIn("aliexpress.com", domains)

        # Verify the shortened URLs were replaced with the expanded versions
        self.assertNotIn("amzn.to", modified_message)
        self.assertNotIn("s.click.aliexpress.com", modified_message)

        # Check that the expanded URLs are now in the message
        self.assertIn("https://www.amazon.com/dp/product456", modified_message)
        self.assertIn(
            "https://www.aliexpress.com/item/1005001234567890.html", modified_message
        )

    def test_amazon_full_url_uk(self) -> None:
        """Test: Handle full Amazon URL with amazon.co.uk."""
        message_text = "Check out this product on Amazon UK: https://www.amazon.co.uk/dp/product123"
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn(
            "amazon.co.uk", domains
        )  # The amazon.co.uk domain should be extracted
        self.assertEqual(len(domains), 1)  # Should only find one domain

    @patch("requests.get")
    def test_expand_amazon_short_url_and_replace_in_message(
        self, mock_get: AsyncMock
    ) -> None:
        """Test: Expands a shortened Amazon URL and replaces it in the message."""
        mock_response = Mock()
        mock_response.url = "https://www.amazon.com/dp/B08XYZ123"
        mock_get.return_value = mock_response

        message_text = "Check out this Amazon link: https://amzn.to/abc123"

        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn("amazon.com", domains)
        self.assertEqual(
            modified_message,
            "Check out this Amazon link: https://www.amazon.com/dp/B08XYZ123",
        )

    @patch("requests.get")
    def test_expand_multiple_short_urls_and_replace_in_message(
        self, mock_get: AsyncMock
    ) -> None:
        """Test: Expands multiple shortened URLs and replaces them in the message."""
        mock_response_amazon = Mock()
        mock_response_amazon.url = "https://www.amazon.com/dp/B08XYZ123"
        mock_response_aliexpress = Mock()
        mock_response_aliexpress.url = "https://www.aliexpress.com/item/12345.html"

        mock_get.side_effect = [mock_response_amazon, mock_response_aliexpress]

        message_text = "Check out this Amazon link: https://amzn.to/abc123 and this AliExpress link: https://s.click.aliexpress.com/e/xyz789"
        domains, modified_message = extract_domains_from_message(message_text)

        self.assertIn("amazon.com", domains)
        self.assertIn("aliexpress.com", domains)
        self.assertEqual(
            modified_message,
            "Check out this Amazon link: https://www.amazon.com/dp/B08XYZ123 and this AliExpress link: https://www.aliexpress.com/item/12345.html",
        )

    @patch("requests.get")
    def test_extract_domains_with_short_urls(self, mock_get: AsyncMock) -> None:
        """Test: Extract domains after expanding shortened URLs."""
        # Simula las respuestas de las cabeceras para las URLs cortas
        mock_response_amazon = Mock()
        mock_response_amazon.url = (
            "https://www.amazon.com/dp/B08XYZ123"  # URL expandida de Amazon
        )
        mock_response_aliexpress = Mock()
        mock_response_aliexpress.url = (
            "https://www.aliexpress.com/item/12345.html"  # URL expandida de AliExpress
        )

        # Configura el mock para devolver las respuestas simuladas en secuencia
        mock_get.side_effect = [mock_response_amazon, mock_response_aliexpress]

        # Texto con URLs acortadas
        message_text = "Check out this Amazon deal: https://amzn.to/abc123 and this AliExpress: https://s.click.aliexpress.com/e/buyproduct"

        # Llama a la función a probar
        domains, modified_message = extract_domains_from_message(message_text)

        # Verifica que los dominios correctos fueron extraídos
        self.assertIn("amazon.com", domains)  # Debería encontrar amazon.com
        self.assertIn("aliexpress.com", domains)  # Debería encontrar aliexpress.com

        # Verifica que las URLs acortadas hayan sido reemplazadas con las URLs expandidas
        self.assertIn("https://www.amazon.com/dp/B08XYZ123", modified_message)
        self.assertIn("https://www.aliexpress.com/item/12345.html", modified_message)

        # Verifica que las URLs cortas ya no estén en el mensaje modificado
        self.assertNotIn("https://amzn.to/abc123", modified_message)
        self.assertNotIn(
            "https://s.click.aliexpress.com/e/buyproduct", modified_message
        )

    def test_extract_domains_with_long_urls(self) -> None:
        """Test: Extract domains from long Amazon and AliExpress URLs."""
        # Text with long URLs already expanded
        message_text = (
            "Check out this Amazon deal: https://www.amazon.com/dp/B08XYZ123 "
            "and this AliExpress: https://es.aliexpress.com/item/12345.html"  ## We use a localized URL because expanding always, can change generic to local URL
        )

        # Call the function that processes the message
        domains, modified_message = extract_domains_from_message(message_text)

        # Verify that the correct domains were extracted
        self.assertIn("amazon.com", domains)  # Should find amazon.com
        self.assertIn("aliexpress.com", domains)  # Should find aliexpress.com

        # Verify that the full URLs are present in the modified message
        self.assertIn("https://www.amazon.com/dp/B08XYZ123", modified_message)
        self.assertIn(
            "aliexpress.com/item/12345.html", modified_message
        )  # Should find aliexpress.com (not checking exact subdomain, as it may expand to different regions)

        # Ensure there were no unnecessary modifications
        self.assertEqual(message_text, modified_message)


class TestExtractEmbeddedUrl(unittest.TestCase):
    """Tests for extract_embedded_url function."""

    def test_no_embedded_urls(self) -> None:
        """Test: No embedded URLs in the query parameters."""
        query_params = {"param1": ["value1"], "param2": ["value2"]}
        result = extract_embedded_url(query_params)
        self.assertEqual(result, set())  # Should return an empty set

    def test_single_embedded_url(self) -> None:
        """Test: A single embedded URL inside the query parameters."""
        query_params = {"param1": ["https://example.com/path?query=123"]}
        result = extract_embedded_url(query_params)
        self.assertIn("example.com", result)  # Should contain the domain 'example.com'

    def test_multiple_embedded_urls(self) -> None:
        """Test: Multiple embedded URLs in different query parameters."""
        query_params = {
            "param1": ["https://example.com/path"],
            "param2": ["https://another.com/resource"],
        }
        result = extract_embedded_url(query_params)
        self.assertIn("example.com", result)
        self.assertIn("another.com", result)
        self.assertEqual(len(result), 2)  # There should be two unique domains

    def test_invalid_urls(self) -> None:
        """Test: Invalid URLs in the query parameters should not be considered."""
        query_params = {
            "param1": ["ftp://invalid.com/file"],  # Not http/https
            "param2": ["invalid://notvalid"],
        }
        result = extract_embedded_url(query_params)
        self.assertEqual(result, set())  # Should return an empty set

    def test_mixed_valid_and_invalid_urls(self) -> None:
        """Test: A mix of valid and invalid URLs in the query parameters."""
        query_params = {
            "param1": ["https://valid.com/resource"],
            "param2": ["ftp://invalid.com/file"],  # Invalid scheme
            "param3": ["invalid://notvalid"],
        }
        result = extract_embedded_url(query_params)
        self.assertIn("valid.com", result)  # Only valid.com should be included
        self.assertEqual(len(result), 1)  # There should be only one valid domain

    def test_multiple_values_for_single_param(self) -> None:
        """Test: A single query parameter with multiple values (some valid URLs)."""
        query_params = {
            "param1": ["https://valid.com/resource", "https://another.com/path"]
        }
        result = extract_embedded_url(query_params)
        self.assertIn("valid.com", result)
        self.assertIn("another.com", result)
        self.assertEqual(len(result), 2)  # Two valid domains should be extracted


class TestPrepareMessage(unittest.TestCase):
    """Tests for prepare_message function."""

    @patch("botaffiumeiro.extract_domains_from_message")
    @patch("botaffiumeiro.select_user_for_domain")
    def test_prepare_message_with_valid_domains(
        self, mock_select_user: AsyncMock, mock_extract_domains: AsyncMock
    ) -> None:
        """Test: Simulate a message with valid domains and ensure users are selected correctly."""
        # Mock the domains extracted from the message
        mock_extract_domains.return_value = (
            {"amazon.com", "aliexpress.com"},
            "Modified message with expanded URLs",
        )

        # Define a function for side_effect to return users based on the domain
        def select_user_side_effect(domain: str) -> dict | None:
            if domain == "amazon.com":
                return {"user": "user1", "amazon_affiliate_id": "id_user1"}
            if domain == "aliexpress.com":
                return {"user": "user2", "aliexpress_affiliate_id": "id_user2"}
            return None

        # Assign the side_effect to the mock
        mock_select_user.side_effect = select_user_side_effect

        # Simulate a message object with text
        message = Mock()
        message.text = "Check out this Amazon link: https://amzn.to/abc123 and this AliExpress link: https://s.click.aliexpress.com/e/xyz789"

        # Call prepare_message to get the context
        context = prepare_message(message)

        # Check the returned context structure
        self.assertIsNotNone(context)
        self.assertEqual(context["message"], message)
        self.assertEqual(
            context["modified_message"], "Modified message with expanded URLs"
        )
        self.assertIn("amazon.com", context["selected_users"])
        self.assertEqual(context["selected_users"]["amazon.com"]["user"], "user1")

        self.assertIn("aliexpress.com", context["selected_users"])
        self.assertEqual(context["selected_users"]["aliexpress.com"]["user"], "user2")

    @patch("botaffiumeiro.extract_domains_from_message")
    @patch("botaffiumeiro.select_user_for_domain")
    def test_prepare_message_with_no_domains(
        self, mock_select_user: AsyncMock, mock_extract_domains: AsyncMock
    ) -> None:
        """Test: Handle a case where no valid domains are found in the message."""
        # Mock the domains extracted from the message (empty set and message unchanged)
        mock_extract_domains.return_value = (set(), "This message contains no links.")

        # Simulate a message object with text
        message = Mock()
        message.text = "This message contains no links."

        # Call the method to get the context
        context = prepare_message(message)

        # No domains, so the selected_users should be empty
        self.assertEqual(context["selected_users"], {})

        # Ensure the select_user_for_domain function was never called
        mock_select_user.assert_not_called()

        # Check that the message text was not changed
        self.assertEqual(context["modified_message"], "This message contains no links.")

    @patch("botaffiumeiro.extract_domains_from_message")
    @patch("botaffiumeiro.select_user_for_domain")
    def test_prepare_message_with_mixed_domains(
        self, mock_select_user: AsyncMock, mock_extract_domains: AsyncMock
    ) -> None:
        """Test: Simulate a message where one domain has a user and another domain does not."""
        # Mock the domains extracted from the message
        mock_extract_domains.return_value = (
            {
                "amazon.com",
                "unknown.com",
            },
            "Modified message with expanded URLs",
        )

        # Define a function for side_effect to return users based on the domain
        def select_user_side_effect(domain: str) -> dict | None:
            if domain == "amazon.com":
                return {"user": "user1", "amazon_affiliate_id": "id_user1"}
            if domain == "unknown.com":
                return None
            return None

        # Assign the side_effect to the mock
        mock_select_user.side_effect = select_user_side_effect

        # Simulate a message object with text
        message = Mock()
        message.text = (
            "Check out this Amazon link: https://amzn.to/abc123 and some unknown link."
        )

        # Call the method to get the context
        context = prepare_message(message)

        # Amazon should have a user selected
        self.assertIn("amazon.com", context["selected_users"])
        self.assertEqual(context["selected_users"]["amazon.com"]["user"], "user1")

        # Unknown domain should not appear in the selected users
        self.assertNotIn("unknown.com", context["selected_users"])

        # Verify the modified message
        self.assertEqual(
            context["modified_message"], "Modified message with expanded URLs"
        )

    @patch("botaffiumeiro.extract_domains_from_message")
    @patch("botaffiumeiro.select_user_for_domain")
    def test_prepare_message_with_only_unknown_domains(
        self, mock_select_user: AsyncMock, mock_extract_domains: AsyncMock
    ) -> None:
        """Test: Simulate a message where all domains are unknown."""
        # Mock the domains extracted from the message
        mock_extract_domains.return_value = (
            {"unknown.com"},
            "Modified message with expanded URLs",
        )

        # Mock the user selection for the unknown domain
        mock_select_user.return_value = None  # No user for unknown.com

        # Simulate a message object with text
        message = Mock()
        message.text = "This message contains an unknown domain link."

        # Call the method to get the context
        context = prepare_message(message)

        # Since there's no valid user for unknown.com, selected_users should be empty
        self.assertEqual(context["selected_users"], {})

        # Ensure the select_user_for_domain function was called once for the unknown domain
        mock_select_user.assert_called_once_with("unknown.com")

        # Verify the modified message
        self.assertEqual(
            context["modified_message"], "Modified message with expanded URLs"
        )

    @patch("botaffiumeiro.extract_domains_from_message")
    @patch("botaffiumeiro.select_user_for_domain")
    def test_prepare_message_with_expanded_urls(
        self, mock_select_user: AsyncMock, mock_extract_domains: AsyncMock
    ) -> None:
        """Test: Ensure that prepare_message returns both the selected users and the modified message."""
        # Mock the domains and the modified message returned by extract_domains_from_message
        mock_extract_domains.return_value = (
            {
                "amazon.com",
                "aliexpress.com",
            },
            "Modified message with expanded URLs",
        )

        # Define a function for side_effect to return users based on the domain
        def select_user_side_effect(domain: str) -> dict | None:
            if domain == "amazon.com":
                return {"user": "user1", "amazon_affiliate_id": "id_user1"}
            if domain == "aliexpress.com":
                return {"user": "user2", "aliexpress_affiliate_id": "id_user2"}
            return None

        # Assign the side_effect to the mock
        mock_select_user.side_effect = select_user_side_effect

        # Simulate a message object with text
        message = Mock()
        message.text = "Check out this Amazon link: https://amzn.to/abc123 and this AliExpress link: https://s.click.aliexpress.com/e/xyz789"

        # Call the method to get the context
        context = prepare_message(message)

        # Ensure select_user_for_domain was called with the correct domains
        mock_select_user.assert_any_call("amazon.com")
        mock_select_user.assert_any_call("aliexpress.com")

        # Verify selected users
        self.assertIn("amazon.com", context["selected_users"])
        self.assertEqual(context["selected_users"]["amazon.com"]["user"], "user1")

        self.assertIn("aliexpress.com", context["selected_users"])
        self.assertEqual(context["selected_users"]["aliexpress.com"]["user"], "user2")

        # Verify the modified message
        self.assertEqual(
            context["modified_message"], "Modified message with expanded URLs"
        )

    def test_prepare_message_with_no_text(self) -> None:
        """Test: Ensure that prepare_message returns an empty dictionary and None for the modified message when there is no text."""
        # Simulate an empty message
        message = Mock()
        message.text = None

        # Call the method to get the context
        context = prepare_message(message)

        # Verify that no users were selected and the modified message is None
        self.assertEqual(context["selected_users"], {})
        self.assertIsNone(context["modified_message"])


class TestSelectUserForDomain(unittest.TestCase):
    """Tests for select_user_for_domain function."""

    def test_select_user1(self) -> None:
        """Test: When random value is within the range of the second user."""
        mock_config_manager = Mock()
        mock_config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "user1", "percentage": 60},
                {"user": "user2", "percentage": 40},
            ]
        }
        mock_config_manager.all_users_configurations = {
            "user1": {"amazon_affiliate_id": "user1-affiliate-id"},
            "user2": {"amazon_affiliate_id": "user2-affiliate-id"},
        }

        with (
            patch("secrets.SystemRandom.uniform", return_value=50),
            patch("botaffiumeiro.config_manager", mock_config_manager),
        ):
            selected_user = select_user_for_domain("amazon")

        if selected_user is None:
            self.fail("select_user_for_domain returned None, but a user was expected.")
        self.assertEqual(selected_user["amazon_affiliate_id"], "user1-affiliate-id")

    def test_select_user2(self) -> None:
        """Test: When random value is within the range of the second user."""
        mock_config_manager = Mock()
        mock_config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "user1", "percentage": 60},
                {"user": "user2", "percentage": 40},
            ]
        }
        mock_config_manager.all_users_configurations = {
            "user1": {"amazon_affiliate_id": "user1-affiliate-id"},
            "user2": {"amazon_affiliate_id": "user2-affiliate-id"},
        }

        with (
            patch("secrets.SystemRandom.uniform", return_value=80),
            patch("botaffiumeiro.config_manager", mock_config_manager),
        ):
            selected_user = select_user_for_domain("amazon")

        if selected_user is None:
            self.fail("select_user_for_domain returned None, but a user was expected.")
        self.assertEqual(selected_user["amazon_affiliate_id"], "user2-affiliate-id")

    @patch(
        "botaffiumeiro.config_manager",  # Parchar el config_manager global
        new_callable=Mock,
    )
    def test_no_users_in_domain(self, mock_config_manager: AsyncMock) -> None:
        """Test: No users are available for the given domain. Should return None."""
        mock_config_manager.domain_percentage_table = {}

        selected_user = select_user_for_domain("nonexistent_domain")
        self.assertIsNone(selected_user)

    @patch(
        "botaffiumeiro.config_manager",  # Parchar el config_manager global
        new_callable=Mock,
    )
    def test_single_user(self, mock_config_manager: AsyncMock) -> None:
        """Test: Only one user is present, should always return that user."""
        mock_config_manager.domain_percentage_table = {
            "amazon": [{"user": "user1", "percentage": 100}]
        }
        mock_config_manager.all_users_configurations = {
            "user1": {"amazon_affiliate_id": "user1-affiliate-id"}
        }

        selected_user = select_user_for_domain("amazon")
        if selected_user is None:
            self.fail("select_user_for_domain returned None, but a user was expected.")
        self.assertEqual(selected_user["amazon_affiliate_id"], "user1-affiliate-id")

    @patch(
        "botaffiumeiro.config_manager",  # Parchar el config_manager global
        new_callable=Mock,
    )
    def test_zero_percentage_user(self, mock_config_manager: AsyncMock) -> None:
        """Test: One user has 0 percentage, should not be selected."""
        mock_config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "user1", "percentage": 0},
                {"user": "user2", "percentage": 100},
            ]
        }
        mock_config_manager.all_users_configurations = {
            "user1": {"amazon_affiliate_id": "user1-affiliate-id"},
            "user2": {"amazon_affiliate_id": "user2-affiliate-id"},
        }

        selected_user = select_user_for_domain("amazon")
        if selected_user is None:
            self.fail("select_user_for_domain returned None, but a user was expected.")
        self.assertEqual(selected_user["amazon_affiliate_id"], "user2-affiliate-id")

    @patch(
        "botaffiumeiro.config_manager",  # Parchar el config_manager global
        new_callable=Mock,
    )
    def test_fallback_to_first_user(self, mock_config_manager: AsyncMock) -> None:
        """Test: If no match is found in random selection, fallback to the first user."""
        mock_config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "user1", "percentage": 60},
                {"user": "user2", "percentage": 40},
            ]
        }
        mock_config_manager.all_users_configurations = {
            "user1": {"amazon_affiliate_id": "user1-affiliate-id"},
            "user2": {"amazon_affiliate_id": "user2-affiliate-id"},
        }

        with patch("secrets.SystemRandom.uniform", return_value=150):
            selected_user = select_user_for_domain("amazon")
        if selected_user is None:
            self.fail("select_user_for_domain returned None, but a user was expected.")
        self.assertEqual(selected_user["amazon_affiliate_id"], "user1-affiliate-id")


class TestExpandShortenedUrl(unittest.TestCase):
    """Tests for the expand_shortened_url function."""

    @patch("botaffiumeiro.requests.get")
    def test_url_with_trailing_period(self, mock_get: AsyncMock) -> None:
        """Test: Handle URLs with a trailing period."""
        mock_response = Mock()
        mock_response.url = "https://www.example.com/full-url"
        mock_get.return_value = mock_response

        # URL with a trailing period
        url = "https://short.url/example."

        expanded_url = expand_shortened_url(url)

        # Ensure requests.get is called with the stripped URL
        mock_get.assert_called_once_with(
            "https://short.url/example", allow_redirects=True, timeout=ANY
        )

        # Check that the expanded URL is correct
        self.assertEqual(expanded_url, "https://www.example.com/full-url")

    @patch("botaffiumeiro.requests.get")
    def test_url_with_trailing_comma(self, mock_get: AsyncMock) -> None:
        """Test: Handle URLs with a trailing comma."""
        mock_response = Mock()
        mock_response.url = "https://www.example.com/full-url"
        mock_get.return_value = mock_response

        # URL with a trailing comma
        url = "https://short.url/example,"

        expanded_url = expand_shortened_url(url)

        # Ensure requests.get is called with the stripped URL
        mock_get.assert_called_once_with(
            "https://short.url/example", allow_redirects=True, timeout=ANY
        )

        # Check that the expanded URL is correct
        self.assertEqual(expanded_url, "https://www.example.com/full-url")


if __name__ == "__main__":
    unittest.main()
