from typing import List

def select_products_by_category(products: List, category: str) -> List:
    return [product for product in products if product.category == category]
