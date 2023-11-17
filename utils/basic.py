import pydantic


class User(pydantic.BaseModel):
    slug: str
    location: str | None
    selected: list[str]
    is_completed: bool
