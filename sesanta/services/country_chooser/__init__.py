import base64
import functools
import hashlib
import itertools
import pathlib

import hjson

from sesanta.services.country_chooser.club_countries import COUNTRIES  # club countries
from sesanta.settings import settings

COUNTRIES = [country_pair[0] for country_pair in COUNTRIES]

with pathlib.Path(__file__).with_name("club_country_popularity.hjson").open("r") as file:
    MEMBERS_BY_COUNTRY: dict[str, int] = hjson.load(file)

GROUPS: dict[str, list[str]] = {}
GROUPS["Весь мир"] = COUNTRIES
with pathlib.Path(__file__).with_name("groups.hjson").open("r") as file:
    GROUPS.update(hjson.load(file))


def validate_groups(groups: dict[str, list[str]]) -> None:
    fast_lookup = set(COUNTRIES)
    failed: list[str] = []
    for country in itertools.chain.from_iterable(groups.values()):
        if country not in fast_lookup:
            failed.append(country)
    if failed:
        msg = f"unknown countries: {failed}"
        raise ValueError(msg)


validate_groups(GROUPS)


@functools.lru_cache(maxsize=len(COUNTRIES))
def hash_country(country: str) -> str:
    """Returns a short pseudo-unique code of a country."""
    hash_ = hashlib.sha512(country.encode()).digest()
    hash_ = base64.urlsafe_b64encode(hash_)
    return hash_.decode()[:16]


HASH_TO_COUNTRY = {hash_country(country): country for country in COUNTRIES}


class CountryChooser:
    @classmethod
    def is_allowed(cls, selected_countries: set[str]) -> bool:
        """Returns True if a total number of people in countries is high enough."""
        if any(country not in COUNTRIES for country in selected_countries):
            # all countries must be selected from a COUNTRIES list
            return False
        total_people = sum(
            MEMBERS_BY_COUNTRY.get(country, 0) for country in selected_countries
        )
        return total_people >= settings.selected_country_min_people
