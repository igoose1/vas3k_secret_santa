Secret Santa registration for [vas3k.club](https://vas3k.club).

It's built with aiogram, motor (python driver for mongodb) and pydantic.

## Run

```sh
docker compose up
```

## Run locally

Launch MongoDB server and fill .env file. If this step is skipped, bot will raise with
describing which environmental variables are missing.

```sh
python -m pip install poetry
poetry install
poetry run python -m sesanta.bot
```

Example of .env:

```
SESANTA_BOT_TOKEN="telegram_bot_token"
SESANTA_MONGO_URI="mongodb://localhost:27017"
SESANTA_CLUB_POST_LINK="https://vas3k.club/post/21649/"
SESANTA_CLUB_BY_TELEGRAM_ID_ENDPOINT="https://vas3k.club/user/by_telegram_id"
SESANTA_CLUB_TOKEN="clubtoken"
SESANTA_CRITERIA_MIN_UPVOTES=100
SESANTA_CRITERIA_MAX_CREATED_AT=2023-05-01
SESANTA_CRITERIA_MIN_MEMBERSHIP_EXPIRES_AT=2024-02-01
SESANTA_SELECTED_COUNTRY_MIN_PEOPLE=20
```

## Contribute

Feel free to create PRs. Be sure you installed pre-commit hooks before pushing:
`pre-commit install`.

Code is licensed by 3-Clause BSD License.
