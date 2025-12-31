from datetime import datetime, timedelta


class Comment:
    def __init__(self, author_id, text):
        self.author_id = author_id
        self.text = text
        self.create_data = datetime.now()
        self.update_data = self.create_data
        self.like_count = 0

    def edit_comment(self, new_text):
        self.text = new_text
        self.update_data = self.update_data + timedelta(microseconds=1)

    def like(self):
        self.like_count += 1

    def dislike(self):
        self.like_count -= 1

    def __repr__(self):
        return (
            f"Comment(author_id={self.author_id}, "
            f"text={self.text!r}, "
            f"likes={self.like_count})"
        )
