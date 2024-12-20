"""Convert json configuration file to yaml."""

import json
from pathlib import Path

import yaml  # type: ignore[import-untyped]

# File paths
json_file = Path("/data/options.json")
yaml_file = Path("/botaffiumeiro/data/config.yaml")

# Load the JSON file
with json_file.open("r") as f:
    data = json.load(f)

# Convert JSON into the desired YAML structure
config = {
    "telegram": {
        "bot_token": data.get("bot_token", ""),
        "delete_messages": data.get("delete_messages", True),
        "excluded_users": [user.get("id") for user in data.get("excluded_users", [])],
        "discount_keywords": [
            user.get("key") for user in data.get("discount_keywords", [])
        ],
    },
    "messages": {
        "affiliate_link_modified": data.get(
            "msg_affiliate_link_modified",
            "Here is the modified link with our affiliate program:",
        ),
        "reply_provided_by_user": data.get(
            "msg_reply_provided_by_user", "Reply provided by"
        ),
    },
    "amazon": {
        advertiser["domain"]: advertiser["id"] for advertiser in data.get("amazon", [])
    },
    "awin": {
        "publisher_id": data.get("awin_publisher_id", ""),
        "advertisers": {
            advertiser["domain"]: advertiser["id"]
            for advertiser in data.get("awin_adversiters", [])
        },
    },
    "admitad": {
        "publisher_id": data.get("admitad_publisher_id", ""),
        "advertisers": {
            advertiser["domain"]: advertiser["id"]
            for advertiser in data.get("admitad_adversiters", [])
        },
    },
    "tradedoubler": {
        "publisher_id": data.get("tradedoubler_publisher_id", ""),
        "advertisers": {
            advertiser["domain"]: advertiser["id"]
            for advertiser in data.get("tradedoubler_adversiters", [])
        },
    },
    "aliexpress": {
        "app_key": data.get("aliexpress_app_key", ""),
        "app_secret": data.get("aliexpress_app_secret", ""),
        "tracking_id": data.get("aliexpress_tracking_id", ""),
        "discount_codes": "\n".join(
            [code.get("line", "") for code in data.get("aliexpress_discount_codes", [])]
        ),
    },
    "log_level": data.get("log_level", "INFO"),
    "affiliate_settings": {
        "creator_affiliate_percentage": int(
            data.get("creator_affiliate_percentage", 10)
        ),
    },
}

# Save the YAML file
with yaml_file.open("w") as f:
    yaml.dump(config, f, allow_unicode=True, sort_keys=False)
