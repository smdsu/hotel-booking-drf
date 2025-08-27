FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --only=main && \
    rm -rf $POETRY_CACHE_DIR

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
