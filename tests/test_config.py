import unittest
import config
from unittest.mock import patch


class TestAddToDomainTable(unittest.TestCase):

    @patch("config.domain_percentage_table", {})
    def test_user_with_affiliate_id(self):
        """
        Test: Add a user with an affiliate ID.
        """
        user_id = "main"
        affiliate_id = "amazon_affiliate_id"
        config.add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertIn("amazon", config.domain_percentage_table)
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 90)

    @patch("config.domain_percentage_table", {})
    def test_user_without_affiliate_id(self):
        """
        Test: Do not add a user if they don't have an affiliate ID.
        """
        user_id = "main"
        affiliate_id = None
        config.add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertNotIn("amazon", config.domain_percentage_table)

    @patch("config.domain_percentage_table", {})
    def test_new_domain_creation(self):
        """
        Test: Create a new domain in the table if it doesn't exist.
        """
        user_id = "main"
        affiliate_id = "user-affiliate-id"
        config.add_to_domain_table("amazon", user_id, affiliate_id, 90)

        self.assertIn("amazon", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["amazon"]), 1)
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 90)

    @patch("config.domain_percentage_table", {})
    def test_existing_domain_append(self):
        """
        Test: Add a user to an existing domain without duplicating the domain.
        """
        # First user
        user_id_1 = "user1"
        affiliate_id_1 = "user1-affiliate-id"
        config.add_to_domain_table("amazon", user_id_1, affiliate_id_1, 80)

        # Second user
        user_id_2 = "user2"
        affiliate_id_2 = "user2-affiliate-id"
        config.add_to_domain_table("amazon", user_id_2, affiliate_id_2, 20)

        # Verify that the domain "amazon" exists only once in the table
        self.assertEqual(len(config.domain_percentage_table), 1)
        self.assertIn("amazon", config.domain_percentage_table)

        # Verify that two users have been added to the existing domain
        self.assertEqual(len(config.domain_percentage_table["amazon"]), 2)

        # Check that the users and their percentages are correct
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "user1")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 80)

        self.assertEqual(config.domain_percentage_table["amazon"][1]["user"], "user2")
        self.assertEqual(config.domain_percentage_table["amazon"][1]["percentage"], 20)

    @patch("config.domain_percentage_table", {})
    def test_multiple_users_in_same_domain(self):
        """
        Test: Add multiple users to the same domain.
        """
        # User 1
        user_id_1 = "user1"
        affiliate_id_1 = "user1-affiliate-id"
        config.add_to_domain_table("amazon", user_id_1, affiliate_id_1, 60)

        # User 2
        user_id_2 = "user2"
        affiliate_id_2 = "user2-affiliate-id"
        config.add_to_domain_table("amazon", user_id_2, affiliate_id_2, 30)

        # User 3
        user_id_3 = "user3"
        affiliate_id_3 = "user3-affiliate-id"
        config.add_to_domain_table("amazon", user_id_3, affiliate_id_3, 10)

        self.assertEqual(len(config.domain_percentage_table), 1)
        self.assertEqual(len(config.domain_percentage_table["amazon"]), 3)
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "user1")
        self.assertEqual(config.domain_percentage_table["amazon"][1]["user"], "user2")
        self.assertEqual(config.domain_percentage_table["amazon"][2]["user"], "user3")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 60)
        self.assertEqual(config.domain_percentage_table["amazon"][1]["percentage"], 30)
        self.assertEqual(config.domain_percentage_table["amazon"][2]["percentage"], 10)


class TestAddAffiliateStoresDomains(unittest.TestCase):

    @patch("config.domain_percentage_table", {})
    def test_no_advertisers(self):
        """
        Test: No advertisers for the store key. The table should remain empty.
        """
        user_id = "main"
        user_data = {"awin_advertisers": {}}  # No advertisers
        config.add_affiliate_stores_domains(user_id, user_data, "awin_advertisers", 50)

        # The table should remain empty because there are no advertisers
        self.assertEqual(len(config.domain_percentage_table), 0)

    @patch("config.domain_percentage_table", {})
    def test_single_advertiser(self):
        """
        Test: Add a single advertiser to the domain_percentage_table.
        """
        user_id = "main"
        advertisers = {
            "example.com": "affiliate-id",
        }
        config.add_affiliate_stores_domains(user_id, advertisers, "awin", 50)

        # The table should contain the new domain (example.com) with the user and their percentage
        self.assertIn("example.com", config.domain_percentage_table)
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["percentage"], 50
        )

    @patch("config.domain_percentage_table", {})
    def test_multiple_advertisers(self):
        """
        Test: Add multiple advertisers to the domain_percentage_table.
        """
        user_id = "main"
        advertisers = {
            "example1.com": "affiliate-id1",
            "example2.com": "affiliate-id2",
        }
        config.add_affiliate_stores_domains(user_id, advertisers, "awin", 50)

        # The table should contain both domains with the user and their percentage
        self.assertIn("example1.com", config.domain_percentage_table)
        self.assertIn("example2.com", config.domain_percentage_table)

        # Check the data for both domains
        self.assertEqual(
            config.domain_percentage_table["example1.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["example1.com"][0]["percentage"], 50
        )

        self.assertEqual(
            config.domain_percentage_table["example2.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["example2.com"][0]["percentage"], 50
        )

    @patch("config.domain_percentage_table", {})
    def test_existing_domain_append(self):
        """
        Test: Append a new user to an existing domain without overwriting.
        """
        # Pre-populate the table with one user for "example.com"
        config.domain_percentage_table = {
            "example.com": [{"user": "existing_user", "percentage": 60}]
        }

        # Now add a new user to the same domain
        user_id = "new_user"
        adversiters = {"example.com": "new-affiliate-id"}
        config.add_affiliate_stores_domains(user_id, adversiters, "awin", 40)

        # Check that the domain now has both users
        self.assertEqual(len(config.domain_percentage_table["example.com"]), 2)

        # Verify that both users and their percentages are correct
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["user"], "existing_user"
        )
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["percentage"], 60
        )

        self.assertEqual(
            config.domain_percentage_table["example.com"][1]["user"], "new_user"
        )
        self.assertEqual(
            config.domain_percentage_table["example.com"][1]["percentage"], 40
        )

    @patch("config.domain_percentage_table", {})
    def test_different_percentages(self):
        """
        Test: Add different users with different percentages for the same advertiser.
        """
        # First user with 70% for "example.com"
        user_id_1 = "user1"
        adversiters_1 = {"example.com": "affiliate-id1"}
        config.add_affiliate_stores_domains(user_id_1, adversiters_1, "awin", 70)

        # Second user with 30% for "example.com"
        user_id_2 = "user2"
        adversiters_2 = {"example.com": "affiliate-id2"}
        config.add_affiliate_stores_domains(user_id_2, adversiters_2, "awin", 30)

        # Check that both users have been added to the same domain with correct percentages
        self.assertEqual(len(config.domain_percentage_table["example.com"]), 2)

        # Check first user
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["user"], "user1"
        )
        self.assertEqual(
            config.domain_percentage_table["example.com"][0]["percentage"], 70
        )

        # Check second user
        self.assertEqual(
            config.domain_percentage_table["example.com"][1]["user"], "user2"
        )
        self.assertEqual(
            config.domain_percentage_table["example.com"][1]["percentage"], 30
        )


class TestAddUserToDomainPercentageTable(unittest.TestCase):

    @patch("config.domain_percentage_table", {})
    def test_no_affiliate_ids(self):
        """
        Test: No affiliate IDs provided for the user. The table should remain empty.
        """
        user_id = "user"
        user_data = {
            "amazon": {
                "advertisers": {}
            },
            "aliexpress": {
                "app_key": None
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id, user_data, 50)

        # The table should remain empty as the user has no affiliate data
        self.assertEqual(len(config.domain_percentage_table), 0)

    @patch("config.domain_percentage_table", {})
    def test_amazon_affiliate_id(self):
        """
        Test: The user has an Amazon affiliate ID. The table should be updated with Amazon.
        """
        user_id = "main"
        user_data = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id"}
            },
            "aliexpress": {
                "app_key": None
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id, user_data, 50)

        # Amazon should be added to the table
        self.assertIn("amazon.es", config.domain_percentage_table)
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["percentage"], 50)

    @patch("config.domain_percentage_table", {})
    def test_multiple_affiliate_ids(self):
        """
        Test: The user has IDs for Amazon, AliExpress, and advertisers in Awin and Admitad.
        """
        user_id = "main"
        user_data = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id"}
            },
            "aliexpress": {
                "app_key": "aliexpress-app-key"
            },
            "awin": {
                "advertisers": {
                    "awin-example.com": "awin-affiliate-id"
                }
            },
            "admitad": {
                "advertisers": {
                    "admitad-example.com": "admitad-affiliate-id"
                }
            }
        }
        config.add_user_to_domain_percentage_table(user_id, user_data, 50)

        # Amazon should be added
        self.assertIn("amazon.es", config.domain_percentage_table)
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["percentage"], 50)

        # AliExpress should be added
        self.assertIn("aliexpress.com", config.domain_percentage_table)
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["percentage"], 50
        )

        # Awin advertiser should be added
        self.assertIn("awin-example.com", config.domain_percentage_table)
        self.assertEqual(
            config.domain_percentage_table["awin-example.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["awin-example.com"][0]["percentage"], 50
        )

        # Admitad advertiser should be added
        self.assertIn("admitad-example.com", config.domain_percentage_table)
        self.assertEqual(
            config.domain_percentage_table["admitad-example.com"][0]["user"], "main"
        )
        self.assertEqual(
            config.domain_percentage_table["admitad-example.com"][0]["percentage"], 50
        )

    @patch("config.domain_percentage_table", {})
    def test_multiple_users_same_domains(self):
        """
        Test: Multiple users with affiliate data for the same domains.
        """
        # First user with Amazon and AliExpress
        user_id_1 = "user1"
        user_data_1 = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id"}
            },
            "aliexpress": {
                "app_key": "aliexpress-app-key-1"
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_1, user_data_1, 60)

        # Second user with the same domains but different IDs
        user_id_2 = "user2"
        user_data_2 = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id-2"}
            },
            "aliexpress": {
                "app_key": "aliexpress-app-key-2"
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_2, user_data_2, 40)

        # Amazon should have two users
        self.assertIn("amazon.es", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["amazon.es"]), 2)

        # Check both users in Amazon
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["user"], "user1")
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["percentage"], 60)

        self.assertEqual(config.domain_percentage_table["amazon.es"][1]["user"], "user2")
        self.assertEqual(config.domain_percentage_table["amazon.es"][1]["percentage"], 40)

        # AliExpress should have two users
        self.assertIn("aliexpress.com", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["aliexpress.com"]), 2)

        # Check both users in AliExpress
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["user"], "user1"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["percentage"], 60
        )

        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["user"], "user2"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["percentage"], 40
        )

    @patch("config.domain_percentage_table", {})
    def test_multiple_users_with_shared_and_unique_domains(self):
        """
        Test: Multiple users where some domains overlap and others are unique.
        """
        # First user with Amazon and an Awin advertiser
        user_id_1 = "user1"
        user_data_1 = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id-1"}
            },
            "aliexpress": {
                "app_key": None
            },
            "awin": {
                "advertisers": {
                    "awin-user1.com": "awin-affiliate-id-1"
                }
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_1, user_data_1, 70)

        # Second user with AliExpress and an Admitad advertiser (no Amazon)
        user_id_2 = "user2"
        user_data_2 = {
            "amazon": {
                "advertisers": {}
            },
            "aliexpress": {
                "app_key": "aliexpress-app-key-2"
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {
                    "admitad-user2.com": "admitad-affiliate-id-2"
                }
            }
        }
        config.add_user_to_domain_percentage_table(user_id_2, user_data_2, 30)

        # Third user with Amazon and AliExpress (shared with the first and second users)
        user_id_3 = "user3"
        user_data_3 = {
            "amazon": {
                "advertisers": {"amazon.es":"amazon-affiliate-id-3"}
            },
            "aliexpress": {
                "app_key": "aliexpress-app-key-3"
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_3, user_data_3, 50)

        # Verify that the domain_percentage_table contains the correct domains and users

        # Amazon should have 2 users (user1 and user3)
        self.assertIn("amazon.es", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["amazon.es"]), 2)

        # Check user1 and user3 in Amazon
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["user"], "user1")
        self.assertEqual(config.domain_percentage_table["amazon.es"][0]["percentage"], 70)

        self.assertEqual(config.domain_percentage_table["amazon.es"][1]["user"], "user3")
        self.assertEqual(config.domain_percentage_table["amazon.es"][1]["percentage"], 50)

        # AliExpress should have 2 users (user2 and user3)
        self.assertIn("aliexpress.com", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["aliexpress.com"]), 2)

        # Check user2 and user3 in AliExpress
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["user"], "user2"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["percentage"], 30
        )

        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["user"], "user3"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["percentage"], 50
        )

        # Awin should have only user1
        self.assertIn("awin-user1.com", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["awin-user1.com"]), 1)

        # Check user1 in Awin
        self.assertEqual(
            config.domain_percentage_table["awin-user1.com"][0]["user"], "user1"
        )
        self.assertEqual(
            config.domain_percentage_table["awin-user1.com"][0]["percentage"], 70
        )

        # Admitad should have only user2
        self.assertIn("admitad-user2.com", config.domain_percentage_table)
        self.assertEqual(len(config.domain_percentage_table["admitad-user2.com"]), 1)

        # Check user2 in Admitad
        self.assertEqual(
            config.domain_percentage_table["admitad-user2.com"][0]["user"], "user2"
        )
        self.assertEqual(
            config.domain_percentage_table["admitad-user2.com"][0]["percentage"], 30
        )

    @patch("config.domain_percentage_table", {})
    def test_multiple_users_with_aliexpress_on_different_platforms(self):
        """
        Test: Multiple users with AliExpress affiliate IDs from different platforms (API, Awin, Admitad).
        """
        # First user has AliExpress via API
        user_id_1 = "user1"
        user_data_1 = {
            "amazon": {
                "advertisers": {}
            },
            "aliexpress": {
                "app_key": "aliexpress-api-key"
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_1, user_data_1, 50)

        # Second user has AliExpress via Awin
        user_id_2 = "user2"
        user_data_2 = {
            "amazon": {
                "affiliate_id": None
            },
            "aliexpress": {
                "app_key": None
            },
            "awin": {
                "advertisers": {
                    "aliexpress.com": "awin-aliexpress-id"
                }
            },
            "admitad": {
                "advertisers": {}
            }
        }
        config.add_user_to_domain_percentage_table(user_id_2, user_data_2, 30)

        # Third user has AliExpress via Admitad
        user_id_3 = "user3"
        user_data_3 = {
            "amazon": {
                "affiliate_id": None
            },
            "aliexpress": {
                "app_key": None
            },
            "awin": {
                "advertisers": {}
            },
            "admitad": {
                "advertisers": {
                    "aliexpress.com": "admitad-aliexpress-id"
                }
            }
        }
        config.add_user_to_domain_percentage_table(user_id_3, user_data_3, 20)

        # Now verify the domain_percentage_table contains the correct entries for aliexpress.com
        self.assertIn("aliexpress.com", config.domain_percentage_table)

        # Check that three users are associated with aliexpress.com
        self.assertEqual(len(config.domain_percentage_table["aliexpress.com"]), 3)

        # Check each user's data for aliexpress.com
        # First user via AliExpress API
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["user"], "user1"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][0]["percentage"], 50
        )

        # Second user via Awin
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["user"], "user2"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][1]["percentage"], 30
        )

        # Third user via Admitad
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][2]["user"], "user3"
        )
        self.assertEqual(
            config.domain_percentage_table["aliexpress.com"][2]["percentage"], 20
        )


class TestAdjustDomainAffiliatePercentages(unittest.TestCase):

    @patch("config.domain_percentage_table", {})
    def test_only_user_in_domain(self):
        """
        Test: Only the main user is in the domain. The user should get 100% of the percentage.
        """
        creator_percentage = 0
        user_percentage =100 - creator_percentage
        config.domain_percentage_table = {
            "amazon": [{"user": "main", "percentage": user_percentage}]
        }
        config.adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )  # No creator influence, feo feo 🤣

        # The user's percentage should remain 100%
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 100)

        # Verify that the total percentage sums to 100%
        total_percentage = sum(
            entry["percentage"] for entry in config.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    @patch("config.domain_percentage_table", {})
    def test_user_and_single_creator(self):
        """
        Test: One user and one creator. Percentages should adjust based on creator_percentage.
        """
        creator_percentage = 30
        user_percentage =100 - creator_percentage
        config.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": user_percentage},
                {"user": "creator1", "percentage": 100},
            ]
        }
        original_user_percentage = config.domain_percentage_table["amazon"][0][
            "percentage"
        ]

        config.adjust_domain_affiliate_percentages("amazon", creator_percentage)

        # The user's percentage should be 70% and the creator's should be 30%
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 70)

        self.assertEqual(
            config.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertEqual(config.domain_percentage_table["amazon"][1]["percentage"], 30)

        # Verify that the total percentage sums to 100%
        total_percentage = sum(
            entry["percentage"] for entry in config.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

        # Verify that the original percentage of the user has not changed before adjustment
        self.assertEqual(original_user_percentage, 70)

    @patch("config.domain_percentage_table", {})
    def test_user_and_multiple_creators(self):
        """
        Test: One user and multiple creators. Percentages should adjust according to creator_percentage.
        """
        creator_percentage = 30

        config.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": 100 - creator_percentage},
                {"user": "creator1", "percentage": 60},
                {"user": "creator2", "percentage": 40},
            ]
        }
        original_user_percentage = config.domain_percentage_table["amazon"][0][
            "percentage"
        ]

        config.adjust_domain_affiliate_percentages("amazon", creator_percentage)

        # User should get 60% and the creators' percentages should adjust accordingly
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 70)

        # Creator percentages should adjust to their relative share of 30%
        self.assertEqual(
            config.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertAlmostEqual(
            config.domain_percentage_table["amazon"][1]["percentage"], 18
        )

        self.assertEqual(
            config.domain_percentage_table["amazon"][2]["user"], "creator2"
        )
        self.assertAlmostEqual(
            config.domain_percentage_table["amazon"][2]["percentage"], 12
        )

        # Verify that the total percentage sums to 100%
        total_percentage = sum(
            entry["percentage"] for entry in config.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

        # Verify that the original percentage of the user has not changed before adjustment
        self.assertEqual(original_user_percentage, 70)

    @patch("config.domain_percentage_table", {})
    def test_only_creators_in_domain(self):
        """
        Test: No main user, only creators. The creators should be adjusted to sum to 100%.
        """
        creator_percentage = 10
        config.domain_percentage_table = {
            "amazon": [
                {"user": "creator1", "percentage": 60},
                {"user": "creator2", "percentage": 40},
            ]
        }
        config.adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )  # All goes to creators

        # The percentages should remain proportional but sum to 100%
        self.assertEqual(
            config.domain_percentage_table["amazon"][0]["user"], "creator1"
        )
        self.assertAlmostEqual(
            config.domain_percentage_table["amazon"][0]["percentage"], 60, places=2
        )

        self.assertEqual(
            config.domain_percentage_table["amazon"][1]["user"], "creator2"
        )
        self.assertAlmostEqual(
            config.domain_percentage_table["amazon"][1]["percentage"], 40, places=2
        )

        # Verify that the total percentage sums to 100%
        total_percentage = sum(
            entry["percentage"] for entry in config.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

    @patch("config.domain_percentage_table", {})
    def test_user_with_zero_creator_percentage(self):
        """
        Test: User with 0% creator influence. The user should get 100%.
        """
        creator_percentage = 0
        config.domain_percentage_table = {
            "amazon": [
                {"user": "main", "percentage": 100 - creator_percentage},
                {"user": "creator1", "percentage": 100},
            ]
        }
        original_user_percentage = config.domain_percentage_table["amazon"][0][
            "percentage"
        ]

        config.adjust_domain_affiliate_percentages(
            "amazon", creator_percentage
        )  # 0% influence for creators

        # The user should get 100% and the creator should get 0%
        self.assertEqual(config.domain_percentage_table["amazon"][0]["user"], "main")
        self.assertEqual(config.domain_percentage_table["amazon"][0]["percentage"], 100)

        self.assertEqual(
            config.domain_percentage_table["amazon"][1]["user"], "creator1"
        )
        self.assertEqual(config.domain_percentage_table["amazon"][1]["percentage"], 0)

        # Verify that the total percentage sums to 100%
        total_percentage = sum(
            entry["percentage"] for entry in config.domain_percentage_table["amazon"]
        )
        self.assertEqual(total_percentage, 100)

        # Verify that the original percentage of the user has not changed before adjustment
        self.assertEqual(original_user_percentage, 100)


if __name__ == "__main__":
    unittest.main()
