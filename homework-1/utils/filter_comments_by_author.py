from typing import List

def filter_comments_by_author(comments: List, author) -> List:
    return [comment for comment in comments if comment.author_id == author.id]
