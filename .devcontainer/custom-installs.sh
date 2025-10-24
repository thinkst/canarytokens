# Install MySQL client (using default-mysql-client for Debian 11+)
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends\
    default-mysql-client \
    libzbar0 \
    osslsigncode \
    dnsutils \
    subversion
