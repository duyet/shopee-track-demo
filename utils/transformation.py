from typing import Union


def transform_price(price: Union[int, str]) -> int:
    """
    Transform price from 28_990_000_00000 to 28_990_000
    """
    if isinstance(price, str):
        price = int(price)

    return price // 100000
