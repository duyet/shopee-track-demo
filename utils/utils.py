import os
import yaml
import glob
import shutil
import pandas as p

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')


def get_item_name(itemid):
    """
    Get item name from ../data/info/{itemid}.yaml
    """
    file = os.path.join(root_dir, f'data/info/{itemid}.yaml')

    with open(file, 'r') as f:
        info = yaml.load(f, Loader=yaml.FullLoader)
        return info['name']


def read_config(config_file):
    """
    Read yaml config file from current directory
    """
    print('Reading', config_file)
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def is_same_row(dict1, dict2, ignores=[]):
    """
    Compare two dict with ignores list
    """
    for key in dict1:
        if key in ignores:
            continue
        if not dict1.get(key) and not dict2.get(key):
            continue
        if str(dict1.get(key)) != str(dict2.get(key)):
            return False
    return True


def ensure_dir(name):
    """
    Create directory if not exist
    """
    if not os.path.exists(name):
        os.makedirs(name)
