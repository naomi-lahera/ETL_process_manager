import datetime as dt
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    named_entities: Mapped[list] = mapped_column(JSONB)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    source: Mapped["Source"] = relationship(back_populates="news")
    author: Mapped["Author"] = relationship(back_populates="news")
    sentiments: Mapped[list["EntitySentiment"]] = relationship(back_populates="news")

class EntitySentiment(Base):
    __tablename__ = "entity_sentiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    entity: Mapped[str] = mapped_column(String(255))
    sentiment: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str] = mapped_column(Text)
    news: Mapped["News"] = relationship(back_populates="sentiments")

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    news: Mapped[list["News"]] = relationship(back_populates="source")

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    news: Mapped[list["News"]] = relationship(back_populates="author")
