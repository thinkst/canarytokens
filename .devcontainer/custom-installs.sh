# Install mysql (default repos are broken for buster)
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C
wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb
DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.22-1_all.deb
apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client
