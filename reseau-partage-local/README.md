# 🌐 Réseau de Partage P2P - Version Locale avec HA

Version locale multi-serveurs avec Haute Disponibilité, conçue pour fonctionner sur réseau local (LAN) sans connexion internet.

## 🎯 Différences avec la version Cloud

| Fonctionnalité | Version Cloud | Version Locale |
|----------------|---------------|----------------|
| Serveurs | 1 seul (PythonAnywhere) | Plusieurs avec HA |
| Réseau | Internet requis | LAN uniquement |
| Découverte | URL fixe | Auto-découverte UDP |
| Basculement | N/A | Automatique <15s |
| Installation | Navigateur | Application locale |

## 🚀 Démarrage Rapide

### 1. Installation

```bash
cd reseau-partage-local

# Créer virtualenv (local uniquement, pas versionné)
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

### 2. Lancer un Serveur

```bash
# PC1 - Serveur primaire
python launcher.py --mode server --name PC1

# PC2 - Serveur secondaire (backup)
python launcher.py --mode server --name PC2
```

### 3. Lancer un Client

```bash
# PC3 - Client seulement
python launcher.py --mode client --name PC3
```

## 📁 Structure

```
reseau-partage-local/
├── launcher.py           # Point d'entrée unique
├── server_local.py       # Serveur avec HA
├── discovery.py          # Découverte réseau UDP
├── ha_manager.py         # Gestion Haute Disponibilité
├── database.py           # Base de données
├── web/                  # Interface web
│   ├── templates/
│   └── static/
└── storage/              # Fichiers (non versionné)
```

## 🔐 Sécurité

- Mot de passe réseau partagé
- Tokens de session
- Isolation par permissions
- Fichiers chiffrés (optionnel)

## 📚 Documentation

Voir [Documentation/](Documentation/) pour plus de détails.
