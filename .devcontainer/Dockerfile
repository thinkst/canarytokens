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

COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy

CMD [ "sleep", "infinity" ]

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
