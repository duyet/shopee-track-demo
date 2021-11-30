import os
import yaml
import glob
import shutil
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')


def read_config(config_file):
    """
    Read yaml config file from current directory
    """
    print('Reading', config_file)
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def compare_row(dict1, dict2, ignores=[]):
    """
    Compare two dict with ignores list
    """
    for key in dict1:
        if key in ignores:
            continue
        if dict1.get(key) != dict2.get(key):
            return False
    return True


def ensure_dir(name):
    """
    Create directory if not exist
    """
    if not os.path.exists(name):
        os.makedirs(name)


def get_item_name(itemid):
    """
    Get item name from ../data/info/{itemid}.yaml
    """
    file = os.path.join(root_dir, f'data/info/{itemid}.yaml')

    with open(file, 'r') as f:
        info = yaml.load(f, Loader=yaml.FullLoader)
        return info['name']


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

    # sort by itemid, overwrite the master file
    df.sort_values(by=['itemid', 'time'], inplace=True)
    df.to_csv(target, index=False)

    # Get file size of master file in KB
    size = os.path.getsize(target) / 1024

    print(f'Master file updated, size: {size:.2f} KB')
