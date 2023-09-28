from __future__ import annotations

import logging

from sqlalchemy import Engine, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from insightbeam.config import Configuration

_logger = logging.getLogger(__name__)


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


def initialize_engine(cfg: Configuration):
    engine = create_engine(cfg.db_url, echo=True)
    table_names = [
        Source.__tablename__,
        SourceItem.__tablename__,
        SourceItemAnalysis.__tablename__,
        SourceItemCounterAnalysis.__tablename__,
    ]

    with engine.connect() as conn:
        any_created = any(
            [engine.dialect.has_table(conn, table_name) for table_name in table_names]
        )

        if not any_created:
            _logger.info("Creating database tables: [%s]", ",".join(table_names))
            Base.metadata.create_all(engine)
            conn.commit()
        else:
            _logger.info("Some tables already created!")
    return engine


def get_session_supplier(engine: Engine):
    def session_supplier(engine: Engine):
        try:
            session = Session(engine)
            yield session
        finally:
            session.rollback()
            session.close()

    return lambda: session_supplier(engine)
