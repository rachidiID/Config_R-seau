#  Projet Créé avec Succès !

##  Ce qui a été fait

### 1. Structure Complète du Projet ✓
```
reseau-partage/
├── server/              # Serveur central
│   ├── main.py         # API REST Flask
│   ├── database.py     # SQLite (annuaire + permissions)
│   └── config.py       # Configuration
├── client/              # Application client
│   ├── main.py         # Point d'entrée
│   ├── network.py      # Communication avec serveur
│   ├── transfer.py     # Transferts P2P
│   └── ui.py           # Interface CLI
├── shared/              # Code partagé
│   ├── protocol.py     # Protocole de communication
│   └── utils.py        # Utilitaires
└── storage/             # Fichiers reçus (créé automatiquement)
```

### 2. Fonctionnalités Implémentées ✓
-  **Découverte réseau** : Les PC se trouvent automatiquement via le serveur
-  **Transfert P2P** : Envoi direct entre PC (pas via le serveur)
-  **3 types de permissions** :
  - Privé (1 destinataire)
  - Partagé (liste spécifique)
  - Public (tout le réseau)
-  **Base de données** : SQLite pour annuaire et permissions
-  **Historique** : Enregistrement de tous les transferts
-  **Checksums** : Vérification d'intégrité des fichiers

### 3. Technologies Utilisées ✓
- **Python 3.11+**
- **Flask** : Serveur web REST
- **SQLite** : Base de données
- **Socket** : Transferts P2P
- **Threading** : Transferts multiples simultanés

---

##  Comment Commencer

### Étape 1 : Le serveur tourne déjà ! ✓
```
http://127.0.0.1:5000
http://10.55.95.252:5000
```

### Étape 2 : Ouvrir 3 nouveaux terminaux pour les clients

**Terminal 2 - PC1 :**
```bash
cd /home/rachidi/Base_de_données/reseau-partage
source venv/bin/activate
python client/main.py --name PC1 --port 5001
```

**Terminal 3 - PC2 :**
```bash
cd /home/rachidi/Base_de_données/reseau-partage
source venv/bin/activate
python client/main.py --name PC2 --port 5002
```

**Terminal 4 - PC3 :**
```bash
cd /home/rachidi/Base_de_données/reseau-partage
source venv/bin/activate
python client/main.py --name PC3 --port 5003
```

---

##  Test Rapide

### Sur PC1 : Voir les autres PC
```
PC1> list
```

### Sur PC1 : Créer un fichier de test
```bash
# Dans un autre terminal (sans quitter PC1)
echo "Message de test depuis PC1" > /tmp/test.txt
```

### Sur PC1 : Envoyer à PC2 (PRIVÉ)
```
PC1> send /tmp/test.txt PC2
```

### Sur PC2 : Vérifier réception
```
PC2> received
```

### Sur PC1 : Envoyer à tout le monde (PUBLIC)
```
PC1> send /tmp/test.txt *
```

---

##  Commandes Disponibles

| Commande | Description | Exemple |
|----------|-------------|---------|
| `list` | Voir les PC connectés | `list` |
| `send <fichier> <dest>` | Envoyer un fichier | `send doc.pdf PC2` |
| `send <fichier> PC1 PC2` | Envoyer à plusieurs | `send doc.pdf PC2 PC3` |
| `send <fichier> *` | Envoyer à tous | `send doc.pdf *` |
| `received` | Voir fichiers reçus | `received` |
| `status` | Statut du serveur | `status` |
| `help` | Aide | `help` |
| `quit` | Quitter | `quit` |

---

##  Scénarios d'Utilisation

### Scénario 1 : Envoi Privé (1 → 1)
```
PC1> send rapport.pdf PC2
```
-  PC2 reçoit le fichier
-  PC3 ne le voit pas

### Scénario 2 : Envoi Partagé (1 → N)
```
PC1> send presentation.pptx PC2 PC3
```
-  PC2 et PC3 reçoivent
-  PC4 (s'il existe) ne le voit pas

### Scénario 3 : Envoi Public (1 → Tous)
```
PC1> send annonce.txt *
```
-  Tous les PC en ligne reçoivent
-  Broadcast sur le réseau

---

##  Où Sont les Fichiers Reçus ?

```bash
# Structure créée automatiquement
reseau-partage/storage/
├── PC1/     # Fichiers reçus par PC1
├── PC2/     # Fichiers reçus par PC2
└── PC3/     # Fichiers reçus par PC3

# Voir les fichiers de PC2
ls -lh /home/rachidi/Base_de_données/reseau-partage/storage/PC2/

# Lire un fichier reçu
cat /home/rachidi/Base_de_données/reseau-partage/storage/PC2/test.txt
```

---

##  Vérifications

### Base de Données
```bash
# Voir la base de données
sqlite3 /home/rachidi/Base_de_données/reseau-partage/server/network.db

# Requêtes SQL utiles
SELECT * FROM peers;                    -- Tous les PC
SELECT * FROM files;                    -- Tous les fichiers
SELECT * FROM transfers;                -- Historique transferts
SELECT * FROM permissions;              -- Permissions
```

### Logs du Serveur
Le serveur affiche en temps réel :
- Enregistrements de PC
- Enregistrements de fichiers
- Transferts effectués

---

##  Prochaines Évolutions

### Phase 1 (Actuelle) ✓
- [x] Architecture client-serveur hybride
- [x] Transferts P2P
- [x] 3 types de permissions
- [x] Interface CLI

### Phase 2 (À Venir)
- [ ] **Interface graphique** (PyQt5)
- [ ] **Transfert de dossiers** complets
- [ ] **Barre de progression** graphique
- [ ] **Notifications** système

### Phase 3 (Sécurité)
- [ ] **Chiffrement** AES-256
- [ ] **Authentification** par mot de passe
- [ ] **Certificats SSL** pour le serveur
- [ ] **Signature** des fichiers

### Phase 4 (Avancé)
- [ ] **Reprise sur erreur** de transfert
- [ ] **Compression** automatique
- [ ] **Aperçu** des fichiers
- [ ] **Recherche** dans l'historique

---

##  Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier si le port 5000 est occupé
lsof -i :5000

# Utiliser un autre port
python server/main.py --port 5010
```

### Un client ne se connecte pas
```bash
# Vérifier que le serveur tourne
curl http://localhost:5000/api/status

# Vérifier le réseau
ping localhost
```

### Fichier non reçu
```bash
# Vérifier les permissions du dossier storage
ls -la storage/

# Vérifier que le port client n'est pas bloqué
sudo ufw allow 5001:5010/tcp
```

---

##  Documentation

- **README.md** : Vue d'ensemble du projet
- **QUICKSTART.md** : Guide de démarrage rapide
- **Ce fichier** : Résumé de ce qui a été créé

---

##  Architecture Technique

### Flux d'un Transfert

```
1. PC1 envoie fichier à PC2

PC1                    Serveur                    PC2
 |                        |                         |
 |-- Register file -----> |                         |
 |                        |-- Check permission ---> |
 |                        |<-- Permission OK -------|
 |<-- File ID registered -|                         |
 |                        |                         |
 |======== Direct P2P Transfer ===================> |
 |                        |                         |
 |-- Log transfer ------> |                         |
 |                        |                         |
```

### Types de Permissions

| Type | Description | Exemple |
|------|-------------|---------|
| **private** | 1 seul destinataire | `send doc.pdf PC2` |
| **shared** | Liste spécifique | `send doc.pdf PC2 PC3` |
| **public** | Tous les PC | `send doc.pdf *` |

---