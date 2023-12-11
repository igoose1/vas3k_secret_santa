import pydantic

from sesanta.db.schemas.users import DeliveryStatus


class User(pydantic.BaseModel):
    slug: str
    telegram_id: int
    address: str | None
    location: str | None
    selected: list[str]
    is_completed: bool
    santa: str | None
    grandchildren: list[str]
    delivery_status: DeliveryStatus
