# If any packages or tools are not available through devcontainer features, install them here.
FROM mcr.microsoft.com/devcontainers/base:debian-11

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    default-mysql-client \
    dnsutils \
    libzbar0 \
    osslsigncode \
    subversion \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="/usr/local/bin" sh

CMD [ "sleep", "infinity" ]
