import json
import logging

from fastapi import Body, Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from insightbeam.api import schemas as sch
from insightbeam.api.schemas import Source, SourceItem
from insightbeam.dal.schemas.sql import Source as DbSource
from insightbeam.dal.schemas.sql import SourceItem as DbSourceItem
from insightbeam.dal.schemas.sql import SourceItemAnalysis as DbSourceItemAnalysis
from insightbeam.dal.schemas.sql import (
    SourceItemCounterAnalysis as DbSourceItemCounterAnalysis,
)
from insightbeam.dependency_manager import manager as m
from insightbeam.engine.interpreter import ArticleAnalysis, CounterAnalysis, Interpreter
from insightbeam.engine.rssreader import RSSReader
from insightbeam.engine.search import SearchEngine

app = FastAPI()
_logger = logging.getLogger(__name__)


@app.get("/sources", response_model=sch.GetSourcesResponse)
def get_sources(session: Session = Depends(m.inject(Session))):
    results = session.execute(select(DbSource.uuid, DbSource.url)).all()
    return sch.GetSourcesResponse(
        sources=[Source(uuid=str(uuid), url=url) for (uuid, url) in results]
    )


@app.post("/sources", response_model=sch.CreateSourceResponse)
def add_source(
    request: sch.CreateSourceRequest = Body(...),
    session: Session = Depends(m.inject(Session)),
):
    source = DbSource(**request.model_dump())
    session.add(source)
    session.commit()
    return sch.CreateSourceResponse(
        source=Source(uuid=str(source.uuid), url=source.url)
    )


@app.get("/sources/{source_id}/pull", response_model=sch.PullSourcesResponse)
def pull_from_sources(
    source_id: int,
    reader: RSSReader = Depends(m.inject(RSSReader)),
    session: Session = Depends(m.inject(Session)),
):
    (source_uuid, url) = session.execute(
        select(DbSource.uuid, DbSource.url).where(DbSource.uuid == source_id)
    ).one()
    current_items = session.execute(
        select(DbSourceItem.uuid, DbSourceItem.title).where(
            DbSourceItem.source_uuid == source_uuid
        )
    )
    retrieved_items = reader.load_source_items(DbSource(uuid=source_uuid, url=url))

    new_item_titles = set([itm.title for itm in retrieved_items]) - set(
        [title for (_, title) in current_items]
    )
    new_items = [itm for itm in retrieved_items if itm.title in new_item_titles]

    session.add_all(new_items)
    session.commit()

    _logger.info(f"pulled {len(new_items)} new documents!")
    return sch.PullSourcesResponse(
        new_items=[
            SourceItem(
                uuid=str(itm.uuid),
                title=itm.title,
                content=itm.content,
                url=itm.url,
                source_uuid=str(itm.source_uuid),
            )
            for itm in new_items
        ]
    )


@app.get("/sources/{source_id}/items", response_model=sch.GetSourceItemsResponse)
def get_source_items(source_id: int, session: Session = Depends(m.inject(Session))):
    results = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        ).where(DbSourceItem.source_uuid == int(source_id))
    )
    return sch.GetSourceItemsResponse(
        items=[
            SourceItem(
                uuid=str(uuid),
                title=title,
                content=content,
                url=url,
                source_uuid=str(source_uuid),
            )
            for (uuid, title, content, url, source_uuid) in results
        ]
    )


@app.get("/items/{item_id}", response_model=sch.GetSourceItemResponse)
def get_source_item(item_id: str, session: Session = Depends(m.inject(Session))):
    (uuid, title, content, url, source_uuid) = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        ).where(DbSourceItem.uuid == item_id)
    ).one()

    return sch.GetSourceItemResponse(
        item=SourceItem(
            uuid=str(uuid),
            title=title,
            content=content,
            url=url,
            source_uuid=str(source_uuid),
        )
    )


@app.get("/items/{item_id}/analyze", response_model=sch.GetSourceItemAnalysisResponse)
def get_source_item_analysis(
    item_id: str,
    session: Session = Depends(m.inject(Session)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
):
    analysis = _get_analysis(item_id, session, interpreter)
    return sch.GetSourceItemAnalysisResponse(analysis=analysis)


@app.get("/items/{item_id}/counters", response_model=sch.GetSourceItemCounterResponse)
def get_source_item_counters(
    item_id: str,
    session: Session = Depends(m.inject(Session)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
    sengine: SearchEngine = Depends(m.inject(SearchEngine)),
):
    counter_analysis = _get_counter_analysis(item_id, session, interpreter, sengine)
    return sch.GetSourceItemCounterResponse(analysis=counter_analysis)


def _get_analysis(item_id: int, session: Session, interpreter: Interpreter):
    row = session.execute(
        select(DbSourceItemAnalysis.analysis).where(
            DbSourceItemAnalysis.source_item_uuid == item_id
        )
    ).one_or_none()

    if row is None:
        (title, content, url, source_uuid) = session.execute(
            select(
                DbSourceItem.title,
                DbSourceItem.content,
                DbSourceItem.url,
                DbSourceItem.source_uuid,
            ).where(DbSourceItem.uuid == item_id)
        ).one()

        item = DbSourceItem(
            uuid=item_id, title=title, content=content, url=url, source_uuid=source_uuid
        )
        analysis = interpreter.analyze([item])[0]
        analysis_item = DbSourceItemAnalysis(
            analysis=analysis.model_dump_json(), source_item_uuid=item_id
        )

        session.add(analysis_item)
        session.commit()
    else:
        (analysis_str,) = row
        analysis = ArticleAnalysis(**json.loads(analysis_str))
    return analysis


def _get_counter_analysis(
    item_id: str, session: Session, interpreter: Interpreter, sengine: SearchEngine
):
    row = session.execute(
        select(DbSourceItemCounterAnalysis.analysis).where(
            DbSourceItemCounterAnalysis.source_item_uuid == item_id
        )
    ).one_or_none()

    if row is None:
        analysis = _get_analysis(item_id, session, interpreter)
        similar_documents = sengine.search(analysis.analysis.subject)

        contents = dict()
        for doc in similar_documents:
            (content,) = session.execute(
                select(DbSourceItem.content).where(
                    DbSourceItem.uuid == int(doc.article_uuid)
                )
            ).one()
            contents[doc.article_uuid] = content
        analysis = interpreter.counter_analysis(analysis, similar_documents, contents)
        analysis_item = DbSourceItemCounterAnalysis(
            analysis=analysis.model_dump_json(), source_item_uuid=item_id
        )

        session.add(analysis_item)
        session.commit()
    else:
        (analysis_str,) = row
        analysis = CounterAnalysis(**json.loads(analysis_str))
    return analysis
