from handlers.base_handler import PATTERN_URL_QUERY

PATTERNS = {
    "amazon": {
        "pattern": (
            r"(https?://(?:www\.)?(?:amazon\.[a-z]{2,3}(?:\.[a-z]{2})?|amzn\.to|amzn\.eu)"
            + PATTERN_URL_QUERY
            + ")"
        ),
        "format_template": "{domain}{path_before_query}?tag={advertiser_id}",
        "affiliate_tag": None,
    },
    "awin": {
        "pattern": (
            r"(https?://(?:[\w\-]+\.)?awin1\.com/cread\.php\?" + PATTERN_URL_QUERY + ")"
        ),
        "format_template": "https://www.awin1.com/cread.php?awinmid={advertiser_id}&awinaffid={affiliate_id}&ued={full_url}",
        "affiliate_tag": "awinaffid",
    },
    "admitad": {
        "pattern": r"(https?://(?:[\w\-]+\.)?wextap\.com/g" + PATTERN_URL_QUERY + ")",
        "format_template": "https://wextap.com/g/{advertiser_id}/?ulp={full_url}",
        "affiliate_tag": None,
    },
}