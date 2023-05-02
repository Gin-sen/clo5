# Groupe de places_m 999858

# Infra

A partir d'ici, nous considèrerons le dossier `ansible_dir` comme le répertoire racine.


```txt
VM1 : 172.16.228.64:student:p?sk4aA9
VM2 : 172.16.228.81:student:(YcdA3YX
VM3 (master) : 172.16.228.15:student:AAc=mo9T
```

Première connexion :
```bash
ssh student@172.16.228.64
ssh student@172.16.228.81
ssh student@172.16.228.15
```

## Setup /etc/hosts

Ajouter ces lignes dans votre `/etc/hosts` (ou `%System%/drivers/etc/hosts` pour Windows):
```txt
172.16.228.15 gitlab.example.local
172.16.228.81 registry.example.local
```
### Gitlab

Login / mdp étudiant [Gitlab](http://gitlab.example.local/) :
`login_ETNA` / `Pass123*`

Login / mdp prof [Gitlab](http://gitlab.example.local/) :
`login_ETNA` / `P@SSW0RD`

Repository : http://gitlab.example.local/gitlab-instance-352af650/clo5

### Utiliser `kubectl`

`kubectl --kubeconfig=kubeconfig.yaml get nodes`

### Consulter le registry

Télécharger la CA et lancer la commande d'update :
```bash
sudo scp places_m@172.16.228.15:/tmp/tls-common/ca-certificate.crt /etc/ssl/certs/registry.example.local.crt
sudo update-ca-certificates
```

Voir la doc Docker pour consulter l'api en détail :

`sudo curl 'https://registry.example.local/v2/_catalog/' --cacert /etc/ssl/certs/registry.example.local.crt`

## Setup Infra
### Installation de Python

- [Téléchargement officiel Python](https://www.python.org/downloads/)
ou
- Installation de python 3.11 avec PPA :

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
# Vérification
python3 --version
```

Installation de `pip`
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
# Vérification
python3 -m pip -V
```

### Installation d'Ansible

- [Documentation Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
```bash
python3 -m pip install --user -r requirements.txt
# Vérification
ansible --version
```

Prérequis sur local:
- `sshpass`

```bash
sudo apt-get install -y sshpass
```

### Création de rôle Ansible

Dans le dossier `roles` :
```bash
ansible-galaxy role init gitlab
ansible-galaxy role init kubernetes
ansible-galaxy role init docker_registry
```

### Création d'un mot de passe dans le Vault

```bash
ansible-vault -v encrypt roles/gitlab/vars/admin.yml
ansible-vault -v decrypt roles/gitlab/vars/admin.yml
```


### Lancement du playbook

Prérequis:
- module `kubernetes.core` d'Ansible
- module `ansible.utils` d'Ansible
- module `ansible.posix` d'Ansible
- module `community.crypto` d'Ansible
- module `community.general` d'Ansible

```bash
ansible-galaxy collection install kubernetes.core
ansible-galaxy collection install ansible.utils
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.crypto
ansible-galaxy collection install community.general
```

### Usage standard

Pas de `kubeadm init` :
```bash
ansible-playbook infrastructure.yaml -i hosts
```

#### Initialisation du cluster

Si vous ne précisez pas cette variable, le script de création de cluster Kubernetes ne se lancera pas

```bash
ansible-playbook infrastructure.yaml -i hosts -e kubernetes_init_host=172.16.228.15
```

## Clean stuff (tmp)

```bash
sudo kubeadm reset -f
sudo iptables -P INPUT ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X
sudo ctr -n k8s.io c rm $(sudo ctr -n k8s.io c ls -q)
sudo systemctl stop kubelet
sudo systemctl stop containerd
sudo rm -r /etc/cni/net.d
sudo rm -r /opt/cni/bin
sudo reboot now
```


## Notes 
PB de certificat depuis le gitlab runner vers le registry. Fix + patch rapide dans les notes : https://docs.gitlab.com/runner/configuration/tls-self-signed.html#supported-options-for-self-signed-certificates-targeting-the-gitlab-server

Conf registry (tls): https://docs.docker.com/registry/configuration/#http

Enable registry dans gitlab ? :  https://docs.gitlab.com/ee/administration/packages/container_registry.html#enable-the-container-registry



# Dev

