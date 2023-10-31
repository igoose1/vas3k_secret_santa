import datetime
import string

import aiohttp
import aiolimiter
import pydantic
from typing_extensions import TypedDict


class ClubMember(pydantic.BaseModel):
    slug: str
    full_name: str
    upvotes: int
    created_at: datetime.datetime
    membership_expires_at: datetime.datetime
    country: str


class ClubMemberBody(TypedDict):
    user: ClubMember


class ClubMemberNotFoundError(Exception):
    """Raised when there's no member with specified `telegram_id`"""


class ClubMemberLoader:
    def __init__(
        self,
        endpoint: str,
        token: str,
        max_rate_per_minute: float,
    ):
        self.session = aiohttp.ClientSession()
        self.session.cookie_jar.update_cookies({"token": token})
        endpoint = endpoint.rstrip("/")
        self.url_template = string.Template(f"{endpoint}/$id.json")
        self.limiter = aiolimiter.AsyncLimiter(
            max_rate=max_rate_per_minute,
            time_period=60,
        )

    async def __call__(self, telegram_id: int) -> ClubMember:
        url = self.url_template.safe_substitute({"id": telegram_id})
        adapter = pydantic.TypeAdapter(ClubMemberBody)
        async with self.limiter, self.session.get(url) as response:
            text = await response.text()
            if not response.ok:
                msg = f'Club returned {response.status} status, text: "{text}"'
                raise ClubMemberNotFoundError(msg)
        validated = adapter.validate_json(text)
        return validated["user"]
