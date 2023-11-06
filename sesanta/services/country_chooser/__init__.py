import hashlib
import pathlib

import hjson

from sesanta.services.country_chooser.club_countries import COUNTRIES  # club countries
from sesanta.settings import settings

COUNTRIES = [country_pair[0] for country_pair in COUNTRIES]

with pathlib.Path(__file__).with_name("club_country_popularity.hjson").open(
    "r",
) as file:
    MEMBERS_BY_COUNTRY: dict[str, int] = hjson.load(file)


def hash_country(country: str) -> str:
    """Returns a short pseudo-unique code of a country."""
    hex_ = hashlib.sha512(country.encode()).hexdigest()
    return hex_[:16]


HASH_TO_COUNTRY = {hash_country(country): country for country in COUNTRIES}


class CountryChooser:
    @classmethod
    def is_allowed(cls, selected_countries: list[str]) -> bool:
        """Returns True if a total number of people in countries is high enough."""
        if any(country not in COUNTRIES for country in selected_countries):
            # all countries must be selected from a COUNTRIES list
            return False
        total_people = sum(MEMBERS_BY_COUNTRY[country] for country in selected_countries)
        return total_people >= settings.selected_country_min_people
