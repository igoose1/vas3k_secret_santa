import base64
import datetime

import pydantic
from nacl.hash import blake2b
from nacl.secret import SecretBox


class ChatInfo(pydantic.BaseModel):
    sender: str
    receiver: str
    exp: datetime.datetime


class ExpiredError(ValueError):
    """Raised when data was expired."""


class ChatAuthenticator:
    def __init__(self, secret: str):
        key = blake2b(secret.encode(), digest_size=16)
        self.__box = SecretBox(key)

    def authenticate(self, data: str) -> ChatInfo:
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

    def generate(self, sender: str, receiver: str, expire_in: datetime.timedelta) -> str:
        """Return encrypted `ChatInfo` encoded in url-safe base64."""
        exp_chat_info = ChatInfo(
            sender=sender,
            receiver=receiver,
            exp=datetime.datetime.now(datetime.UTC) + expire_in,
        )
        encrypted = self.__box.encrypt(exp_chat_info.model_dump_json().encode())
        encoded = base64.urlsafe_b64encode(encrypted)
        return encoded.decode()
