import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class AppMode(str, enum.Enum):  # noqa: WPS600

    API = "API"
    PRODUCT_CONSUMER = "PRODUCT_CONSUMER"
    DOCUMENT_CONSUMER = "DOCUMENT_CONSUMER"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    app_mode: AppMode = AppMode.API

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "msrdstocks"
    db_pass: str = "msrdstocks"
    db_base: str = "msrdstocks"
    db_echo: bool = False

    kafka_bootstrap_servers: list[str] = ["msrdstocks-kafka:9092"]
    kafka_consumer_group: str = "msrd.stocksconsumer"
    kafka_schemaregistry_client: str = "http://schemaregistry0:8085"

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "MSRDSTOCKS_"
        env_file_encoding = "utf-8"


settings = Settings()
