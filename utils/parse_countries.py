import json
import re
import sys

import click
from bs4 import BeautifulSoup

number_regex = re.compile(r"\((?P<number>\d+)\)")


@click.command()
def main() -> None:
    """Parses people-search-country div block from https://vas3k.club/people/

    Returns countries with a number of people from it."""
    result: dict[str, int] = {}
    soup = BeautifulSoup(sys.stdin.read(), features="html.parser")
    select = soup.find("select", attrs={"name": "country"})
    for option in select.find_all("option"):  # type: ignore
        matched = number_regex.search(str(option))
        if matched is None:
            if option.text != "Весь мир":
                msg = f'Can\'t find a number in line "{option}"'
                raise ValueError(msg)
            continue
        country, number = option.attrs["value"], int(matched.group("number"))
        result[country] = number
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
