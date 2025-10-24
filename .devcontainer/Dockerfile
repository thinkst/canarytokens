# If any packages or tools are not available through devcontainer features, install them here.
FROM mcr.microsoft.com/devcontainers/python:3.9

# Install custom packages not available through features
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # custom package
    && apt-get autoremove -y && apt-get clean -y

# Install custom tools here
