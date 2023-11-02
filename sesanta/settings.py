from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    mongo_uri: MongoDsn
    mongo_db: str = "sesanta"

    club_by_telegram_id_endpoint: str
    club_token: str
    club_max_rate_per_minute: int = 60

    model_config = SettingsConfigDict(env_prefix="sesanta_", env_file=".env")


settings = Settings()  # type: ignore
