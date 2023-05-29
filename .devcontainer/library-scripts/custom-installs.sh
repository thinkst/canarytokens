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
wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb
DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.22-1_all.deb
apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client

apt install -y wireguard-tools

# curl -sSL https://install.python-poetry.org | POETRY_HOME=/home/vscode/.local python -
# /home/vscode/.local/bin/poetry config virtualenvs.in-project true

# wget https://golang.org/dl/go1.18.2.linux-amd64.tar.gz
# tar -C /usr/local -xzf go1.18.2.linux-amd64.tar.gz
# /usr/local/go/bin/go install github.com/aquasecurity/tfsec/cmd/tfsec@latest

sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg  https://dl.k8s.io/apt/doc/apt-key.gpg
sudo install -o root -g root -m 644 /usr/share/keyrings/kubernetes-archive-keyring.gpg /etc/apt/trusted.gpg.d/
sudo echo "deb [signed-by=/etc/apt/trusted.gpg.d/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update -y
sudo apt-get install -y kubectl
