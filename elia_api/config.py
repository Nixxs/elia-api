from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_FORCE_ROLL_BACK: bool = False

    FRONTEND_URL: str
    JWT_SECRET: str

    GOOGLE_API_KEY: str
    BIGQUERY_JSON_KEY_B64: str
    SERVICE_ACCOUNT_WRITE_PATH: str = "/tmp/service-account.json"
    CHAT_HISTORY_LIMIT: int
    GOOGLE_LLM_MODEL: str

    GEOFLIP_API_KEY: str
    GEOFLIP_API_URL: str


    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_prefix="")

    def __init__(self, **values):
        super().__init__(**values)
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DevConfig(GlobalConfig):
    DB_FORCE_ROLL_BACK: bool = False
    SERVICE_ACCOUNT_WRITE_PATH: str = "./elia_api/keys/service-account.json"


class TestConfig(GlobalConfig):
    TEST_DB_NAME: str = "test-db"
    DB_FORCE_ROLL_BACK: bool = True
    SERVICE_ACCOUNT_WRITE_PATH: str = "./elia_api/keys/service-account.json"

    def __init__(self, **values):
        super().__init__(**values)
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"


@lru_cache()
def get_config(env_state: str):
    match env_state:
        case "test":
            return TestConfig()
        case "dev":
            return DevConfig()
        case _:
            return GlobalConfig()


config = get_config(BaseConfig().ENV_STATE)
