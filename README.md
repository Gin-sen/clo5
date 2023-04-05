# Groupe de places_m 999858

# Infra

```txt
VM1 : 172.16.228.64:student:p?sk4aA9
VM2 : 172.16.228.81:student:(YcdA3YX
VM3 : 172.16.228.15:student:AAc=mo9T
```

Première connexion :
```bash
ssh student@172.16.228.64
ssh student@172.16.228.81
ssh student@172.16.228.15
```

## Setup

### Installation de Python

Installation de python 3.11

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

```bash
python3 -m pip install --user ansible
# Vérification
ansible --version
```

## Configuration avec Ansible

### Installation d'Ansible sur sa machine

- [Installation Python](https://www.python.org/downloads/)
- [Installation d'Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

### Lancement des scripts de configuration Ansible


# Dev

