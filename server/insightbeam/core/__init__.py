import json
import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import insightbeam.dal as dal
from insightbeam.common import Article
from insightbeam.engine.interpreter import (
    Analysis,
    ArticleAnalysis,
    CounterAnalysis,
    Interpreter,
)
from insightbeam.engine.rssreader import RSSReader
from insightbeam.engine.search import SearchEngine

_logger = logging.getLogger(__name__)


def get_sources(session: Session):
    return dal.get_all_sources(session)


def add_source(session: Session, **kwargs):
    return dal.add_source(session, **kwargs)


def pull_from_sources(source_id: int, reader: RSSReader, session: Session):
    """
    :raise NoResultFound: When source could not be found
    """
    source = dal.get_source(session, source_id)

    current_items = dal.get_source_items(session, source.uuid)
    (retrieved_items, failed) = reader.load_source_items(source.url)

    new_item_titles = set([itm.title for itm in retrieved_items]) - set(
        [itm.title for itm in current_items]
    )
    new_items = [itm for itm in retrieved_items if itm.title in new_item_titles]

    _logger.info(f"pulled {len(new_items)} new documents!")
    return (dal.add_source_items(session, source, new_items), failed)


def get_source_items(source_id: int, session: Session):
    """
    :raise NoResultFound: When source could not be found
    """
    dal.get_source(session, source_id)
    return dal.get_source_items(session, source_id)


def get_source_item(item_id: int, session: Session):
    """
    :raise NoResultFound: When source item could not be found
    """
    return dal.get_source_item(session, item_id)


def get_source_item_analysis(item_id: int, session: Session, interpreter: Interpreter):
    """
    :raise NoResultFound: When source item could not be found
    :raise RuntimeError: When there is an error generating the article analysis
    """
    analysis_str = dal.get_source_item_analysis(session, item_id)

    if analysis_str is None:
        source_item = dal.get_source_item(session, item_id)

        item = Article(
            url=source_item.url, title=source_item.title, content=source_item.content
        )
        analysis = interpreter.analyze([item])[0]

        if analysis.error is not None or not isinstance(analysis.analysis, Analysis):
            error = analysis.error or "analysis is not of expected type [Analysis]"
            raise RuntimeError("Error generating analysis {error}".format(error=error))

        dal.add_source_item_analysis(session, item_id, analysis)
    else:
        analysis = ArticleAnalysis(**json.loads(analysis_str))
    return analysis


def get_source_item_counters(
    item_id: int, session: Session, interpreter: Interpreter, sengine: SearchEngine
):
    """
    :raise NoResultFound: When base article analysis could not be found or associated articles cannot be found in the db
    :raise RuntimeError: When article analysis can be found but the analysis itself is missing or there was an error
    generating the counter analysis.
    """
    counter_analysis_str = dal.get_source_item_counter_analysis(session, item_id)

    if counter_analysis_str is None:
        analysis_str = dal.get_source_item_analysis(session, item_id)

        if analysis_str is None:
            raise NoResultFound("Associated analysis not found for {}".format(item_id))

        article_analysis = ArticleAnalysis(**json.loads(analysis_str))

        if article_analysis.analysis is None:
            raise RuntimeError("Article analysis was found but the analysis was empty")

        similar_documents = sengine.search(article_analysis.analysis.subject)
        articles = list()

        for doc in similar_documents:
            source_item = dal.get_source_item(session, item_id)
            articles.append(
                Article(
                    title=doc.article_title,
                    content=source_item.content,
                    url=source_item.url,
                )
            )

        counter_analysis = interpreter.counter_analysis(
            article_analysis.article_url, article_analysis.analysis, articles
        )

        if counter_analysis.error is not None or not isinstance(
            counter_analysis.counter, CounterAnalysis
        ):
            error = (
                counter_analysis.error
                or "analysis is not of expected type [CounterAnalysis]"
            )
            raise RuntimeError("Error generating analysis {error}".format(error=error))

        dal.add_source_item_counter_analysis(session, item_id, counter_analysis)
    else:
        counter_analysis = ArticleAnalysis(**json.loads(counter_analysis_str))
    return counter_analysis
