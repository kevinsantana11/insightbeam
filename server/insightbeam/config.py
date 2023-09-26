import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel

_logger = logging.getLogger(__name__)


class Configuration(BaseModel):
    openai_api_key: str
    db_dir: str
    sengine_dir: str
    logs_dir: str
    log_level: str

    def __init__(self):
        load_dotenv()
        super().__init__(
            **{
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "db_dir": os.getenv("DB_DIR"),
                "sengine_dir": os.getenv("SENGINE_DIR"),
                "logs_dir": os.getenv("LOGS_DIR"),
                "log_level": os.getenv("LOG_LEVEL"),
            }
        )
        not os.path.exists(self.db_dir) and os.makedirs(self.db_dir)
        not os.path.exists(self.sengine_dir) and os.makedirs(self.sengine_dir)
        not os.path.exists(self.logs_dir) and os.makedirs(self.logs_dir)

        _logger.info("Configuration initialized!")
