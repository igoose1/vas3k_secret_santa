import base64
import datetime
import random
from typing import Self

import pydantic
from nacl.hash import blake2b
from nacl.secret import SecretBox


class ChatInfo(pydantic.BaseModel):
    sender: str
    receiver: str
    santa: str
    exp: datetime.datetime

    # random number of zeroes so length of original data can't be easily extracted.
    padding: str

    @property
    def me(self) -> str:
        return self.sender

    @property
    def they(self) -> str:
        return self.receiver

    @property
    def grandchild(self) -> str:
        return self.sender if self.santa != self.sender else self.receiver

    @pydantic.model_validator(mode="after")
    def check_santa(self) -> Self:
        if self.santa not in [self.sender, self.receiver]:
            msg = "santa must be one of chat participant"
            raise ValueError(msg)
        return self


class ExpiredError(ValueError):
    """Raised when data was expired."""


class ChatAuthenticator:
    def __init__(self, secret: str):
        key = blake2b(f"auth-{secret}".encode(), digest_size=16)
        self.__box = SecretBox(key)
        padgen = random.Random(blake2b(f"padding-{secret}".encode()))
        self.__padding_length = padgen.randrange(8)

    def __call__(self, data: str) -> ChatInfo:
        """Decrypt `data` to `ChatInfo`.

        Raises ExpiredError when data was expired."""
        try:
            decoded = base64.urlsafe_b64decode(data)
            decrypted = self.__box.decrypt(decoded)
        except Exception:
            msg = "can't decode"
            raise ValueError(msg)
        exp_chat_info = ChatInfo.model_validate_json(decrypted)
        if exp_chat_info.exp < datetime.datetime.now(datetime.UTC):
            msg = "chat info was expired"
            raise ExpiredError(msg)
        return ChatInfo.model_validate(exp_chat_info, strict=True)

    def generate(
        self,
        sender: str,
        receiver: str,
        santa: str,
        expire_in: datetime.timedelta,
    ) -> str:
        """Return encrypted `ChatInfo` encoded in url-safe base64."""
        chat_info = ChatInfo(
            sender=sender,
            receiver=receiver,
            santa=santa,
            exp=datetime.datetime.now(datetime.UTC) + expire_in,
            padding="0" * self.__padding_length,
        )
        encrypted = self.__box.encrypt(chat_info.model_dump_json().encode())
        encoded = base64.urlsafe_b64encode(encrypted)
        return encoded.decode()
