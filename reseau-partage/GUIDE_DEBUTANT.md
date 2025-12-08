#  Guide Complet pour Débutants - Réseau de Partage de Fichiers

##  Table des Matières
1. [C'est quoi ce projet ?](#cest-quoi-ce-projet)
2. [Comment ça marche ?](#comment-ça-marche)
3. [Installation sur CHAQUE PC](#installation-sur-chaque-pc)
4. [Configuration Réseau](#configuration-réseau)
5. [Démarrage Pas à Pas](#démarrage-pas-à-pas)
6. [Utilisation Concrète](#utilisation-concrète)
7. [Dépannage](#dépannage)

---

##  C'est quoi ce projet ?

### Imaginez...

Vous avez **3 ordinateurs** dans la même pièce (ou sur le même WiFi) :
- PC de **Alice** (votre PC)
- PC de **Bob** (PC de votre ami)
- PC de **Charlie** (PC de votre autre ami)

**AVANT ce projet :**
- Pour envoyer un fichier à Bob, vous devez :
  - Utiliser WhatsApp / Email / USB
  - Bob doit télécharger
  - Charlie ne peut pas avoir le fichier facilement

**AVEC ce projet :**
- Alice tape : `send photo.jpg Bob` → Bob reçoit INSTANTANÉMENT
- Alice tape : `send video.mp4 *` → Bob ET Charlie reçoivent EN MÊME TEMPS
- Tout reste **privé** : si Alice envoie à Bob, Charlie ne voit rien

### En Résumé

C'est comme un **WhatsApp privé** mais :
-  Fonctionne sans Internet
-  Vitesse maximale (réseau local)
-  Vous contrôlez qui voit quoi
-  Aucun serveur externe (tout reste chez vous)

---

##  Comment ça marche ?

### Architecture Simple

```
┌─────────────────────────────────────────────────────────┐
│                    VOTRE RÉSEAU LOCAL                    │
│                   (WiFi ou Câble Ethernet)               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│   ┌──────────┐         ┌──────────┐        ┌──────────┐│
│   │  PC 1    │         │  SERVEUR │        │  PC 2    ││
│   │ (Alice)  │◄────────┤  CENTRAL ├───────►│  (Bob)   ││
│   │          │  "Qui   │          │  "Qui  │          ││
│   │ 💼       │   est   │  📋      │   est  │ 💼       ││
│   └──────────┘   là?"  └──────────┘   là?" └──────────┘│
│        │                     ▲                   │      │
│        │                     │                   │      │
│        │              ┌──────────┐               │      │
│        │              │  PC 3    │               │      │
│        │              │(Charlie) │               │      │
│        │              │          │               │      │
│        │              │ 💼       │               │      │
│        │              └──────────┘               │      │
│        │                                         │      │
│        └─────────────────────────────────────────┘      │
│             Transfert DIRECT (rapide!)                  │
└─────────────────────────────────────────────────────────┘
```

### Les 3 Composants

#### 1. **SERVEUR CENTRAL** (1 seul, sur un PC)
**Rôle :** C'est comme l'annuaire téléphonique
- Sait qui est connecté (Alice, Bob, Charlie)
- Sait où ils sont (adresses IP)
- Vérifie les permissions ("Alice peut envoyer à Bob ?")

**Comparaison :** C'est le réceptionniste d'un hôtel qui sait dans quelle chambre est chacun

#### 2. **CLIENT** (sur chaque PC)
**Rôle :** C'est votre application
- S'enregistre auprès du serveur ("Je suis Alice")
- Envoie des fichiers aux autres
- Reçoit des fichiers des autres

**Comparaison :** C'est votre téléphone qui appelle les gens

#### 3. **BASE DE DONNÉES** (automatique)
**Rôle :** Mémorise tout
- Liste des PC connectés
- Historique des fichiers envoyés
- Permissions ("ce fichier est pour Bob uniquement")

---

##  Installation sur CHAQUE PC

### Configuration Requise

**CHAQUE PC doit avoir :**
-  Python 3.11+ installé
-  Même réseau WiFi / Ethernet
-  Une copie du projet

---

###  ÉTAPE 1 : Copier le Projet sur Chaque PC

#### Option A : Avec Git (Recommandé)

**Sur CHAQUE PC, ouvrez un terminal et tapez :**

```bash
# 1. Aller dans un dossier de travail
cd ~/Documents

# 2. Cloner le projet GitHub
git clone https://github.com/rachidiID/neo4j-graphes-amitie.git

# 3. Aller dans le dossier du projet réseau
cd neo4j-graphes-amitie/reseau-partage
```

#### Option B : Avec Clé USB (Si pas de Git)

**Sur le PC d'Alice (qui a le projet) :**

```bash
# 1. Copier tout le dossier sur une clé USB
cp -r /home/rachidi/Base_de_données/reseau-partage /media/USB/

# 2. Débrancher la clé
# 3. Brancher sur le PC de Bob
# 4. Sur le PC de Bob :
cp -r /media/USB/reseau-partage ~/Documents/
```

Répéter pour chaque PC !

---

### 🔧 ÉTAPE 2 : Installer Python et Dépendances

**Sur CHAQUE PC :**

#### Vérifier Python

```bash
python3 --version
```

**Résultat attendu :** `Python 3.11.2` ou supérieur

**Si Python n'est pas installé :**

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Windows (télécharger depuis python.org)
# MacOS
brew install python3
```

#### Installer les Dépendances

**Sur CHAQUE PC, dans le dossier du projet :**

```bash
# 1. Aller dans le dossier
cd ~/Documents/reseau-partage

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement
source venv/bin/activate
# Sur Windows : venv\Scripts\activate

# 4. Installer les bibliothèques
pip install -r requirements.txt
```

**Résultat attendu :**
```
Successfully installed Flask-3.0.0 Flask-CORS-4.0.0 ...
 Installation terminée !
```

---

###  ÉTAPE 3 : Configuration Réseau

**IMPORTANT :** Tous les PC doivent être sur le **MÊME réseau** !

#### Vérifier le Réseau

**Sur CHAQUE PC :**

```bash
# Voir votre adresse IP
ip addr show | grep inet

# Ou plus simple
hostname -I
```

**Exemple de résultats :**
- PC Alice : `192.168.1.10`
- PC Bob : `192.168.1.20`
- PC Charlie : `192.168.1.30`

**Les 3 premiers chiffres doivent être IDENTIQUES** (`192.168.1.xxx`)

#### Si les Adresses sont Différentes

Tous les PC doivent être :
-  Sur le même WiFi, OU
-  Branchés au même routeur avec câble Ethernet

**Exemple WiFi :**
- Alice : Connectée au WiFi "MonWiFi"
- Bob : Connectée au WiFi "MonWiFi"  (pas "WiFi-Voisin" )
- Charlie : Connectée au WiFi "MonWiFi" 

---

##  Démarrage Pas à Pas

### Qui fait Quoi ?

**DÉCISION IMPORTANTE :** Il faut choisir **1 PC pour le serveur**

| Rôle | PC | Personne | Ce qu'il fait |
|------|-----|----------|---------------|
| **SERVEUR** | PC 1 | Alice | Lance le serveur central (1 seule fois) |
| **CLIENT** | PC 2 | Bob | Lance l'application client |
| **CLIENT** | PC 3 | Charlie | Lance l'application client |

**Note :** Le PC serveur peut AUSSI être un client !

---

###  SUR LE PC SERVEUR (PC d'Alice)

**Terminal 1 - Démarrer le Serveur**

```bash
# 1. Aller dans le dossier
cd ~/Documents/reseau-partage

# 2. Activer l'environnement
source venv/bin/activate

# 3. Démarrer le serveur
python server/main.py
```

**Résultat attendu :**
```
✓ Base de données initialisée : .../server/network.db
==================================================
 SERVEUR DE PARTAGE P2P
==================================================
Host: 0.0.0.0
Port: 5000
Base de données: .../server/network.db
==================================================

Serveur démarré ! Utilisez Ctrl+C pour arrêter.

 * Running on http://192.168.1.10:5000  ← NOTER CETTE ADRESSE IP !
```

**IMPORTANT :** Noter l'adresse IP affichée (ex: `192.168.1.10`)

**LAISSER CE TERMINAL OUVERT** (ne pas fermer, le serveur doit tourner)

---

###  SUR LE PC D'ALICE (Client Alice)

**Terminal 2 - Alice se connecte**

```bash
# 1. NOUVEAU TERMINAL (Ctrl+Shift+T)
cd ~/Documents/reseau-partage

# 2. Activer l'environnement
source venv/bin/activate

# 3. Lancer le client Alice
python client/main.py --name Alice --port 5001
```

**Résultat attendu :**
```
==================================================
🌐  RÉSEAU DE PARTAGE P2P - Alice
==================================================
✓ Enregistré sur le serveur en tant que: Alice
  IP: 192.168.1.10:5001

✓ Serveur de réception démarré sur le port 5001

 Client prêt ! Tapez 'help' pour voir les commandes.

Alice>
```

**Taper `help` pour voir les commandes :**
```
Alice> help
```

---

###  SUR LE PC DE BOB (Client Bob)

**Bob doit savoir l'IP du serveur** (celle notée plus haut : `192.168.1.10`)

```bash
# 1. Ouvrir un terminal
cd ~/Documents/reseau-partage

# 2. Activer l'environnement
source venv/bin/activate

# 3. Lancer le client Bob
python client/main.py --name Bob --port 5001 --server http://192.168.1.10:5000
                                                      ^^^^^^^^^^^^^^^^^^^^
                                            REMPLACER par l'IP du serveur !
```

**Résultat attendu :**
```
==================================================
🌐  RÉSEAU DE PARTAGE P2P - Bob
==================================================
✓ Enregistré sur le serveur en tant que: Bob
  IP: 192.168.1.20:5001

✓ Serveur de réception démarré sur le port 5001

 Client prêt ! Tapez 'help' pour voir les commandes.

Bob>
```

---

###  SUR LE PC DE CHARLIE (Client Charlie)

**Même chose que Bob :**

```bash
# 1. Ouvrir un terminal
cd ~/Documents/reseau-partage

# 2. Activer l'environnement
source venv/bin/activate

# 3. Lancer le client Charlie
python client/main.py --name Charlie --port 5001 --server http://192.168.1.10:5000
```

**Résultat attendu :**
```
Charlie>
```

---

##  Utilisation Concrète - Exemples Réels

### Exemple 1 : Alice Envoie une Photo à Bob

**Sur le PC d'Alice :**

```bash
# 1. Voir qui est connecté
Alice> list

 PC CONNECTÉS (2):

Nom             Adresse IP           Port       Statut
-------------------------------------------------------
Bob             192.168.1.20         5001        En ligne
Charlie         192.168.1.30         5001        En ligne


# 2. Envoyer la photo (UNIQUEMENT à Bob)
Alice> send /home/alice/photo.jpg Bob

📦 Préparation de l'envoi:
  Fichier: photo.jpg
  Taille: 2.3 MB
  Destinataires: Bob
  Permission: private

 Fichier enregistré (ID: 1)

📤 Envoi vers Bob...
Progression: 100.0%
✓ Fichier envoyé avec succès

 Transfert terminé: 1/1 réussis
```

**Sur le PC de Bob (AUTOMATIQUEMENT) :**

```bash
Bob> 
📥 Réception: photo.jpg (2.3 MB) de 192.168.1.20
Progression: 100.0%
✓ Fichier reçu: /home/bob/Documents/reseau-partage/storage/Bob/photo.jpg
  Checksum: a1b2c3d4...

# Bob peut vérifier
Bob> received

 FICHIERS REÇUS (1):

Nom                            Taille
---------------------------------------------
photo.jpg                      2.3 MB
```

**Sur le PC de Charlie :**
```bash
Charlie> received

 Aucun fichier reçu
```
**Charlie NE VOIT PAS la photo** (c'était privé pour Bob uniquement)

---

### Exemple 2 : Alice Envoie un Document à Bob ET Charlie

**Sur le PC d'Alice :**

```bash
Alice> send /home/alice/rapport.pdf Bob Charlie

📦 Préparation de l'envoi:
  Fichier: rapport.pdf
  Taille: 450 KB
  Destinataires: Bob, Charlie
  Permission: shared

 Fichier enregistré (ID: 2)

📤 Envoi vers Bob...
✓ Fichier envoyé avec succès

📤 Envoi vers Charlie...
✓ Fichier envoyé avec succès

 Transfert terminé: 2/2 réussis
```

**Sur le PC de Bob :**
```bash
📥 Réception: rapport.pdf (450 KB) de 192.168.1.20
✓ Fichier reçu

Bob> received
 FICHIERS REÇUS (2):
photo.jpg                      2.3 MB
rapport.pdf                    450 KB
```

**Sur le PC de Charlie :**
```bash
📥 Réception: rapport.pdf (450 KB) de 192.168.1.20
✓ Fichier reçu

Charlie> received
 FICHIERS REÇUS (1):
rapport.pdf                    450 KB
```

---

### Exemple 3 : Alice Envoie un Message à Tout le Monde

**Sur le PC d'Alice :**

```bash
# 1. Créer un fichier texte
# (Dans un autre terminal)
echo "Réunion demain à 14h" > /tmp/annonce.txt

# 2. Envoyer à TOUS
Alice> send /tmp/annonce.txt *

 Envoi public à 2 PC

📦 Préparation de l'envoi:
  Fichier: annonce.txt
  Taille: 24 B
  Destinataires: Bob, Charlie
  Permission: public

 Transfert terminé: 2/2 réussis
```

**Bob ET Charlie reçoivent TOUS LES DEUX :**

```bash
📥 Réception: annonce.txt (24 B) de 192.168.1.20
✓ Fichier reçu
```

---

##  Ce Qui a Été Implémenté - Explications Terre à Terre

### 1. **Serveur Central** (`server/main.py`)

**C'est quoi ?** Un mini-site web qui tourne sur un PC

**À quoi ça sert ?**
- Savoir qui est connecté ("Alice est là, Bob aussi")
- Donner l'adresse de chacun ("Alice est au 192.168.1.10")
- Vérifier les permissions ("Bob peut recevoir ce fichier d'Alice")

**Analogie :** C'est comme la réception d'un hôtel :
- Vous appelez la réception : "Je cherche Monsieur Bob"
- Réception : "Il est dans la chambre 205"
- Vous allez directement à la 205

### 2. **Base de Données** (`server/database.py`)

**C'est quoi ?** Un fichier qui mémorise tout

**À quoi ça sert ?**
- Table `peers` : Liste de tous les PC (Alice, Bob, Charlie)
- Table `files` : Liste de tous les fichiers partagés
- Table `permissions` : Qui peut voir quoi
- Table `transfers` : Historique (Alice a envoyé à Bob à 14h30)

**Analogie :** C'est comme un cahier de notes :
```
Page 1 - Liste des gens :
  - Alice : 192.168.1.10, en ligne
  - Bob : 192.168.1.20, en ligne

Page 2 - Fichiers partagés :
  - photo.jpg : propriétaire=Alice, pour=Bob

Page 3 - Historique :
  - 14:30 : Alice → Bob : photo.jpg (succès)
```

### 3. **Client Réseau** (`client/network.py`)

**C'est quoi ?** Le téléphone qui appelle le serveur

**À quoi ça sert ?**
- S'enregistrer : "Bonjour, je suis Alice !"
- Demander la liste : "Qui est connecté ?"
- Enregistrer un fichier : "Je veux envoyer photo.jpg à Bob"

**Exemple de conversation :**
```
Alice → Serveur : "Je suis Alice, mon IP est 192.168.1.10"
Serveur → Alice : "OK, enregistrée !"

Alice → Serveur : "Qui est connecté ?"
Serveur → Alice : "Bob (192.168.1.20) et Charlie (192.168.1.30)"

Alice → Serveur : "Je veux envoyer photo.jpg à Bob"
Serveur → Alice : "Permission accordée, file_id = 1"
```

### 4. **Transfert de Fichiers** (`client/transfer.py`)

**C'est quoi ?** Le facteur qui livre les colis

**À quoi ça sert ?**
- **Envoyer** : Lire le fichier, le découper en morceaux, envoyer chaque morceau
- **Recevoir** : Écouter, recevoir les morceaux, reconstituer le fichier
- **Vérifier** : Calculer le checksum (signature du fichier) pour vérifier qu'il n'est pas corrompu

**Analogie :** Envoyer un puzzle par la poste :
1. Alice découpe le puzzle en 100 morceaux
2. Elle envoie chaque morceau à Bob
3. Bob reçoit les morceaux et les assemble
4. Bob vérifie : "J'ai bien 100 morceaux, image complète !"

### 5. **Interface CLI** (`client/ui.py`)

**C'est quoi ?** Le menu du restaurant

**À quoi ça sert ?**
- Afficher les commandes disponibles (`help`)
- Montrer les PC connectés (`list`)
- Afficher les fichiers reçus (`received`)
- Jolie mise en forme

**Analogie :** Au lieu de taper du code compliqué, vous tapez juste :
```
send photo.jpg Bob
```
Au lieu de :
```python
transfer.send_file('/home/alice/photo.jpg', '192.168.1.20', 5001)
```

### 6. **Protocole de Communication** (`shared/protocol.py`)

**C'est quoi ?** Le langage commun entre tout le monde

**À quoi ça sert ?**
- Définir les "mots" que tout le monde comprend
- Message "REGISTER" = "Je me connecte"
- Message "REQUEST_SEND" = "Je veux envoyer un fichier"

**Analogie :** C'est comme parler la même langue :
- Au lieu que Alice parle français, Bob anglais, Charlie espagnol
- Tout le monde parle "ProtocoleP2P" :
  - "BONJOUR" = Je me connecte
  - "LISTE" = Qui est là ?
  - "ENVOYER" = J'envoie un fichier

---

##  Résumé : Les 3 Types de Permissions

### 1. **PRIVÉ** (1 seul destinataire)

**Commande :** `send fichier.txt Bob`

**Qui voit ?**
-  Bob reçoit
-  Charlie ne voit rien
-  Personne d'autre

**Exemple réel :** Envoyer votre mot de passe WiFi à un ami

---

### 2. **PARTAGÉ** (liste spécifique)

**Commande :** `send fichier.txt Bob Charlie`

**Qui voit ?**
-  Bob reçoit
-  Charlie reçoit
-  Les autres ne voient rien

**Exemple réel :** Envoyer un document de groupe à vos coéquipiers

---

### 3. **PUBLIC** (tout le monde)

**Commande :** `send fichier.txt *`

**Qui voit ?**
-  Bob reçoit
-  Charlie reçoit
-  Tous les PC connectés reçoivent

**Exemple réel :** Annoncer une réunion à toute l'équipe

---

##  Dépannage - Problèmes Courants

### Problème 1 : "Impossible de contacter le serveur"

**Message d'erreur :**
```
 Impossible de contacter le serveur
```

**Causes possibles :**

1. **Le serveur n'est pas démarré**
   - **Solution :** Aller sur le PC serveur, vérifier le Terminal 1
   - Vous devez voir : `Running on http://...`

2. **Mauvaise adresse IP**
   - **Solution :** Vérifier l'IP du serveur
   ```bash
   # Sur le PC serveur
   hostname -I
   ```
   - Utiliser cette IP dans `--server http://IP:5000`

3. **Firewall bloque**
   - **Solution :**
   ```bash
   # Sur le PC serveur
   sudo ufw allow 5000/tcp
   sudo ufw allow 5001/tcp
   ```

---

### Problème 2 : "PC non trouvé"

**Message d'erreur :**
```
⚠️  PC non trouvé ou hors ligne: Bob
```

**Causes possibles :**

1. **Bob n'est pas connecté**
   - **Solution :** Vérifier que Bob a lancé son client
   ```bash
   # Sur le PC de Bob
   python client/main.py --name Bob --port 5001 --server http://IP:5000
   ```

2. **Nom mal orthographié**
   - **Solution :** Les noms sont sensibles à la casse !
   - `Bob` ≠ `bob` ≠ `BOB`
   - Taper `list` pour voir les noms exacts

---

### Problème 3 : "Port déjà utilisé"

**Message d'erreur :**
```
OSError: [Errno 98] Address already in use
```

**Cause :** Le port 5000 ou 5001 est déjà pris

**Solution :**

```bash
# Vérifier qui utilise le port
lsof -i :5000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
python server/main.py --port 5010
python client/main.py --name Alice --port 5011 --server http://IP:5010
```

---

### Problème 4 : "Fichier non reçu"

**Symptôme :** Alice envoie, mais Bob ne reçoit rien

**Vérifications :**

1. **Bob est-il en ligne ?**
   ```bash
   # Sur Alice
   Alice> list
   # Vérifier que Bob apparaît avec 🟢
   ```

2. **Le fichier existe-t-il ?**
   ```bash
   # Sur Alice
   ls -lh /chemin/vers/fichier.txt
   ```

3. **Permissions du dossier storage ?**
   ```bash
   # Sur Bob
   ls -la ~/Documents/reseau-partage/storage/Bob/
   # Doit être accessible en écriture
   ```

4. **Firewall bloque les transferts ?**
   ```bash
   # Sur Bob
   sudo ufw allow 5001/tcp
   ```

---

## 📊 Schéma Récapitulatif Final

```
CONFIGURATION COMPLÈTE - 3 PC

┌─────────────────────────────────────────────────────────────┐
│                    RÉSEAU LOCAL WiFi/Ethernet                │
│                      (192.168.1.xxx)                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   PC ALICE    │     │    PC BOB     │     │  PC CHARLIE   │
│               │     │               │     │               │
│ IP: .1.10     │     │ IP: .1.20     │     │ IP: .1.30     │
├───────────────┤     ├───────────────┤     ├───────────────┤
│               │     │               │     │               │
│ SERVEUR       │     │               │     │               │
│ :5000         │     │               │     │               │
│ + CLIENT      │     │ CLIENT        │     │ CLIENT        │
│ :5001         │     │ :5001         │     │ :5001         │
│               │     │               │     │               │
│ Terminal 1:   │     │ Terminal:     │     │ Terminal:     │
│ server/main   │     │ client/main   │     │ client/main   │
│               │     │ --name Bob    │     │ --name Charlie│
│ Terminal 2:   │     │ --port 5001   │     │ --port 5001   │
│ client/main   │     │ --server      │     │ --server      │
│ --name Alice  │     │ http://.1.10  │     │ http://.1.10  │
│ --port 5001   │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │◄────────────────────┼────────────────────►│
        │    Transferts P2P Directs (rapides)       │
        └───────────────────────────────────────────┘
```

---

## ✅ Checklist de Démarrage

### Sur CHAQUE PC :

- [ ] Python 3.11+ installé (`python3 --version`)
- [ ] Projet copié (`git clone` ou USB)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Même réseau WiFi/Ethernet
- [ ] Adresse IP notée (`hostname -I`)

### Sur le PC SERVEUR (Alice) :

- [ ] Terminal 1 : Serveur démarré (`python server/main.py`)
- [ ] IP du serveur notée (ex: `192.168.1.10`)
- [ ] Terminal 2 : Client Alice lancé

### Sur les PC CLIENTS (Bob, Charlie) :

- [ ] Client lancé avec `--server http://IP_SERVEUR:5000`
- [ ] Message "✅ Client prêt !" affiché
- [ ] Commande `list` montre les autres PC

### Test Final :

- [ ] Alice tape `list` → Voit Bob et Charlie
- [ ] Alice crée un fichier : `echo "Test" > /tmp/test.txt`
- [ ] Alice envoie : `send /tmp/test.txt Bob`
- [ ] Bob tape `received` → Voit `test.txt`
- [ ] ✅ **PROJET FONCTIONNE !**

---

## 🎓 Conclusion

Maintenant vous comprenez :

1. **Ce que c'est** : Un système de partage de fichiers sur réseau local
2. **Comment ça marche** : Serveur central + clients qui s'échangent directement
3. **Comment installer** : Même procédure sur chaque PC
4. **Comment configurer** : Trouver l'IP du serveur, la donner aux clients
5. **Comment utiliser** : Commandes simples (`list`, `send`, `received`)
6. **Ce qui a été codé** : 6 modules qui travaillent ensemble

**Prochaine étape** : Interface graphique (boutons au lieu de commandes) !
