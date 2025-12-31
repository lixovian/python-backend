from typing import List

def get_ordered_products_by_price(products: List) -> List:
    return sorted(products, key=lambda product: product.get_price(), reverse=True)
