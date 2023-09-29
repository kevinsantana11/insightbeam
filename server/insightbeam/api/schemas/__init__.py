from typing import List

from pydantic import BaseModel

from insightbeam.engine.interpreter import ArticleAnalysis


class Source(BaseModel):
    uuid: str
    url: str


class SourceItem(BaseModel):
    uuid: str
    title: str
    content: str
    url: str
    source_uuid: str


class GetSourcesResponse(BaseModel):
    sources: List[Source]


class CreateSourceRequest(BaseModel):
    url: str


class CreateSourceResponse(BaseModel):
    source: Source


class PullSourcesResponse(BaseModel):
    new_items: List[SourceItem]
    failed: List[str]


class GetSourceItemsResponse(BaseModel):
    items: List[SourceItem]


class GetSourceItemResponse(BaseModel):
    item: SourceItem


class GetSourceItemAnalysisResponse(BaseModel):
    analysis: ArticleAnalysis
