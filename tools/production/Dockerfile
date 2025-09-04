FROM python:3.11-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build deps for Pillow / pillow-heif wheels (header packages)
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

# Copy requirements first to leverage layer caching
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip wheel \
 && pip wheel --wheel-dir /wheels -r /app/requirements.txt


########################
# Runtime: slim + only runtime libs
########################
FROM python:3.11-slim-bookworm AS runtime

ARG APP_USER=app
ARG APP_UID=10001
ARG APP_GID=10001
# Toggle Playwright/Chromium install to keep image small by default
ARG PLAYWRIGHT=1

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=60

# Runtime libs for Pillow / pillow-heif (no headers), plus curl for healthchecks
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

# Optional Playwright + Chromium (heavy). Enable with --build-arg PLAYWRIGHT=1
RUN if [ "$PLAYWRIGHT" = "1" ]; then \
      pip install --no-cache-dir playwright && \
      python -m playwright install --with-deps chromium; \
    fi

# Non-root user
RUN groupadd -g "${APP_GID}" "${APP_USER}" \
 && useradd --no-log-init -m -u "${APP_UID}" -g "${APP_GID}" -s /bin/bash "${APP_USER}"

WORKDIR /app

# Install deps from wheels built in the builder stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copy your project (including requirements.txt if you want it in the image)
COPY . /app

# Ensure the run script is executable
RUN chmod +x /app/run-service.sh

# Drop privileges
USER ${APP_USER}

EXPOSE 8000

# Optional: simple healthcheck (expects /health view; adjust as needed)
HEALTHCHECK --interval=30s --timeout=3s --retries=5 CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Use CMD (not ENTRYPOINT) to run the service script
CMD ["/bin/sh", "-lc", "/app/run-service.sh"]
