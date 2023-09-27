from __future__ import annotations

import logging

from insightbeam.api import app as _app
from insightbeam.config import Configuration
from insightbeam.dal import JsonFileDatabase
from insightbeam.dal.schemas import (
    Source,
    SourceItem,
    SourceItemAnalysis,
    SourceItemCounterAnalysis,
)
from insightbeam.dependency_manager import manager
from insightbeam.engine.interpreter import Interpreter
from insightbeam.engine.rssreader import RSSReader
from insightbeam.engine.search import SearchEngine

_logger = logging.getLogger(__name__)


def init_db(cfg: Configuration) -> JsonFileDatabase:
    json_db = JsonFileDatabase(cfg)
    json_db.load(Source)
    json_db.load(SourceItem)
    json_db.load(SourceItemAnalysis)
    json_db.load(SourceItemCounterAnalysis)
    _logger.info("Initialized Database!")
    return json_db


def prime_search_engine(sengine: SearchEngine, db: JsonFileDatabase):
    source_items = db.get_all(SourceItem)
    sengine.add_documents(source_items)
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
interpreter = Interpreter(cfg)
sengine = SearchEngine(cfg)
db = init_db(cfg)
reader = RSSReader()

manager.register(db)
manager.register(reader)
manager.register(interpreter)
manager.register(sengine)

prime_search_engine(sengine, db)
app = _app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(_app)
