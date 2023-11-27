import datetime

from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from sesanta.serving_status import ServingStatus


class Settings(BaseSettings):
    serving_status: ServingStatus

    secret: str

    chats_host: str
    chats_port: int
    chats_workers: int = 4
    chats_expire_in: datetime.timedelta = datetime.timedelta(hours=12)

    bot_token: str

    mongo_uri: MongoDsn
    mongo_db: str = "sesanta"

    club_post_link: str
    club_by_telegram_id_endpoint: str
    club_token: str
    club_max_rate_per_minute: int = 60

    criteria_min_upvotes: int
    criteria_max_created_at: datetime.date
    criteria_min_membership_expires_at: datetime.date

    selected_country_min_people: int

    model_config = SettingsConfigDict(env_prefix="sesanta_", env_file=".env")


settings = Settings()  # type: ignore
