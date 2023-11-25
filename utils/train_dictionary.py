import datetime
import random
import string
import sys

import click
import zstandard

from sesanta.utils.chat_auth import ChatInfo


def random_slug(generator: random.Random) -> str:
    length = generator.randrange(5, 10)
    raw = (generator.choice(string.ascii_letters + string.digits) for _ in range(length))
    return "".join(raw)


@click.command()
@click.argument("seed", default=69)
@click.argument("sample_number", default=2**16)
@click.argument("dict_size", default=256)
def main(seed: int, sample_number, dict_size) -> None:
    """Generate random ChatInfo instances and train zstandard dictionary on them."""
    generator = random.Random(seed)
    now = datetime.datetime.now(datetime.UTC)
    samples: list[bytes] = []
    for index in range(sample_number):
        sender, receiver = random_slug(generator), random_slug(generator)
        chat_info = ChatInfo(
            sender=sender,
            receiver=receiver,
            santa=generator.choice([sender, receiver]),
            exp=now + datetime.timedelta(seconds=generator.randrange(0, 3600 * 8)),
            padding="0" * generator.randrange(8),
        )
        samples.append(chat_info.model_dump_json().encode())

    trained = zstandard.train_dictionary(
        dict_size,
        samples,
        threads=-1,
        level=19,
    )
    sys.stdout.buffer.write(trained.as_bytes())


if __name__ == "__main__":
    main()
