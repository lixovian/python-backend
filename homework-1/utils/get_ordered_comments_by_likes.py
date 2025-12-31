from typing import List

def get_ordered_comments_by_likes(comments: List) -> List:
    return sorted(comments, key=lambda comment: comment.like_count, reverse=True)
