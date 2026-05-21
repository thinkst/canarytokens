# If any packages or tools are not available through devcontainer features, install them here.
FROM mcr.microsoft.com/devcontainers/base:debian-11

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    default-mysql-client \
    dnsutils \
    libzbar0 \
    osslsigncode \
    subversion \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

CMD [ "sleep", "infinity" ]
