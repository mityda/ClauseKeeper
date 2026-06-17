# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    CLAUSEKEEPER_DB=/data/clausekeeper.db

WORKDIR /app

RUN addgroup --system clausekeeper \
    && adduser --system --ingroup clausekeeper clausekeeper \
    && mkdir -p /data \
    && chown -R clausekeeper:clausekeeper /data

COPY --from=builder /opt/venv /opt/venv
COPY --chown=clausekeeper:clausekeeper app ./app
COPY --chown=clausekeeper:clausekeeper templates ./templates
COPY --chown=clausekeeper:clausekeeper static ./static
COPY --chown=clausekeeper:clausekeeper README.md ./README.md

USER clausekeeper

EXPOSE 8000
VOLUME ["/data"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
