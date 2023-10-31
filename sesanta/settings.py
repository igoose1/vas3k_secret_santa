from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    mongodb_uri: MongoDsn

    model_config = SettingsConfigDict(env_prefix="sesanta")


settings = Settings()  # type: ignore
