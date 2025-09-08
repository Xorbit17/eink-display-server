FROM python:3.11-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    liblcms2-dev \
    libimagequant-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml

RUN pip install --upgrade pip setuptools wheel

FROM python:3.11-slim-bookworm AS runtime

ARG APP_USER=app
ARG APP_UID=10001
ARG APP_GID=10001
ARG PLAYWRIGHT=1

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=60 \
    IN_DOCKER=True

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libtiff6 \
    libopenjp2-7 \
    libwebp7 \
    liblcms2-2 \
    libimagequant0 \
    libheif1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g "${APP_GID}" "${APP_USER}" \
 && useradd --no-log-init -m -u "${APP_UID}" -g "${APP_GID}" -s /bin/bash "${APP_USER}"

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

COPY . /app

RUN chmod +x /app/run-service.sh

USER ${APP_USER}

EXPOSE 8000

# Optional: simple healthcheck (expects /health view; adjust as needed)
HEALTHCHECK --interval=30s --timeout=3s --retries=5 CMD curl -fsS http://localhost:8000/health || exit 1

# Use CMD (not ENTRYPOINT) to run the service script
CMD ["/bin/sh", "-lc", "/app/run-service.sh"]
