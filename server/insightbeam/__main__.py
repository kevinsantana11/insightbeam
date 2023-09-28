from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from insightbeam.api import app as _app
from insightbeam.config import Configuration
from insightbeam.dal.schemas.sql import SourceItem as DbSourceItem
from insightbeam.dal.schemas.sql import get_session_supplier, initialize_engine
from insightbeam.dependency_manager import manager
from insightbeam.engine.interpreter import Interpreter
from insightbeam.engine.rssreader import RSSReader
from insightbeam.engine.search import SearchEngine

_logger = logging.getLogger(__name__)


def prime_search_engine(sengine: SearchEngine, session: Session):
    results = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
            DbSourceItem.source_uuid,
        )
    )
    sengine.add_documents(
        [
            DbSourceItem(
                uuid=uuid,
                title=title,
                content=content,
                url=url,
                source_uuid=source_uuid,
            )
            for (uuid, title, content, url, source_uuid) in results
        ]
    )
    _logger.info("Primed search engine!")


def setup_logging(cfg: Configuration):
    logging.basicConfig(
        format="[%(levelname)s][%(asctime)s][%(name)s] - %(message)s",
        filename=f"{cfg.logs_dir}/application.log",
        encoding="utf-8",
        level=cfg.log_level,
    )


cfg = Configuration()
setup_logging(cfg)
db_engine = initialize_engine(cfg)
interpreter = Interpreter(cfg)
sengine = SearchEngine(cfg)
reader = RSSReader()

manager.register(reader)
manager.register(interpreter)
manager.register(sengine)
manager.register(Session, supplier=get_session_supplier(db_engine))

prime_search_engine(sengine, manager.inject(Session)())

app = _app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
