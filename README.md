# 🌐 Réseau de Partage de Fichiers P2P

Système de partage de fichiers sécurisé entre ordinateurs sur le même réseau local.

##  Fonctionnalités

-  **Découverte automatique** des PC sur le réseau
-  **Transfert de fichiers** direct entre PC (P2P)
-  **Permissions granulaires** :
  - Privé (1 destinataire)
  - Partagé (plusieurs destinataires)
  - Public (tout le réseau)
-  **Transfert de dossiers** complets
-  **Chiffrement** des fichiers sensibles
-  **Interface** simple en ligne de commande

##  Structure

```
reseau-partage/
├── server/          # Serveur central (annuaire)
│   ├── main.py      # Point d'entrée serveur
│   ├── database.py  # Base de données SQLite
│   └── config.py    # Configuration
├── client/          # Application client
│   ├── main.py      # Point d'entrée client
│   ├── network.py   # Communication réseau
│   ├── transfer.py  # Gestion des transferts
│   └── ui.py        # Interface utilisateur
├── shared/          # Code partagé
│   ├── protocol.py  # Protocole de communication
│   └── utils.py     # Utilitaires
├── storage/         # Dossier de stockage (fichiers reçus)
└── requirements.txt
```

##  Installation

### 1. Créer l'environnement virtuel

```bash
cd reseau-partage
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

##  Utilisation

### Démarrer le serveur (sur 1 PC)

```bash
python server/main.py
```

Le serveur démarre sur `http://0.0.0.0:5000`

### Démarrer un client (sur chaque PC)

```bash
python client/main.py --name PC1
```

Remplacer `PC1` par `PC2`, `PC3`, etc.

##  Test en Local (simuler 3 PC)

Ouvrir **3 terminaux** :

**Terminal 1 - Serveur :**
```bash
python server/main.py
```

**Terminal 2 - PC1 :**
```bash
python client/main.py --name PC1
```

**Terminal 3 - PC2 :**
```bash
python client/main.py --name PC2
```

**Terminal 4 - PC3 :**
```bash
python client/main.py --name PC3
```

##  Exemple d'utilisation

```bash
# Sur PC1
> send fichier.pdf PC2          # Envoyer à PC2 uniquement
> send rapport.docx PC2 PC3     # Envoyer à PC2 et PC3
> send image.png *              # Envoyer à tout le monde
> list                          # Voir les PC connectés
> received                      # Voir les fichiers reçus
> quit                          # Quitter
```

##  Sécurité

- Authentification simple par nom d'utilisateur
- Contrôle d'accès côté serveur
- Chiffrement optionnel (à venir)

##  Architecture

```
┌─────────┐         ┌─────────────────┐         ┌─────────┐
│   PC1   │←─── ───→│ Serveur Central │←─── ───→│   PC2   │
└─────────┘         │   (Annuaire)    │         └─────────┘
                    └─────────────────┘
                            ↑
                            │
                            ↓
                       ┌─────────┐
                       │   PC3   │
                       └─────────┘
```

- **Serveur** : Gère l'annuaire des PC, les permissions
- **Clients** : Envoient/reçoivent directement (P2P)
- **Transferts** : Directs entre clients pour la vitesse

##  Technologies

- **Python 3.11+**
- **Flask** : Serveur web
- **Requests** : Client HTTP
- **SQLite** : Base de données
- **Socket** : Transferts P2P
- **Threading** : Transferts multiples

##  Roadmap

- [x] Structure du projet
- [x] Serveur central
- [x] Client CLI basique
- [x] Transfert fichier simple
- [ ] Transfert de dossiers
- [ ] Interface graphique (PyQt5)
- [ ] Chiffrement AES-256
- [ ] Compression des fichiers
- [ ] Historique des transferts

##  Auteurs

Projet académique - Réseau de partage P2P

##  Licence

MIT
