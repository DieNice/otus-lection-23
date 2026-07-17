FROM python:3.12-slim-bullseye AS build

WORKDIR /usr/src/
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=2.2.1

RUN apt-get update && pip install --no-cache-dir poetry==${POETRY_VERSION} \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --no-root --no-cache --without=dev

COPY  ./app ./app

FROM python:3.12-slim-bullseye AS prod

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PATH=/usr/local/lib/python3.12/site-packages:$PATH \
    PATH=/usr/local/bin:$PATH

COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# COPY ./migrations/ /usr/src/migrations
# COPY ./alembic.ini /usr/src/alembic.ini
COPY --from=build /usr/src/app /usr/src/app

WORKDIR /usr/src/

CMD [ "uvicorn", "app.app:app", "--workers=3", "--host=0.0.0.0", "--port=8080"]


FROM python:3.12-slim-bullseye AS test

WORKDIR /usr/src/
COPY ./test /usr/src/test

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=2.1.3\
    PATH=/usr/local/lib/python3.12/site-packages:$PATH \
    PATH=/usr/local/bin:$PATH

COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# COPY ./alembic.ini ./alembic.ini
COPY --from=build /usr/src/poetry.lock /usr/src/pyproject.toml ./

RUN poetry install --no-root --no-cache --only=dev

# COPY ./migrations/ /usr/src/migrations
# COPY ./alembic.ini /usr/src/alembic.ini
COPY --from=build /usr/src/app /usr/src/app

WORKDIR /usr/src/

CMD [ "uvicorn", "app.app:app", "--workers=3", "--host=0.0.0.0", "--port=8080"]
