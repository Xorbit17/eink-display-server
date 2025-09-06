# tools/development/Dockerfile

# ---------- Stage 1: build deps & install Python packages ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build-time OS deps for compiling wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    zlib1g-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

# Install app deps into a temporary prefix we can copy out of
COPY pyproject.toml /app/pyproject.toml
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install --prefix=/install .

# ---------- Stage 2: slim runtime with only runtime libs ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Runtime OS libs only (no compilers, no headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libopenjp2-7 \
    zlib1g \
    libheif1 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Python site-packages & scripts from builder
COPY --from=builder /install /usr/local

RUN playwright install --with-deps chromium

# Your scripts (you can also leave these in /app/tools and call them explicitly)
COPY tools/development/start.sh /usr/local/bin/start.sh
COPY tools/development/wait-for-postgres.sh /usr/local/bin/wait-for-postgres.sh
RUN chmod +x /usr/local/bin/*.sh
