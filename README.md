Secret Santa is no longer updated as the FOSS project. You can download, edit and do what
you want according to the license with this version of code.

---

Secret Santa registration for [vas3k.club](https://vas3k.club).

With this project you can:

- Start registration for a new "Secret Santa",
- Match participants according to shipping preferences,
- Organize anonymous web-chats so every Santa can ask for shipping details without
  revealing their names,
- Monitor "Bad Santa" names.

The project is built around vas3k.club but can be adjusted to any other community.

Technologies used: aiogram, motor (python driver for mongodb) and fastapi.

## Simple run

```sh
docker compose up
```

## Run locally

Launch MongoDB server and fill .env file. If this step is skipped, bot will raise with
describing which environmental variables are missing.

Install requirements:

```sh
python -m pip install poetry
poetry install
```

Run bot:

```sh
poetry run python -m sesanta.bot
```

Run web-chats with gunicorn:

```sh
gunicorn -c sesanta/chats/gunicorn.py sesanta.chats.web:app
```

Example of .env:

```
SESANTA_SERVING_STATUS=sending
SESANTA_CHATS_PORT=3423
SESANTA_SECRET=changeme
SESANTA_BOT_TOKEN="123456:abcdef"
SESANTA_MONGO_URI="mongodb://localhost:27017"
SESANTA_CLUB_POST_LINK="https://vas3k.club/post/21649/"
SESANTA_CLUB_BY_TELEGRAM_ID_ENDPOINT="https://vas3k.club/user/by_telegram_id"
SESANTA_CLUB_TOKEN="abcdef123456"
SESANTA_CRITERIA_MIN_UPVOTES=100
SESANTA_CRITERIA_MAX_CREATED_AT=2023-05-01
SESANTA_CRITERIA_MIN_MEMBERSHIP_EXPIRES_AT=2024-02-01
SESANTA_SELECTED_COUNTRY_MIN_PEOPLE=20
```

`SESANTA_SERVING_STATUS` describes current mode of the bot:

- bot accepts new participants with `collecting`,
- bot stops accepting new forms with `drawing`,
- bot doesn't accept new forms but shares links to web-chats with `sending`.

It's expected that at the beginning bot is launched with `collecting`. Then the variable
is set to `drawing` meaning it's in a process of people matching. When a cycle of
participants was imported (see "Scripts" in this README) the bot is expected to be under
`sending` mode.

## Scripts

It's recommended to have `jq` installed. All scripts output in hjson but it can be
converted to json with built-in hjson-json converter.

### Export users

Exports users to stdout.

```sh
python -m utils.export_users
```

### Find a cycle

Finds a cycle from exported users. Accepts `utils.export_users` input in stdin.

```sh
python -m utils.find_cycle
```

Example:

```sh
python -m utils.export_users | python -m utils.find_cycle
```

### Import a cycle

Imports a cycle from `utils.find_cycle`. Accepts a list of slugs joined by comma.

```sh
python -m utils.import_cycle
```

Example:

```sh
python -m utils.export_users > exported.hjson

python -m utils.find_cycle < exported.hjson | cut -d ' ' -f 2 | python -m utils.import_cycle
```

### Announce Santas

Sends messages to Santas with links to whom they were matched.

```sh
python -m utils.announce_santas
```

### Send messages

Sends messages to specified users with the same message. Can be used to warn everyone
about deadlines.

```sh
python -m utils.send_message [OPTIONS] MESSAGE
```

Example:

```sh
python -m utils.export_users > exported.hjson

cat > message.txt <<EOF
Hi! It's a reminder that deadline is coming!
EOF

python -m utils.send_message message.txt < exported.hjson
```

Another example showing how to send a message to users who didn't send a gift:

```sh
python -m utils.export_users \
    | hjson -j \
    | jq 'map(select(.is_completed == true and .delivery_status == "not_sent"))' \
    | hjson > target.hjson

python -m utils.send_message message.txt < target.hjson
```

### Draw a graph

Generates graphviz (DOT) code to draw a graph of participants.

```sh
python -m utils.draw_graph
```

Example:

```sh
python -m utils.export_users > exported.hjson

python -m utils.draw_graph < exported.hjson \
    | dot -Tpng > graph.png
```

## Contribute

Feel free to create PRs. Be sure you installed pre-commit hooks before pushing:
`pre-commit install`.

Code is licensed by 3-Clause BSD License.
