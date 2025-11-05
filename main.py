import re
import os
import sys
import time
import yaml
import glob
import logging
import datetime
import requests
import pandas as pd
from typing import Dict, Any, Tuple

from utils import read_config, is_same_row, ensure_dir, parse_shopee_url, update_master_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def fetch_data(itemid: str, shopid: str, max_retries: int = 3, retry_delay: int = 2) -> Dict[str, Any]:
    """
    Fetch data from shopee.vn api and return json data
    API: https://shopee.vn/api/v4/item/get?itemid={itemid}&shopid={shopid}
    Implements retry logic with exponential backoff

    Args:
        itemid: Product item ID
        shopid: Shop ID
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 2)

    Returns:
        dict: Product data from API

    Raises:
        Exception: If all retry attempts fail or data validation fails
    """
    url = f'https://shopee.vn/api/v4/item/get?itemid={itemid}&shopid={shopid}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    last_exception = None
    for attempt in range(max_retries):
        try:
            # Add rate limiting delay between requests (not on first request)
            if attempt > 0:
                delay = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                logger.warning(f'Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})')
                time.sleep(delay)

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                raise Exception(f'HTTP {response.status_code}: Failed to fetch data from {url}')

            data = response.json().get('data')
            if not data:
                raise Exception(f'No data returned from {url}')

            required_fieds = [
                'itemid', 'shopid', 'name', 'description', 'price',
                'price_before_discount', 'stock', 'sold', 'item_status', 'image',
                'cmt_count', 'liked_count', 'shop_location'
            ]

            # validate data must have required fields
            for field in required_fieds:
                if field not in data:
                    raise Exception(f'Invalid data from {url}, missing {field}')

            return data

        except Exception as e:
            last_exception = e
            logger.error(f'Error fetching data (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt == max_retries - 1:
                raise last_exception

    raise last_exception


def update_db(data: Dict[str, Any]) -> None:
    """
    Store update data info to ./data/info/{itemid}.yaml file in yaml format
    And append history  data to ./data/history/{itemid}.csv file
    Only append new row if new data is not same as last row or if file not exist

    File format {itemid}.yaml:

    ```yaml
    itemid: 5873954476
    shopid: 88201679
    name: Apple MacBook Air (2020) M1 Chip 13.3 inch 8GB 256GB SSD
    image: http://...
    description: ...
    shop_location: Ho Chi Minh City
    updated_at: 2020-05-01T00:00:00+07:00
    ```

    File format {itemid}.csv:

    ```csv
    time,date,itemid,price,discount,price_before_discount,stock,sold,item_status,cmt_count,liked_count
    1610003537,20200101,5873954476,1000000,0,1000000,100,0,normal,100,100
    1638204525,20200102,1587395447,6000000,0,1000000,99,1,normal,100,100
    1638204553,20200102,1587395447,6000000,0,1000000,98,2,normal,100,100
    ````
    """
    current_time = int(time.time())
    current_date = time.strftime('%Y%m%d', time.localtime(current_time))
    itemid = data.get('itemid')
    shopid = data.get('shopid')
    data['date'] = current_date

    # create ./data/info and ./data/history directory if not exist
    ensure_dir('./data/info')
    ensure_dir('./data/history')

    # update history file or create new file if not exist
    history_file = f'./data/history/{itemid}.csv'
    if os.path.exists(history_file):
        df = pd.read_csv(history_file)
    else:
        df = pd.DataFrame(columns=[
            'time', 'date', 'itemid', 'price', 'discount',
            'price_before_discount', 'stock', 'sold', 'item_status',
            'cmt_count', 'liked_count'
        ])

    # get the last rows of history file and convert to dict
    last_row = df.iloc[-1].to_dict() if len(df) > 0 else None
    if last_row and is_same_row(last_row, data, ignores=['time', 'itemid']):
        logger.info(f'No update for {itemid}')
        return

    # append new row
    new_row = pd.DataFrame([{
        'time': current_time,
        'date': current_date,
        'itemid': itemid,
        'price': data.get('price'),
        'discount': data.get('discount'),
        'price_before_discount': data.get('price_before_discount'),
        'stock': data.get('stock'),
        'sold': data.get('sold'),
        'item_status': data.get('item_status'),
        'cmt_count': data.get('cmt_count'),
        'liked_count': data.get('liked_count')
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(history_file, index=False)
    logger.info(f'Updated {history_file}')

    info_data = {
        'itemid': itemid,
        'shopid': shopid,
        'name': data.get('name'),
        'image': data.get('image'),
        'shop_location': data.get('shop_location'),
        'updated_at': datetime.datetime.now().isoformat()
    }
    # create or update info file
    info_file = f'./data/info/{itemid}.yaml'
    with open(info_file, 'w') as f:
        yaml.dump(info_data, f)
        logger.info(f'Updated {info_file}')


def main() -> None:
    """
    Main function
    """
    # Reading configs
    config = read_config('config.yaml')
    urls = config.get('urls', [])
    logger.info(f'Got {len(urls)} URLs from config file')

    # Fetch data from shopee.vn api and update db
    for idx, url in enumerate(urls):
        try:
            logger.info(f'Processing ({idx + 1}/{len(urls)}): {url}')
            itemid, shopid = parse_shopee_url(url)
            data = fetch_data(itemid, shopid)
            update_db(data)

            # Add delay between requests to avoid rate limiting (except for last item)
            if idx < len(urls) - 1:
                time.sleep(1)  # 1 second delay between requests

        except Exception as e:
            logger.error(f'Failed to process {url}: {str(e)}')

    # This demontrate how to transform data and write to master file (output)
    update_master_file()


if __name__ == '__main__':
    main()
