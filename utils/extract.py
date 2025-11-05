import re
import sys
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_shopee_url(url: str) -> Tuple[str, str]:
    """
    Parse shopee.vn url to get itemid and shopid

    for example:
    url = https://shopee.vn/Apple-MacBook-Air-(2020)-M1-Chip-13.3-inch-8GB-256GB-SSD-i.88201679.5873954476
    itemid = 5873954476
    shopid = 88201679
    """
    # is valid url?
    if not re.match(r'^https://shopee.vn/.*[0-9]+\.[0-9]+$', url):
        logger.error(f'Invalid URL format: {url}')
        sys.exit(1)

    url_split = url.split('.')
    itemid = url_split[-1]
    shopid = url_split[-2]

    return itemid, shopid
