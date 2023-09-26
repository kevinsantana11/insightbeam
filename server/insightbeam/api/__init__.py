import json
import logging
from typing import List
from uuid import UUID

from dal import JsonFileDatabase
from dal.schemas import (
    Source,
    SourceItem,
    SourceItemAnalysis,
    SourceItemCounterAnalysis,
)
from dependency_manager import manager as m
from engine.interpreter import ArticleAnalysis, CounterAnalysis, Interpreter
from engine.rssreader import RSSReader
from engine.search import SearchEngine
from fastapi import Body, Depends, FastAPI

from . import schemas as sch

app = FastAPI()
_logger = logging.getLogger(__name__)


@app.get("/sources", response_model=sch.GetSourcesResponse)
def get_sources(db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase))):
    return sch.GetSourcesResponse(sources=db.get_all(Source))


@app.post("/sources", response_model=sch.CreateSourceResponse)
def add_source(
    request: sch.CreateSourceRequest = Body(...),
    db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase)),
):
    source = Source(**request.model_dump())
    db.save(source)
    db.store_all()
    return sch.CreateSourceResponse(source=source)


@app.get("/sources/{source_id}/pull", response_model=sch.PullSourcesResponse)
def pull_from_sources(
    source_id: str,
    reader: RSSReader = Depends(m.inject(RSSReader)),
    db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase)),
):
    source: Source = db.get(Source, source_id)
    source_items = reader.load_source_items(source)
    current_items: List[SourceItem] = db.get_all(
        SourceItem, lambda x: x.get("source_uuid") == source.uuid
    )

    new_item_titles = set([itm.title for itm in source_items]) - set(
        [itm.title for itm in current_items]
    )
    new_items = [itm for itm in source_items if itm.title in new_item_titles]
    db.save_all(new_items)
    db.store_all()
    _logger.info(f"pulled {len(new_items)} new documents!")
    return sch.PullSourcesResponse(new_items=new_items)


@app.get("/sources/{source_id}/items", response_model=sch.GetSourceItemsResponse)
def get_source_items(
    source_id: str, db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase))
):
    return sch.GetSourceItemsResponse(
        items=db.get_all(SourceItem, lambda x: x.get("source_uuid") == source_id)
    )


@app.get("/items/{item_id}", response_model=sch.GetSourceItemResponse)
def get_source_item(
    item_id: str, db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase))
):
    return sch.GetSourceItemResponse(item=db.get(SourceItem, item_id))


@app.get("/items/{item_id}/analyze", response_model=sch.GetSourceItemAnalysisResponse)
def get_source_item_analysis(
    item_id: str,
    db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
    sengine: SearchEngine = Depends(m.inject(SearchEngine)),
):
    analysis = _get_analysis(item_id, db, interpreter)
    return sch.GetSourceItemAnalysisResponse(analysis=analysis)


@app.get("/items/{item_id}/counters", response_model=sch.GetSourceItemCounterResponse)
def get_source_item_counters(
    item_id: str,
    db: JsonFileDatabase = Depends(m.inject(JsonFileDatabase)),
    interpreter: Interpreter = Depends(m.inject(Interpreter)),
    sengine: SearchEngine = Depends(m.inject(SearchEngine)),
):
    counter_analysis = _get_counter_analysis(item_id, db, interpreter, sengine)
    return sch.GetSourceItemCounterResponse(analysis=counter_analysis)


def _get_analysis(item_id: str, db: JsonFileDatabase, interpreter: Interpreter):
    analysis_records: List[SourceItemAnalysis] = db.get_all(
        SourceItemAnalysis, lambda x: x.get("source_item_uuid") == item_id
    )
    if analysis_records is None or len(analysis_records) == 0:
        item = db.get(SourceItem, item_id)
        analysis = interpreter.analyze([item])[0]
        db.save_all(
            [
                SourceItemAnalysis(
                    source_item_uuid=UUID(hex=item_id),
                    analysis=analysis.model_dump_json(),
                )
            ]
        )
        db.store_all()
    else:
        analysis_str = analysis_records[0].analysis
        analysis = ArticleAnalysis(**json.loads(analysis_str))
    return analysis


def _get_counter_analysis(
    item_id: str, db: JsonFileDatabase, interpreter: Interpreter, sengine: SearchEngine
):
    analysis_records: List[SourceItemCounterAnalysis] = db.get_all(
        SourceItemCounterAnalysis, lambda x: x.get("source_item_uuid") == item_id
    )
    if analysis_records is None or len(analysis_records) == 0:
        analysis = _get_analysis(item_id, db, interpreter)
        similar_documents = sengine.search(analysis.analysis.subject)

        contents = dict()
        for doc in similar_documents:
            source_item: SourceItem = db.get(SourceItem, doc.article_uuid)
            contents[source_item.uuid.__str__()] = source_item.content
        analysis = interpreter.counter_analysis(analysis, similar_documents, contents)

        db.save_all(
            [
                SourceItemCounterAnalysis(
                    source_item_uuid=UUID(hex=item_id),
                    analysis=analysis.model_dump_json(),
                )
            ]
        )
        db.store_all()
    else:
        analysis_str = analysis_records[0].analysis
        analysis = CounterAnalysis(**json.loads(analysis_str))
    return analysis
