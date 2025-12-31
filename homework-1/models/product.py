class Product:
    def __init__(self, name: str, category: str, price: float):
        self.name: str = name
        self.category: str = category
        self.price: float = price
        self.sale: int = 0

    def edit_category(self, new_category: str) -> None:
        self.category = new_category

    def edit_price(self, new_price: float) -> None:
        self.price = new_price

    def set_sale(self, sale: int) -> None:
        self.sale = sale

    def cancel_sale(self) -> None:
        self.sale = 0

    def get_price(self) -> float:
        if self.sale == 0:
            return self.price
        return self.price * (1 - self.sale / 100)

    def __repr__(self) -> str:
        return (
            f"Product(name={self.name!r}, "
            f"category={self.category!r}, "
            f"price={self.price}, "
            f"sale={self.sale}%)"
        )
