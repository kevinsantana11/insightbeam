from __future__ import annotations

import os
from logging import Logger
from typing import List

from pydantic import BaseModel
from whoosh.fields import ID, TEXT, Schema
from whoosh.index import Index, create_in, exists_in, open_dir
from whoosh.qparser import OrGroup, QueryParser
from whoosh.writing import IndexWriter
from insightbeam.common import Article

from insightbeam.config import Configuration

_logger = Logger(__name__)


class SearchEngine:
    _schema = Schema(
        content=TEXT,
        title=TEXT(stored=True),
        uuid=ID(stored=True, analyzer=None),
        url=TEXT(stored=True, analyzer=None)
    )
    _ix: Index
    _parser: QueryParser

    def __init__(self, cfg: Configuration, clean=True):
        path = cfg.sengine_dir
        if not os.path.exists(path):
            os.mkdir(path)

        if clean or not exists_in(path):
            self._ix = create_in(path, self._schema)
        elif exists_in(path) and not clean:
            self._ix = open_dir(path)

        self._parser = QueryParser("content", self._schema, group=OrGroup.factory(0.8))

    def _add_document(self, writer: IndexWriter, item: Article):
        writer.add_document(
            content=item.content, title=item.title, url=item.url, uuid=str(item.article_id)
        )

    def add_documents(self, items: List[Article]):
        try:
            writer: IndexWriter = self._ix.writer()
            [self._add_document(writer, item) for item in items]
            writer.commit()
        except Exception as e:
            _logger.error("Exception raised adding documents to the index %s", e)
            writer.cancel()

    def search(self, query_expr: str) -> List[SearchResult]:
        with self._ix.searcher() as s:
            query = self._parser.parse(query_expr)
            results = s.search(query, terms=True)
            return [
                SearchResult(
                    article_uuid=hit["uuid"],
                    article_title=hit["title"],
                    matched_terms=[t for (_, t) in hit.matched_terms()],
                )
                for hit in results
            ]


class SearchResult(BaseModel):
    article_uuid: str
    article_title: str
    matched_terms: List[str]
