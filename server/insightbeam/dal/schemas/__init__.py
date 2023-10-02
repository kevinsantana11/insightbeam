from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    ...


class Source(Base):
    __tablename__ = "source"

    uuid: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]

    source_items: Mapped[SourceItem] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class SourceItem(Base):
    __tablename__ = "source_item"

    uuid: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    url: Mapped[str]
    source_uuid: Mapped[int] = mapped_column(ForeignKey("source.uuid"))

    source: Mapped[Source] = relationship(back_populates="source_items")
    analysis: Mapped[SourceItemAnalysis] = relationship(back_populates="source_item")
    counter_analysis: Mapped[SourceItemCounterAnalysis] = relationship(
        back_populates="source_item"
    )


class SourceItemAnalysis(Base):
    __tablename__ = "source_item_analysis"

    uuid: Mapped[int] = mapped_column(primary_key=True)
    analysis: Mapped[str]
    source_item_uuid: Mapped[int] = mapped_column(ForeignKey("source_item.uuid"))

    source_item: Mapped[SourceItem] = relationship(back_populates="analysis")


class SourceItemCounterAnalysis(Base):
    __tablename__ = "source_item_counter_analysis"

    uuid: Mapped[int] = mapped_column(primary_key=True)
    analysis: Mapped[str]
    source_item_uuid: Mapped[int] = mapped_column(ForeignKey("source_item.uuid"))

    source_item: Mapped[SourceItem] = relationship(back_populates="counter_analysis")
