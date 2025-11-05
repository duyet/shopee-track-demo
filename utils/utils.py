import os
import yaml
import glob
import shutil
import logging
import pandas as p
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')


def get_item_name(itemid: int) -> str:
    """
    Get item name from ../data/info/{itemid}.yaml
    """
    file = os.path.join(root_dir, f'data/info/{itemid}.yaml')

    with open(file, 'r') as f:
        info = yaml.safe_load(f)
        return info['name']


def read_config(config_file: str) -> Dict[str, Any]:
    """
    Read yaml config file from current directory
    """
    logger.info(f'Reading config file: {config_file}')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def is_same_row(dict1: Dict[str, Any], dict2: Dict[str, Any], ignores: List[str] = None) -> bool:
    """
    Compare two dict with ignores list
    """
    if ignores is None:
        ignores = []
    for key in dict1:
        if key in ignores:
            continue
        if not dict1.get(key) and not dict2.get(key):
            continue
        if str(dict1.get(key)) != str(dict2.get(key)):
            return False
    return True


def ensure_dir(name: str) -> None:
    """
    Create directory if not exist
    """
    if not os.path.exists(name):
        os.makedirs(name)
