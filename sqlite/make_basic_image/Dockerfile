ARG FROM_PLATFORM
ARG IMAGE_OFFICIAL_SQLITE_NAME
ARG IMAGE_OFFICIAL_SQLITE_VERSION
FROM --platform=${FROM_PLATFORM} ${IMAGE_OFFICIAL_SQLITE_NAME}:${IMAGE_OFFICIAL_SQLITE_VERSION} AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir sqlite-web
