import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel

_logger = logging.getLogger(__name__)


class Configuration(BaseModel):
    openai_api_key: str
    db_url: str
    sengine_dir: str
    logs_dir: str
    log_level: str
    dep_call_timeout: int
    dep_call_retry: int
    browser_agent: str
    host_name: str
    port: int

    def __init__(self):
        load_dotenv()
        super().__init__(
            **{
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "db_url": os.getenv("DB_URL"),
                "sengine_dir": os.getenv("SENGINE_DIR"),
                "logs_dir": os.getenv("LOGS_DIR"),
                "log_level": os.getenv("LOG_LEVEL"),
                "dep_call_timeout": os.getenv("DEP_CALL_TIMEOUT", 10),
                "dep_call_retry": os.getenv("DEP_CALL_RETRY", 10),
                "host_name": os.getenv("HOST_NAME", "127.0.0.1"),
                "port": os.getenv("PORT", 8000),
                "browser_agent": os.getenv(
                    "BROWSER_AGENT",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0a",
                ),
            }
        )
        not os.path.exists(self.sengine_dir) and os.makedirs(self.sengine_dir)
        not os.path.exists(self.logs_dir) and os.makedirs(self.logs_dir)

        print("Configuration initialized!")
