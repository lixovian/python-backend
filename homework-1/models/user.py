import uuid


class User:
    def __init__(self, name: str):
        self.id: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.comments_count: int = 0
        self.rate: int = 0
        self.is_banned: bool = False

    def edit_name(self, new_name: str) -> None:
        self.name = new_name

    def increment_rate(self) -> None:
        self.rate += 1

    def ban_user(self) -> None:
        self.is_banned = True

    def unban_user(self) -> None:
        self.is_banned = False

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, "
            f"name={self.name!r}, "
            f"rate={self.rate}, "
            f"is_banned={self.is_banned})"
        )
