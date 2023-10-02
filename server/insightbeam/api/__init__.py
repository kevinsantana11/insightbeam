import logging

from fastapi import Body, Depends, FastAPI, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import insightbeam.core as core
from insightbeam.api import schemas as sch
from insightbeam.dependency_manager import manager as m
from insightbeam.engine.interpreter import Interpreter
from insightbeam.engine.rssreader import RSSReader
from insightbeam.engine.search import SearchEngine

app = FastAPI()
_logger = logging.getLogger(__name__)


@app.get("/sources", response_model=sch.GetSourcesResponse)
def get_sources(session: Session = Depends(m.inject(Session))):
    return sch.GetSourcesResponse(sources=core.get_sources(session))


@app.post("/sources", response_model=sch.CreateSourceResponse)
def add_source(
    request: sch.CreateSourceRequest = Body(...),
    session: Session = Depends(m.inject(Session)),
):
    return sch.CreateSourceResponse(
        source=core.add_source(session, **request.model_dump())
    )


@app.get("/sources/{source_id}/pull", response_model=sch.PullSourcesResponse)
def pull_from_sources(
    source_id: int,
    reader: RSSReader = Depends(m.inject(RSSReader)),
    session: Session = Depends(m.inject(Session)),
):
    try:
        (new_items, failed) = core.pull_from_sources(source_id, reader, session)
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Source[id:{source_id}] not found")

    return sch.PullSourcesResponse(
        new_items=new_items,
        failed=failed,
    )


@app.get("/sources/{source_id}/items", response_model=sch.GetSourceItemsResponse)
def get_source_items(source_id: int, session: Session = Depends(m.inject(Session))):
    try:
        return sch.GetSourceItemsResponse(
            items=core.get_source_items(source_id, session)
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Source[id:{source_id}] not found")


@app.get("/items/{item_id}", response_model=sch.GetSourceItemResponse)
def get_source_item(item_id: int, session: Session = Depends(m.inject(Session))):
    try:
        return sch.GetSourceItemResponse(item=core.get_source_item(item_id, session))
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"item[id:{str(item_id)}] not found"
        )


@app.get("/items/{item_id}/analyze", response_model=sch.GetSourceItemAnalysisResponse)
def get_source_item_analysis(
    item_id: int,
    session: Session = Depends(m.inject(Session)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
):
    try:
        return sch.GetSourceItemAnalysisResponse(
            analysis=core.get_source_item_analysis(item_id, session, interpreter)
        )
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"item[id:{str(item_id)}] not found"
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/items/{item_id}/counters", response_model=sch.GetSourceItemAnalysisResponse)
def get_source_item_counters(
    item_id: int,
    session: Session = Depends(m.inject(Session)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
    sengine: SearchEngine = Depends(m.inject(SearchEngine)),
):
    try:
        return sch.GetSourceItemAnalysisResponse(
            analysis=core.get_source_item_counters(
                item_id, session, interpreter, sengine
            )
        )
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"item[id:{str(item_id)}] not found"
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
