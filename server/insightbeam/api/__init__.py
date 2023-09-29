import json
import logging

from fastapi import Body, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from insightbeam.api import schemas as sch
from insightbeam.api.schemas import Source, SourceItem
from insightbeam.common import Article
from insightbeam.dal.schemas.sql import Source as DbSource
from insightbeam.dal.schemas.sql import SourceItem as DbSourceItem
from insightbeam.dal.schemas.sql import SourceItemAnalysis as DbSourceItemAnalysis
from insightbeam.dal.schemas.sql import (
    SourceItemCounterAnalysis as DbSourceItemCounterAnalysis,
)
from insightbeam.dependency_manager import manager as m
from insightbeam.engine.interpreter import (
    Analysis,
    ArticleAnalysis,
    CounterAnalysis,
    Interpreter,
)
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
    try:
        (source_uuid, url) = session.execute(
            select(DbSource.uuid, DbSource.url).where(DbSource.uuid == source_id)
        ).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Source[id:{source_id}] not found")

    current_items = session.execute(
        select(DbSourceItem.uuid, DbSourceItem.title).where(
            DbSourceItem.source_uuid == source_uuid
        )
    )
    (retrieved_items, failed) = reader.load_source_items(url)

    new_item_titles = set([itm.title for itm in retrieved_items]) - set(
        [title for (_, title) in current_items]
    )
    new_items = [itm for itm in retrieved_items if itm.title in new_item_titles]

    db_items = [
        DbSourceItem(
            title=itm.title, content=itm.content, url=itm.url, source_uuid=source_id
        )
        for itm in new_items
    ]

    session.add_all(db_items)
    session.commit()

    _logger.info(f"pulled {len(new_items)} new documents!")
    return sch.PullSourcesResponse(
        new_items=[
            SourceItem(
                uuid=str(itm.uuid),
                title=itm.title,
                content=itm.content,
                url=itm.url,
                source_uuid=str(source_id),
            )
            for itm in db_items
        ],
        failed=failed,
    )


@app.get("/sources/{source_id}/items", response_model=sch.GetSourceItemsResponse)
def get_source_items(source_id: int, session: Session = Depends(m.inject(Session))):
    try:
        session.execute(select(DbSource.uuid).where(DbSource.uuid == source_id)).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Source[id:{source_id}] not found")

    results = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        ).where(DbSourceItem.source_uuid == int(source_id))
    ).all()

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
    try:
        (uuid, title, content, url, source_uuid) = session.execute(
            select(
                DbSourceItem.uuid,
                DbSourceItem.title,
                DbSourceItem.content,
                DbSourceItem.url,
                DbSourceItem.source_uuid,
            ).where(DbSourceItem.uuid == item_id)
        ).one()
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"item[id:{str(item_id)}] not found"
        )

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


@app.get("/items/{item_id}/counters", response_model=sch.GetSourceItemAnalysisResponse)
def get_source_item_counters(
    item_id: str,
    session: Session = Depends(m.inject(Session)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
    sengine: SearchEngine = Depends(m.inject(SearchEngine)),
):
    counter_analysis = _get_counter_analysis(item_id, session, interpreter, sengine)
    return sch.GetSourceItemAnalysisResponse(analysis=counter_analysis)


def _get_analysis(item_id: int, session: Session, interpreter: Interpreter):
    row = session.execute(
        select(DbSourceItemAnalysis.analysis).where(
            DbSourceItemAnalysis.source_item_uuid == item_id
        )
    ).one_or_none()

    if row is None:
        try:
            (title, content, url) = session.execute(
                select(
                    DbSourceItem.title,
                    DbSourceItem.content,
                    DbSourceItem.url,
                ).where(DbSourceItem.uuid == item_id)
            ).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"item[id:{item_id}] not found")

        item = Article(url=url, title=title, content=content)
        analysis = interpreter.analyze([item])[0]

        if analysis.error is not None or not isinstance(analysis.analysis, Analysis):
            raise HTTPException(status_code=503, detail=analysis.model_dump())

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
        article_analysis = _get_analysis(item_id, session, interpreter)
        similar_documents = sengine.search(article_analysis.analysis.subject)
        articles = list()

        for doc in similar_documents:
            try:
                (content, url) = session.execute(
                    select(DbSourceItem.content, DbSourceItem.url).where(
                        DbSourceItem.uuid == int(doc.article_uuid)
                    )
                ).one()
            except NoResultFound:
                raise HTTPException(
                    status_code=404, detail=f"item[id:{item_id}] not found"
                )

            articles.append(Article(title=doc.article_title, content=content, url=url))
        analysis = interpreter.counter_analysis(article_analysis, articles)
        analysis_item = DbSourceItemCounterAnalysis(
            analysis=analysis.model_dump_json(), source_item_uuid=item_id
        )

        if analysis.error is not None or not isinstance(
            analysis.analysis, CounterAnalysis
        ):
            raise HTTPException(status_code=503, detail=analysis.model_dump())

        session.add(analysis_item)
        session.commit()
    else:
        (analysis_str,) = row
        analysis = ArticleAnalysis(**json.loads(analysis_str))
    return analysis
