import logging
from typing import Any, List, Union

from sqlalchemy import Engine, Select, create_engine, select
from sqlalchemy.orm import Session

from insightbeam.common import Article, Source, SourceItem
from insightbeam.config import Configuration
from insightbeam.dal.schemas import Base
from insightbeam.dal.schemas import Source as DbSource
from insightbeam.dal.schemas import SourceItem as DbSourceItem
from insightbeam.dal.schemas import SourceItemAnalysis as DbSourceItemAnalysis
from insightbeam.dal.schemas import (
    SourceItemCounterAnalysis as DbSourceItemCounterAnalysis,
)
from insightbeam.engine.interpreter import ArticleAnalysis

_logger = logging.getLogger(__name__)


def get_all_sources(session: Session) -> List[Source]:
    results = session.execute(select(DbSource.uuid, DbSource.url)).all()
    return [Source(uuid=uuid, url=url) for (uuid, url) in results]


def add_source(session: Session, **kwargs) -> Source:
    source = DbSource(**kwargs)
    session.add(source)
    session.commit()
    return Source(uuid=source.uuid, url=source.url)


def get_source(session: Session, source_id: int) -> Source:
    """
    raise: NoResultFound: When a Source cannot be found for the given source_id
    """
    (source_uuid, url) = session.execute(
        select(DbSource.uuid, DbSource.url).where(DbSource.uuid == source_id)
    ).one()
    return Source(uuid=source_uuid, url=url)


def get_source_items(
    session: Session, source_id: Union[int, None] = None
) -> List[SourceItem]:
    if source_id is not None:
        stmt: Select[Any] = select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        ).where(DbSourceItem.source_uuid == source_id)
    else:
        stmt = select(DbSourceItem.uuid, DbSourceItem.title)

    results = session.execute(stmt)
    return [
        SourceItem(
            uuid=uuid, title=title, content=content, url=url, source_uuid=source_uuid
        )
        for (uuid, title, content, url, source_uuid) in results
    ]


def add_source_items(
    session: Session, source: Source, articles: List[Article]
) -> List[SourceItem]:
    db_items = [
        DbSourceItem(
            title=a.title, content=a.content, url=a.url, source_uuid=source.uuid
        )
        for a in articles
    ]

    session.add_all(db_items)
    session.commit()

    return [
        SourceItem(
            uuid=itm.uuid,
            title=itm.title,
            content=itm.content,
            url=itm.url,
            source_uuid=source.uuid,
        )
        for itm in db_items
    ]


def get_source_item(session: Session, source_item_id: int) -> SourceItem:
    """
    raise: NoResultFound: When a SourceItem cannot be found for the given source_item_id
    """
    (uuid, title, content, url, source_uuid) = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        ).where(DbSourceItem.uuid == source_item_id)
    ).one()

    return SourceItem(
        uuid=uuid,
        title=title,
        content=content,
        url=url,
        source_uuid=source_uuid,
    )


def get_source_item_analysis(session: Session, source_item_id: int) -> Union[str, None]:
    row = session.execute(
        select(DbSourceItemAnalysis.analysis).where(
            DbSourceItemAnalysis.source_item_uuid == source_item_id
        )
    ).one_or_none()

    if row is not None:
        (analysis_str,) = row
        return analysis_str
    return None


def add_source_item_analysis(
    session: Session, source_item_id: int, analysis: ArticleAnalysis
) -> None:
    analysis_item = DbSourceItemAnalysis(
        analysis=analysis.model_dump_json(), source_item_uuid=source_item_id
    )

    session.add(analysis_item)
    session.commit()


def get_source_item_counter_analysis(
    session: Session, source_item_id: int
) -> Union[str, None]:
    row = session.execute(
        select(DbSourceItemCounterAnalysis.analysis).where(
            DbSourceItemCounterAnalysis.source_item_uuid == source_item_id
        )
    ).one_or_none()

    if row is not None:
        (anaysis_str,) = row
        return anaysis_str
    else:
        return None


def add_source_item_counter_analysis(
    session: Session, source_item_id: int, analysis: ArticleAnalysis
) -> None:
    analysis_item = DbSourceItemCounterAnalysis(
        analysis=analysis.model_dump_json(), source_item_uuid=source_item_id
    )

    session.add(analysis_item)
    session.commit()


def initialize_engine(cfg: Configuration):
    engine = create_engine(cfg.db_url, echo=True)
    table_names = [
        DbSource.__tablename__,
        DbSourceItem.__tablename__,
        DbSourceItemAnalysis.__tablename__,
        DbSourceItemCounterAnalysis.__tablename__,
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
