import pydantic


class User(pydantic.BaseModel):
    slug: str
    telegram_id: int
    location: str | None
    selected: list[str]
    is_completed: bool
