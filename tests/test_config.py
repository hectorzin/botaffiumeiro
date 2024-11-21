"""Tests for the configuration class ConfigurationManager."""
# ruff: noqa: SLF001

from __future__ import annotations

import unittest

from config import ConfigurationManager


class TestAddToDomainTable(unittest.TestCase):
    """Tests for _add_to_domain_table function."""

    def setUp(self) -> None:
        """Set up a fresh ConfigurationManager instance for each test."""
        self.config_manager = ConfigurationManager()

    def test_user_with_affiliate_id(self) -> None:
        """Test: Add a user with an affiliate ID."""
        user_id = "main"
        affiliate_id = "amazon_affiliate_id"
        self.config_manager._add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertIn("amazon", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 90
        )

    def test_user_without_affiliate_id(self) -> None:
        """Test: Do not add a user if they don't have an affiliate ID."""
        user_id = "main"
        affiliate_id = None
        self.config_manager._add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertNotIn("amazon", self.config_manager.domain_percentage_table)

    def test_new_domain_creation(self) -> None:
        """Test: Create a new domain in the table if it doesn't exist."""
        user_id = "main"
        affiliate_id = "user-affiliate-id"
        self.config_manager._add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertIn("amazon", self.config_manager.domain_percentage_table)
        self.assertEqual(len(self.config_manager.domain_percentage_table["amazon"]), 1)
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 90
        )

    def test_existing_domain_append(self) -> None:
        """Test: Add a user to an existing domain without duplicating the domain."""
        # First user
        user_id_1 = "user1"
        affiliate_id_1 = "user1-affiliate-id"
        self.config_manager._add_to_domain_table(
            "amazon", user_id_1, affiliate_id_1, 80
        )

        # Second user
        user_id_2 = "user2"
        affiliate_id_2 = "user2-affiliate-id"
        self.config_manager._add_to_domain_table(
            "amazon", user_id_2, affiliate_id_2, 20
        )

        # Verify that the domain "amazon" exists only once in the table
        self.assertEqual(len(self.config_manager.domain_percentage_table), 1)
        self.assertIn("amazon", self.config_manager.domain_percentage_table)

        # Verify that two users have been added to the existing domain
        self.assertEqual(len(self.config_manager.domain_percentage_table["amazon"]), 2)

        # Check that the users and their percentages are correct
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "user1"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 80
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "user2"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 20
        )

    def test_multiple_users_in_same_domain(self) -> None:
        """Test: Add multiple users to the same domain."""
        # User 1
        user_id_1 = "user1"
        affiliate_id_1 = "user1-affiliate-id"
        self.config_manager._add_to_domain_table(
            "amazon", user_id_1, affiliate_id_1, 60
        )

        # User 2
        user_id_2 = "user2"
        affiliate_id_2 = "user2-affiliate-id"
        self.config_manager._add_to_domain_table(
            "amazon", user_id_2, affiliate_id_2, 30
        )

        # User 3
        user_id_3 = "user3"
        affiliate_id_3 = "user3-affiliate-id"
        self.config_manager._add_to_domain_table(
            "amazon", user_id_3, affiliate_id_3, 10
        )

        self.assertEqual(len(self.config_manager.domain_percentage_table), 1)
        self.assertEqual(len(self.config_manager.domain_percentage_table["amazon"]), 3)
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "user1"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "user2"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][2]["user"], "user3"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 60
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 30
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][2]["percentage"], 10
        )


class TestAddAffiliateStoresDomains(unittest.TestCase):
    """Tests for _add_affiliate_stores_domains function."""

    def setUp(self) -> None:
        """Set up a fresh ConfigurationManager instance for each test."""
        self.config_manager = ConfigurationManager()

    def test_no_advertisers(self) -> None:
        """Test: No advertisers for the store key. The table should remain empty."""
        user_id = "main"
        user_data: dict[str, str] = {}  # No advertisers
        self.config_manager._add_affiliate_stores_domains(
            user_id, user_data, "awin_advertisers", 50
        )

        # The table should remain empty because there are no advertisers
        self.assertEqual(len(self.config_manager.domain_percentage_table), 0)

    def test_single_advertiser(self) -> None:
        """Test: Add a single advertiser to the domain_percentage_table."""
        user_id = "main"
        advertisers = {
            "example.com": "affiliate-id",
        }
        self.config_manager._add_affiliate_stores_domains(
            user_id, advertisers, "awin", 50
        )

        # The table should contain the new domain (example.com) with the user and their percentage
        self.assertIn("example.com", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["user"],
            "main",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["percentage"],
            50,
        )

    def test_multiple_advertisers(self) -> None:
        """Test: Add multiple advertisers to the domain_percentage_table."""
        user_id = "main"
        advertisers = {
            "example1.com": "affiliate-id1",
            "example2.com": "affiliate-id2",
        }
        self.config_manager._add_affiliate_stores_domains(
            user_id, advertisers, "awin", 50
        )

        # The table should contain both domains with the user and their percentage
        self.assertIn("example1.com", self.config_manager.domain_percentage_table)
        self.assertIn("example2.com", self.config_manager.domain_percentage_table)

        # Check the data for both domains
        self.assertEqual(
            self.config_manager.domain_percentage_table["example1.com"][0]["user"],
            "main",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example1.com"][0][
                "percentage"
            ],
            50,
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["example2.com"][0]["user"],
            "main",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example2.com"][0][
                "percentage"
            ],
            50,
        )

    def test_existing_domain_append(self) -> None:
        """Test: Append a new user to an existing domain without overwriting."""
        # Pre-populate the table with one user for "example.com"
        self.config_manager.domain_percentage_table = {
            "example.com": [{"user": "existing_user", "percentage": 60}]
        }

        # Now add a new user to the same domain
        user_id = "new_user"
        advertisers = {"example.com": "new-affiliate-id"}
        self.config_manager._add_affiliate_stores_domains(
            user_id, advertisers, "awin", 40
        )

        # Check that the domain now has both users
        self.assertEqual(
            len(self.config_manager.domain_percentage_table["example.com"]), 2
        )

        # Verify that both users and their percentages are correct
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["user"],
            "existing_user",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["percentage"],
            60,
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][1]["user"],
            "new_user",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][1]["percentage"],
            40,
        )

    def test_different_percentages(self) -> None:
        """Test: Add different users with different percentages for the same advertiser."""
        # First user with 70% for "example.com"
        user_id_1 = "user1"
        advertisers_1 = {"example.com": "affiliate-id1"}
        self.config_manager._add_affiliate_stores_domains(
            user_id_1, advertisers_1, "awin", 70
        )

        # Second user with 30% for "example.com"
        user_id_2 = "user2"
        advertisers_2 = {"example.com": "affiliate-id2"}
        self.config_manager._add_affiliate_stores_domains(
            user_id_2, advertisers_2, "awin", 30
        )

        # Check that both users have been added to the same domain with correct percentages
        self.assertEqual(
            len(self.config_manager.domain_percentage_table["example.com"]), 2
        )

        # Check first user
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["user"],
            "user1",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][0]["percentage"],
            70,
        )

        # Check second user
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][1]["user"],
            "user2",
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["example.com"][1]["percentage"],
            30,
        )


class TestAddUserToDomainPercentageTable(unittest.TestCase):
    """Tests for _add_user_to_domain_percentage_table function."""

    def setUp(self) -> None:
        """Set up a fresh ConfigurationManager instance for each test."""
        self.config_manager = ConfigurationManager()

    def test_no_affiliate_ids(self) -> None:
        """Test: No affiliate IDs provided for the user. The table should remain empty."""
        user_id = "user"
        user_data = {
            "amazon": {"advertisers": {}},
            "aliexpress": {"app_key": None},
            "awin": {"advertisers": {}},
            "admitad": {"advertisers": {}},
        }
        self.config_manager._add_user_to_domain_percentage_table(user_id, user_data, 50)

        self.assertEqual(len(self.config_manager.domain_percentage_table), 0)

    def test_amazon_affiliate_id(self) -> None:
        """Test: The user has an Amazon affiliate ID. The table should be updated with Amazon."""
        user_id = "main"
        user_data = {
            "amazon": {"advertisers": {"amazon.es": "amazon-affiliate-id"}},
            "aliexpress": {"app_key": None},
            "awin": {"advertisers": {}},
            "admitad": {"advertisers": {}},
        }
        self.config_manager._add_user_to_domain_percentage_table(user_id, user_data, 50)

        self.assertIn("amazon.es", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon.es"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon.es"][0]["percentage"],
            50,
        )

    def test_multiple_affiliate_ids(self) -> None:
        """Test: The user has IDs for Amazon, AliExpress, and advertisers in Awin and Admitad."""
        user_id = "main"
        user_data = {
            "amazon": {"advertisers": {"amazon.es": "amazon-affiliate-id"}},
            "aliexpress": {"app_key": "aliexpress-app-key"},
            "awin": {"advertisers": {"awin-example.com": "awin-affiliate-id"}},
            "admitad": {"advertisers": {"admitad-example.com": "admitad-affiliate-id"}},
        }
        self.config_manager._add_user_to_domain_percentage_table(user_id, user_data, 50)

        # Amazon
        self.assertIn("amazon.es", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon.es"][0]["user"], "main"
        )

        # AliExpress
        self.assertIn("aliexpress.com", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["aliexpress.com"][0]["user"],
            "main",
        )

        # Awin
        self.assertIn("awin-example.com", self.config_manager.domain_percentage_table)
        self.assertEqual(
            self.config_manager.domain_percentage_table["awin-example.com"][0]["user"],
            "main",
        )

        # Admitad
        self.assertIn(
            "admitad-example.com", self.config_manager.domain_percentage_table
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["admitad-example.com"][0][
                "user"
            ],
            "main",
        )

    def test_multiple_users_same_domains(self) -> None:
        """Test: Multiple users with affiliate data for the same domains."""
        # First user
        user_id_1 = "user1"
        user_data_1 = {
            "amazon": {"advertisers": {"amazon.es": "amazon-affiliate-id"}},
            "aliexpress": {"app_key": "aliexpress-app-key-1"},
        }
        self.config_manager._add_user_to_domain_percentage_table(
            user_id_1, user_data_1, 60
        )

        # Second user
        user_id_2 = "user2"
        user_data_2 = {
            "amazon": {"advertisers": {"amazon.es": "amazon-affiliate-id-2"}},
            "aliexpress": {"app_key": "aliexpress-app-key-2"},
        }
        self.config_manager._add_user_to_domain_percentage_table(
            user_id_2, user_data_2, 40
        )

        # Amazon
        self.assertIn("amazon.es", self.config_manager.domain_percentage_table)
        self.assertEqual(
            len(self.config_manager.domain_percentage_table["amazon.es"]), 2
        )

        # AliExpress
        self.assertIn("aliexpress.com", self.config_manager.domain_percentage_table)
        self.assertEqual(
            len(self.config_manager.domain_percentage_table["aliexpress.com"]), 2
        )

    def test_multiple_users_with_shared_and_unique_domains(self) -> None:
        """Test: Multiple users where some domains overlap and others are unique."""
        user_1 = {"amazon": {"advertisers": {"amazon.es": "id1"}}, "awin": {}}
        user_2 = {"aliexpress": {"app_key": "key2"}}
        user_3 = {"amazon": {"advertisers": {"amazon.es": "id3"}}, "awin": {}}

        self.config_manager._add_user_to_domain_percentage_table("user1", user_1, 70)
        self.config_manager._add_user_to_domain_percentage_table("user2", user_2, 30)
        self.config_manager._add_user_to_domain_percentage_table("user3", user_3, 50)

        self.assertIn("amazon.es", self.config_manager.domain_percentage_table)
        self.assertIn("aliexpress.com", self.config_manager.domain_percentage_table)

    def test_multiple_users_with_aliexpress_on_different_platforms(self) -> None:
        """Test: Multiple users with AliExpress affiliate IDs from different platforms."""
        user_1 = {"aliexpress": {"app_key": "api-key"}}
        user_2 = {"awin": {"advertisers": {"aliexpress.com": "awin-id"}}}
        user_3 = {"admitad": {"advertisers": {"aliexpress.com": "admitad-id"}}}

        self.config_manager._add_user_to_domain_percentage_table("user1", user_1, 50)
        self.config_manager._add_user_to_domain_percentage_table("user2", user_2, 30)
        self.config_manager._add_user_to_domain_percentage_table("user3", user_3, 20)

        self.assertIn("aliexpress.com", self.config_manager.domain_percentage_table)
        self.assertEqual(
            len(self.config_manager.domain_percentage_table["aliexpress.com"]), 3
        )


class TestAdjustDomainAffiliatePercentages(unittest.TestCase):
    """Tests for _adjust_domain_affiliate_percentages function."""

    def setUp(self) -> None:
        """Set up a fresh ConfigurationManager instance for each test."""
        self.config_manager = ConfigurationManager()

    def test_only_user_in_domain(self) -> None:
        """Test: Only the main user is in the domain. The user should get 100% of the percentage."""
        creator_percentage = 0
        self.config_manager.domain_percentage_table = {
            "amazon": [{"user": "main", "percentage": 100}]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 100
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    def test_user_and_single_creator(self) -> None:
        """Test: One user and one creator. Percentages should adjust based on creator_percentage."""
        creator_percentage = 30
        self.config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": 70},
                {"user": "creator1", "percentage": 30},
            ]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 70
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 30
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    def test_user_and_multiple_creators(self) -> None:
        """Test: One user and multiple creators. Percentages should adjust according to creator_percentage."""
        creator_percentage = 30
        self.config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": 70},
                {"user": "creator1", "percentage": 60},
                {"user": "creator2", "percentage": 40},
            ]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 70
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertAlmostEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 18
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][2]["user"], "creator2"
        )
        self.assertAlmostEqual(
            self.config_manager.domain_percentage_table["amazon"][2]["percentage"], 12
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    def test_only_creators_in_domain(self) -> None:
        """Test: No main user, only creators. The creators should be adjusted to sum to 100%."""
        creator_percentage = 10
        self.config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "creator1", "percentage": 60},
                {"user": "creator2", "percentage": 40},
            ]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "creator1"
        )
        self.assertAlmostEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 60
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "creator2"
        )
        self.assertAlmostEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 40
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    def test_user_with_zero_creator_percentage(self) -> None:
        """Test: User with 0% creator influence. The user should get 100%."""
        creator_percentage = 0
        self.config_manager.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": 100},
                {"user": "creator1", "percentage": 100},
            ]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][0]["percentage"], 100
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon"][1]["percentage"], 0
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    def test_main_user_only(self) -> None:
        """Test: The main user is the only one in the domain. The user should get 100% of the percentage."""
        creator_percentage = 10
        self.config_manager.domain_percentage_table = {
            "amazon.com": [{"user": "main", "percentage": 100}]
        }

        self.config_manager._adjust_domain_affiliate_percentages(
            "amazon.com", creator_percentage
        )

        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon.com"][0]["user"], "main"
        )
        self.assertEqual(
            self.config_manager.domain_percentage_table["amazon.com"][0]["percentage"],
            100,
        )
        total_percentage = sum(
            entry["percentage"]
            for entry in self.config_manager.domain_percentage_table["amazon.com"]
        )
        self.assertEqual(total_percentage, 100)


if __name__ == "__main__":
    unittest.main()
