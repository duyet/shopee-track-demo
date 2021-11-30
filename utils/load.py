import os
import yaml
import glob
import pandas as pd

from .transformation import transform_price
from .utils import get_item_name

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')


def update_master_file(src='./data/history/*.csv', target='./data/master.csv'):
    """
    Concat all history file to master file
    Add the item name by lookup into ./data/info/{itemid}.yaml
    """
    print('Updating master file')

    src_files = glob.glob(os.path.join(root_dir, src))

    # check src files
    if not src_files:
        print('No history file found')
        return

    df = pd.DataFrame()
    for file in src_files:
        df = df.append(pd.read_csv(file))

    # add item_name column
    df['item_name'] = df['itemid'].apply(get_item_name)

    # format price, price_before_discount
    df['price'] = df['price'].apply(transform_price)
    df['price_before_discount'] = df['price_before_discount'].apply(
        transform_price)

    # sort by itemid, overwrite the master file
    df.sort_values(by=['itemid', 'time'], inplace=True)
    df.to_csv(target, index=False)

    # Get file size of master file in KB
    size = os.path.getsize(target) / 1024

    print(f'Master file updated, size: {size:.2f} KB')
