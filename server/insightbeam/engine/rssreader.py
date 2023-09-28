from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Union

import feedparser
import newspaper

from insightbeam.dal.schemas.sql import Source as DbSource
from insightbeam.dal.schemas.sql import SourceItem as DbSourceItem

_logger = logging.getLogger(__name__)


class RSSReader:
    _newspaper_config: newspaper.Config

    def __init__(self):
        self._newspaper_config = newspaper.Config()
        self._newspaper_config.browser_user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0a"
        )

    def load_source_item(self, url: str) -> newspaper.Article:
        article = newspaper.Article(url=url, config=self._newspaper_config)
        article.download()
        article.parse()
        return article

    def load_source_items(
        self, source: DbSource, limit: Union[int, None] = None
    ) -> List[DbSourceItem]:
        source_items = list()
        feed: Dict = feedparser.parse(source.url)

        entries: List[Dict] = feed.get("entries", [])
        if limit is not None and isinstance(limit, int):
            entries = entries[:limit]

        with ThreadPoolExecutor(max_workers=len(entries)) as tpe:
            retrieve_article_tasks = {
                tpe.submit(self.load_source_item, entry.get("link")): entry.get("link")
                for entry in entries
            }

            for retrieve_article_task in as_completed(retrieve_article_tasks):
                url = retrieve_article_tasks[retrieve_article_task]
                try:
                    article = retrieve_article_task.result()
                    if article is not None:
                        source_item = DbSourceItem(
                            title=article.title,
                            url=article.url,
                            content=article.text,
                            source_uuid=source.uuid,
                        )
                        source_items.append(source_item)
                except Exception as e:
                    _logger.warn("Error retrieving article for: (url) (%s)", url, e)
                    pass
        return source_items
