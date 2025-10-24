# If any packages or tools are not available through devcontainer features, install them here.
FROM --platform=linux/${BUILDARCH} python:3.9@sha256:17e2d81e5757980ee40742d77dd5d3e1a69ad0d6dacb13064e1b018a6664ec72

COPY custom-install.sh /tmp/custom-installs.sh
RUN apt-get update \
    && /bin/bash /tmp/custom-installs.sh
# Clean up
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/custom-installs.sh

CMD [ "sleep", "infinity" ]

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
