from typing import List

from dal.schemas import Source, SourceItem
from engine.interpreter import ArticleAnalysis, CounterAnalysis
from pydantic import BaseModel


class GetSourcesResponse(BaseModel):
    sources: List[Source]


class CreateSourceRequest(BaseModel):
    url: str


class CreateSourceResponse(BaseModel):
    source: Source


class PullSourcesResponse(BaseModel):
    new_items: List[SourceItem]


class GetSourceItemsResponse(BaseModel):
    items: List[SourceItem]


class GetSourceItemResponse(BaseModel):
    item: SourceItem


class GetSourceItemAnalysisResponse(BaseModel):
    analysis: ArticleAnalysis


class GetSourceItemCounterResponse(BaseModel):
    analysis: CounterAnalysis
