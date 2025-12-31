from typing import List

def extract_prices(products: List) -> List[float]:
    return [product.get_price() for product in products]
