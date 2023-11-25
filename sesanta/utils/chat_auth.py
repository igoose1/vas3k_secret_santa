import base64
import datetime
import pathlib
import random
from typing import Self

import pydantic
import zstandard
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
    def __init__(self, secret: str, dictionary: pathlib.Path):
        key = blake2b(f"auth-{secret}".encode(), digest_size=16)
        self.__box = SecretBox(key)
        padgen = random.Random(blake2b(f"padding-{secret}".encode()))
        self.__padding_length = padgen.randrange(8)

        with dictionary.open("rb") as file:
            dict_data = zstandard.ZstdCompressionDict(file.read())
        self.cctx = zstandard.ZstdCompressor(dict_data=dict_data)
        self.dctx = zstandard.ZstdDecompressor(dict_data=dict_data)

    def __call__(self, data: str) -> ChatInfo:
        """Decrypt `data` to `ChatInfo`.

        Raises ExpiredError when data was expired."""
        try:
            decoded = base64.urlsafe_b64decode(data)
            decrypted = self.__box.decrypt(decoded)
            decompressed = self.dctx.decompress(decrypted)
            chat_info = ChatInfo.model_validate_json(decompressed)
        except Exception:
            msg = "can't decode"
            raise ValueError(msg)
        if chat_info.exp < datetime.datetime.now(datetime.UTC):
            msg = "chat info was expired"
            raise ExpiredError(msg)
        return chat_info

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
        compressed = self.cctx.compress(chat_info.model_dump_json().encode())
        encrypted = self.__box.encrypt(compressed)
        encoded = base64.urlsafe_b64encode(encrypted)
        return encoded.decode()
