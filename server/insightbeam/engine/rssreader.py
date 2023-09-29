from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Union

import feedparser
import newspaper

from insightbeam.common import Article
from insightbeam.config import Configuration

_logger = logging.getLogger(__name__)


class RSSReader:
    _newspaper_config: newspaper.Config

    def __init__(self, cfg: Configuration):
        self._newspaper_config = newspaper.Config()
        self._newspaper_config.request_timeout = cfg.dep_call_timeout
        self._newspaper_config.browser_user_agent = cfg.browser_agent

    def load_source_item(self, url: str) -> newspaper.Article:
        article = newspaper.Article(url=url, config=self._newspaper_config)
        article.download()
        article.parse()
        return article

    def load_source_items(
        self, url: str, limit: Union[int, None] = None
    ) -> Tuple[List[Article], List[str]]:
        items = list()
        failed = list()
        feed: Dict = feedparser.parse(url)

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
                        item = Article(
                            content=article.text, title=article.title, url=article.url
                        )
                        items.append(item)
                except Exception as e:
                    _logger.warn("Error retrieving article for: (url) (%s)", url, e)
                    failed.append(url)

        return (items, failed)
