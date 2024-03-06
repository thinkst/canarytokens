# Install terraform and packer
apt-get update
apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

apt-get update
apt-get install terraform
apt-get install packer

curl -Lo ./terraform-docs.tar.gz https://github.com/terraform-docs/terraform-docs/releases/download/v0.16.0/terraform-docs-v0.16.0-$(uname)-amd64.tar.gz
tar -xzf terraform-docs.tar.gz
chmod +x terraform-docs
mv terraform-docs /usr/local/terraform-docs

# Install mysql (default repos are broken for buster)
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C
wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb
DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.22-1_all.deb
apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client

apt install -y wireguard-tools

mkdir -p /etc/apt/keyrings
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 234654DA9A296436
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list
apt-get update -y
apt-get install -y kubectl=1.28.1-1.1
