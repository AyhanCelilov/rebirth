import sqlalchemy.orm as so

from extensions import db

class SearchLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    url: so.Mapped[str] = so.mapped_column(index=True)
    date: so.Mapped[str] = so.mapped_column(index=True)

    def __repr__(self):
        return f'<SearchLog {self.id}, {self.url}, {self.date}>'