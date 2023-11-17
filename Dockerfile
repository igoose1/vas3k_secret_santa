FROM python:3.11-alpine

ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_ENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_NO_INTERACTION=1

RUN pip install poetry==${POETRY_VERSION}
ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app
COPY pyproject.toml poetry.lock .
RUN poetry install --no-ansi --without dev

COPY "sesanta" "/app/sesanta"
COPY "utils" "/app/utils"
ENTRYPOINT ["poetry", "run"]
CMD ["python", "-m", "sesanta.bot"]
