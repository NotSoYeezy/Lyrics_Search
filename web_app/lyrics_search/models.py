from sqlalchemy.orm import Mapped, mapped_column
from web_app.lyrics_search.extensions import db


class Song(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(255), nullable=True)
    author: Mapped[str] = mapped_column(db.String(120), nullable=False)
    lyrics: Mapped[str] = mapped_column(db.Text, nullable=False)
    index: Mapped[int] = mapped_column(db.Integer, nullable=False)
    removed: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Song {self.title}, author: {self.author}>"
