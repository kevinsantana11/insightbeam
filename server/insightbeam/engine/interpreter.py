from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Union
from uuid import UUID

import bs4
from bs4 import ResultSet, Tag
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.messages import BaseMessageChunk
from pydantic import BaseModel

from insightbeam.config import Configuration
from insightbeam.dal.schemas import SourceItem
from insightbeam.engine.search import SearchResult

_logger = logging.getLogger(__name__)


class Interpreter:
    _chat_model: BaseChatModel
    _fail_token = "IGNORE"

    _gen_analysis_sys_msg = """You analyze articles and help the user determine the main subject matter the article
    is talking about along with the view points made and supporting arguments for that view point. The report you
    provide should be in the following format:

     <analysis>
        <subject>[subject goes here]</subject>
        <view-points>
            <view-point>
                <point>[The point being made]</point>
                <arguments>
                    <argument>[supporting argument that supports the point]</argument>
                </arguments>
            </view-point>
        </view-points>
     </analysis>

     The subject, points and arguments included in the report should be easily searchable in the original article.
     """

    _gen_analysis_template = """
    Article: {article}

    Report:
    """

    _gen_counter_sys_msg = """Given a subject, points made about the subject and related articles, identify
    which, if any that provide countering/opposite points. Your response should be in the following format:
    <analysis>
        <counters>
            <counter>
                <original>[One of the original view points being apposed/countered]</original>
                <counter>[The opposing/counter view point being presented]</counter>
                <article-id>[article_id for counter-view-point goes here]</article-id>
            </counter>
        </counters>
    </analysis>

    If any of the rules below fail, simply respond with only: `{fail_token}`.
    Rules:
    * Subject should be a non empty string.
    * Under the `Points` section, there should be one to many points each starting with `*` and separated by newlines.
    * There will be a section called `Related` under which each related article will be provided sepearated by two
    newlines.
    * Each article provided will have an `article_id` property whose value should be a non null and non empty string.
    * Each article provided will have an content` property which value should be a non null and non empty string.

    Only include counter/opposing views in the analysis any that aren't can be ignored.
    """.format(
        fail_token=_fail_token
    )

    _gen_counter_template = """
    Subject:
    {subject}

    Points:
    {points}

    Related:
    {related}
    """

    _point_template = "* {point}"
    _related_article_template = "article_id: {article_id}\ncontent: {content}"

    def __init__(self, cfg: Configuration):
        self._chat_model = ChatOpenAI(
            temperature=0.2,
            openai_api_key=cfg.openai_api_key,
            model="gpt-3.5-turbo-16k",
        )

    def _sub_analysis(self, item: SourceItem) -> BaseMessageChunk:
        _logger.info("Generating analysis for (title) (%s)", item.title)
        return self._chat_model.invoke(
            [
                SystemMessage(content=self._gen_analysis_sys_msg),
                HumanMessage(
                    content=self._gen_analysis_template.format(article=item.content)
                ),
            ]
        )

    def counter_analysis(
        self,
        article_analysis: ArticleAnalysis,
        relevant: List[SearchResult],
        contents: Dict[str, str],
    ) -> CounterAnalysis:
        points = "\n".join(
            [
                self._point_template.format(point=vp.point)
                for vp in article_analysis.analysis.view_points
            ]
        )
        related = "\n\n".join(
            [
                self._related_article_template.format(
                    article_id=rel.article_uuid, content=contents.get(rel.article_uuid)
                )
                for rel in relevant
            ]
        )
        msg = self._gen_counter_template.format(
            subject=article_analysis.analysis.subject, points=points, related=related
        )
        opposing_view = self._chat_model.invoke(
            [
                SystemMessage(content=self._gen_counter_sys_msg),
                HumanMessage(content=msg),
            ]
        )

        if opposing_view != self._fail_token:
            return CounterAnalysis.parse_xml(opposing_view.content)
        return CounterAnalysis(counters=list())

    def analyze(self, items: List[SourceItem]) -> List[ArticleAnalysis]:
        feed_item_analysis: Dict[UUID, str] = dict()
        with ThreadPoolExecutor(max_workers=len(items)) as tpe:
            analysis_tasks = {
                tpe.submit(self._sub_analysis, item): item.uuid for item in items
            }

            for analysis_task in as_completed(analysis_tasks):
                uuid = analysis_tasks[analysis_task]
                response: BaseMessageChunk = analysis_task.result()
                feed_item_analysis[uuid] = response.content

            uuids_and_reports = [
                (uuid, Analysis.parse_xml(analysis))
                for (uuid, analysis) in feed_item_analysis.items()
            ]

            return [
                ArticleAnalysis(article_uuid=uuid.hex, analysis=analysis)
                for (uuid, analysis) in uuids_and_reports
                if analysis is not None
            ]


class ViewPoint(BaseModel):
    point: str
    arguments: List[str]

    @classmethod
    def parse_xml(cls, content: Tag) -> ViewPoint:
        point = content.find("point").get_text()
        arguments_soup: ResultSet[Tag] = content.find("arguments").find_all("argument")
        arguments = [arg.get_text() for arg in arguments_soup]
        return cls(point=point, arguments=arguments)


class Analysis(BaseModel):
    subject: str
    view_points: List[ViewPoint]

    @classmethod
    def parse_xml(cls, content: str) -> Union[Analysis, None]:
        try:
            content_soup = bs4.BeautifulSoup(content, features="lxml")
            analysis_report = content_soup.find("analysis")
            subject = analysis_report.find("subject").get_text()
            view_points = cls._parse_xml_viewpoints(
                analysis_report.find("view-points").find_all("view-point")
            )
            return cls(subject=subject, view_points=view_points)
        except Exception as e:
            _logger.error("Error parsing xml: %s", e)
            return None

    @classmethod
    def _parse_xml_viewpoints(cls, view_points: ResultSet[Any]) -> List[ViewPoint]:
        return [ViewPoint.parse_xml(view_point) for view_point in view_points]


class ArticleAnalysis(BaseModel):
    article_uuid: str
    analysis: Analysis


class Counter(BaseModel):
    article_uuid: str
    original_view_point: str
    counter_view_point: str

    @classmethod
    def parse_xml(cls, content: Tag) -> Counter:
        article_id = content.find("article-id").get_text()
        original = content.find("original").get_text()
        counter = content.find("counter").get_text()
        return cls(
            article_uuid=article_id,
            original_view_point=original,
            counter_view_point=counter,
        )


class CounterAnalysis(BaseModel):
    counters: List[Counter]

    @classmethod
    def parse_xml(cls, content: str) -> CounterAnalysis:
        content_soup = bs4.BeautifulSoup(content, features="lxml")
        counters_soup = (
            content_soup.find("analysis").find("counters").find_all("counter")
        )
        counters = cls._parse_xml_counters(counters_soup)
        return cls(counters=counters)

    @classmethod
    def _parse_xml_counters(cls, counters: ResultSet[Any]) -> List[Counter]:
        return [Counter.parse_xml(counter) for counter in counters]
