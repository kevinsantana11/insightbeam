from typing import Union
from uuid import UUID, uuid4

from pydantic import UUID4, BaseModel, Field


class JsonTable(BaseModel):
    uuid: UUID4 = Field(default_factory=lambda: uuid4())

    def __init__(self, uuid: Union[str, None] = None, **kwargs):
        if uuid is not None and isinstance(uuid, str):
            super().__init__(uuid=UUID(hex=uuid), **kwargs)
        else:
            super().__init__(**kwargs)

    @classmethod
    def table_name(cls):
        return cls.__name__


class Source(JsonTable):
    url: str


class SourceItem(JsonTable):
    title: str
    content: str
    url: str
    source_uuid: UUID4


class SourceItemAnalysis(JsonTable):
    source_item_uuid: UUID4
    analysis: str


class SourceItemCounterAnalysis(JsonTable):
    source_item_uuid: UUID4
    analysis: str
