from typing import List

def select_top_users_by_rate(users: List, top_size: int) -> List:
    ordered_users = sorted(users, key=lambda user: user.rate, reverse=True)
    return ordered_users[:top_size]
