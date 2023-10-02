from pydantic import BaseModel


class Article(BaseModel):
    title: str
    content: str
    url: str


class Source(BaseModel):
    uuid: int
    url: str


class SourceItem(BaseModel):
    uuid: int
    title: str
    content: str
    url: str
    source_uuid: int
