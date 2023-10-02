from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from .api import app as _app
from .config import Configuration
from .dal import get_session_supplier, initialize_engine
from .dal.schemas import SourceItem as DbSourceItem
from .dependency_manager import manager
from .engine.interpreter import Interpreter
from .engine.rssreader import RSSReader
from .engine.search import Input, SearchEngine

_logger = logging.getLogger(__name__)


def prime_search_engine(sengine: SearchEngine, session: Session):
    results = session.execute(
        select(
            DbSourceItem.uuid,
            DbSourceItem.title,
            DbSourceItem.content,
            DbSourceItem.url,
        )
    )
    sengine.add_documents(
        [
            DbSourceItem(uuid=uuid, title=title, content=content, url=url)
            for (uuid, title, content, url) in results
        ],
        lambda item: Input(
            uuid=str(item.uuid), url=item.url, title=item.title, content=item.content
        ),
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
reader = RSSReader(cfg)

manager.register(reader)
manager.register(interpreter)
manager.register(sengine)
manager.register(Session, supplier=get_session_supplier(db_engine))

prime_search_engine(sengine, manager.inject(Session)())

app = _app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=cfg.host_name, port=cfg.port)
