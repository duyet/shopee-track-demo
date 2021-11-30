import os
import yaml
import shutil


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
