import datetime
import pathlib

import pytest
import time_machine

from sesanta.utils.chat_auth import ChatAuthenticator, ExpiredError


@pytest.fixture
def auth() -> ChatAuthenticator:
    return ChatAuthenticator("fake secret", pathlib.Path("zstddict"))


def test_forth_and_back(auth) -> None:
    string = auth.generate("bob", "alice", "bob", datetime.timedelta(hours=1))
    assert auth(string).sender == "bob"
    assert auth(string).receiver == "alice"
    assert auth(string).santa == "bob"


def test_wrong_santa(auth) -> None:
    with pytest.raises(ValueError):
        _ = auth.generate("bob", "alice", "eva", datetime.timedelta(hours=1))


def test_on_random_data(auth) -> None:
    with pytest.raises(ValueError):
        # not base64
        auth("Hello world!")
    with pytest.raises(ValueError):
        # wrong key
        auth(
            "CybQUlRWh1oPmVQU0nlki7qmymxf8k5DDhltUethpZxATDfA9R"
            "mjkRsHFvCoVed90WJO9dkEBo8zJbNmKFXP1BFrUb_jByVEh0v7"
            "PsNz3sOo0E26mA6dcCvlqNneifdzCR3HQNL5CG0HJUcQTFRI",
        )


def test_expired(auth) -> None:
    with time_machine.travel(0, tick=False) as traveller:
        string = auth.generate("bob", "alice", "bob", datetime.timedelta(hours=1))
        auth(string)  # shouldn't fail
        traveller.move_to(datetime.timedelta(hours=1, seconds=1))
        with pytest.raises(ExpiredError):
            auth(string)  # should fail
