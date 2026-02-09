# Architecture Serveur/Client - Réseau P2P

## Vue d'ensemble

Ce système utilise une architecture **hybride** : 
- **1 serveur central** : annuaire et coordination
- **N clients** : partage de fichiers peer-to-peer

---

## Le Serveur Central

### Qu'est-ce que le serveur ?

Le serveur est une application Flask qui tourne **sur UN SEUL ordinateur** (typiquement déployé sur PythonAnywhere ou un PC dédié).

**Fichier principal :** [server/main.py](../server/main.py)

### Rôle du serveur

Le serveur centralise UNIQUEMENT :
- **Annuaire des PC** : qui est connecté, adresses IP, ports
- **Base de données** : métadonnées des fichiers, permissions, historique
- **Authentification** : vérification des mots de passe, tokens de session
- **Interface web** : page de connexion et interface de gestion

### Ce que le serveur NE fait PAS

Le serveur **ne stocke PAS** et **ne transfère PAS** les fichiers entre clients. Les fichiers sont copiés localement dans le dossier `storage/` uniquement pour l'interface web.

---

## Les Clients (Peers)

### Qu'est-ce qu'un client ?

Un client = **n'importe quel ordinateur** qui se connecte au réseau via l'interface web.

**Exemples :** PC1, PC2, Mon-Ordinateur, Rachidi, etc.

### Comment devient-on client ?

Simplement en accédant à l'interface web :

```
1. Ouvrir navigateur
2. Aller sur https://rachidi.pythonanywhere.com (ou l'URL du serveur)
3. Entrer nom + mot de passe
4. → Connecté en tant que client !
```

**Aucune installation requise** : tout passe par le navigateur.

---

## Architecture Détaillée

```
┌─────────────────────────────────────────┐
│   SERVEUR CENTRAL (PythonAnywhere)      │
│                                          │
│   - Flask + SQLite                      │
│   - Annuaire (peers table)              │
│   - Métadonnées fichiers (files table)  │
│   - Permissions (transfers table)       │
│   - Interface web                       │
│   - Port: 443 (HTTPS)                   │
└─────────────────┬───────────────────────┘
                  │
                  │ Internet
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  CLIENT │  │  CLIENT │  │  CLIENT │
│   PC1   │  │   PC2   │  │   PC3   │
│         │  │         │  │         │
│ Browser │  │ Browser │  │ Browser │
│ Session │  │ Session │  │ Session │
└─────────┘  └─────────┘  └─────────┘
```

---

## Fonctionnement : Qui fait quoi ?

### 1. Connexion d'un client

```
CLIENT (PC1)                    SERVEUR
    │                              │
    │  POST /api/auth/login        │
    │  {name: "PC1", password}     │
    ├─────────────────────────────>│
    │                              │
    │                     Vérifier mot de passe
    │                     Créer token session
    │                     Enregistrer dans peers
    │                              │
    │  200 OK {token, port}        │
    │<─────────────────────────────┤
    │                              │
    │  Stocker token localStorage  │
    │  Rediriger vers interface    │
```

**Résultat :** PC1 est maintenant dans la table `peers` avec `status='online'`

---

### 2. Heartbeat (signal de vie)

Toutes les **2 minutes**, chaque client envoie un heartbeat :

```
CLIENT (PC1)                    SERVEUR
    │                              │
    │  POST /api/heartbeat         │
    │  {name: "PC1"}               │
    ├─────────────────────────────>│
    │                              │
    │              UPDATE peers
    │              SET last_seen = NOW()
    │              WHERE name = "PC1"
    │                              │
    │  200 OK                      │
    │<─────────────────────────────┤
```

**Fonction :** [web/static/app.js](../web/static/app.js) - `sendHeartbeat()`

**Conséquence :**
- Si heartbeat reçu : `status = 'online'`
- Si >5 min sans heartbeat : `status = 'offline'` (task planifiée)
- Si >10h sans heartbeat : peer supprimé de la DB

---

### 3. Envoi de fichier

```
CLIENT PC1                      SERVEUR                   BASE DE DONNÉES
    │                              │                              │
    │  Sélectionne fichier.pdf     │                              │
    │  Choisit destinataire: PC2   │                              │
    │                              │                              │
    │  POST /api/file/upload       │                              │
    │  FormData(file, recipients)  │                              │
    ├─────────────────────────────>│                              │
    │                              │                              │
    │                      Sauvegarder dans                       │
    │                      storage/PC2/fichier.pdf                │
    │                              │                              │
    │                              │  INSERT INTO files           │
    │                              │  (filename, owner="PC1")     │
    │                              ├─────────────────────────────>│
    │                              │                              │
    │                              │  INSERT INTO transfers       │
    │                              │  (from="PC1", to="PC2")      │
    │                              ├─────────────────────────────>│
    │                              │                              │
    │  200 OK {file_id}            │                              │
    │<─────────────────────────────┤                              │
```

**Important :** 
- Le fichier est copié dans `storage/PC2/` (sur le serveur)
- Un enregistrement `transfers` est créé avec `to_peer='PC2'`
- **PC2 peut maintenant le télécharger** via l'interface web

---

### 4. Consultation des fichiers reçus

```
CLIENT PC2                      SERVEUR
    │                              │
    │  GET /api/files/received/PC2 │
    ├─────────────────────────────>│
    │                              │
    │              SELECT files WHERE
    │              to_peer = "PC2" AND
    │              status = "success"
    │                              │
    │  200 OK [fichier.pdf]        │
    │<─────────────────────────────┤
    │                              │
    │  Afficher dans l'interface   │
```

**Résultat :** PC2 voit uniquement les fichiers qui lui ont été envoyés.

---

### 5. Téléchargement de fichier

```
CLIENT PC2                      SERVEUR
    │                              │
    │  Clic "Télécharger"          │
    │  GET /api/file/download/     │
    │      PC2/fichier.pdf         │
    ├─────────────────────────────>│
    │                              │
    │              Vérifier :
    │              1. Fichier existe ?
    │              2. to_peer = "PC2" ?
    │                              │
    │              ✓ OK             │
    │                              │
    │  Flux fichier (streaming)    │
    │<─────────────────────────────┤
    │                              │
    │  Enregistrer sur disque      │
```

**Sécurité :** PC3 ne peut PAS télécharger `fichier.pdf` car il n'y a pas d'enregistrement `transfers` pour lui.

---

## Récapitulatif : Serveur vs Client

| Aspect | Serveur | Client (PC1, PC2...) |
|--------|---------|---------------------|
| **Nombre** | 1 seul | Autant que nécessaire |
| **Hébergement** | PythonAnywhere, VPS, PC fixe | N'importe quel PC avec navigateur |
| **Installation** | Code Flask déployé | Aucune (via navigateur) |
| **Accès** | URL fixe (rachidi.pythonanywhere.com) | Se connecte via URL |
| **Rôle** | Annuaire + métadonnées | Envoyer/recevoir fichiers |
| **Base de données** | Oui (SQLite) | Non |
| **Stockage fichiers** | Oui (storage/) | Non (télécharge depuis serveur) |
| **Authentification** | Génère tokens | Utilise tokens |

---

## Qui est "serveur" et qui est "client" ?

### Le serveur

**UN SEUL ordinateur** où vous avez déployé l'application Flask.

**Dans votre cas :**
- **Hébergement :** PythonAnywhere (https://rachidi.pythonanywhere.com)
- **Code :** `/home/rachidi/Base_de_données/Config_R-seau/reseau-partage/`
- **Processus :** Application Flask WSGI

### Les clients

**TOUS les utilisateurs** qui se connectent via l'interface web, peu importe leur ordinateur.

**Exemples dans votre réseau :**
- `PC1` : votre laptop
- `PC2` : un autre ordinateur
- `Rachidi` : votre PC principal
- etc.

**Caractéristique :** Chaque client a un nom unique dans la table `peers`.

---

## FAQ

### Q1 : Puis-je avoir plusieurs serveurs ?

**Non.** Un seul serveur central gère tout le réseau. C'est le principe de l'architecture.

**Alternative :** Vous pouvez configurer un **serveur de backup** (voir [ARCHITECTURE.md](ARCHITECTURE.md) pour la Haute Disponibilité), mais il sera en standby, pas actif simultanément.

---

### Q2 : Un client peut-il devenir serveur ?

**Non.** Les rôles sont fixes :
- Serveur = machine où tourne Flask
- Client = toute machine qui accède à l'interface web

---

### Q3 : Combien de clients peuvent se connecter ?

**Limites techniques :**
- PythonAnywhere Free : ~1-5 clients simultanés (limites CPU/RAM)
- PythonAnywhere Paid : dizaines de clients
- Serveur dédié : centaines de clients

**Limite pratique :** Dépend de votre usage (taille fichiers, fréquence transferts).

---

### Q4 : Si le serveur tombe, que se passe-t-il ?

**Conséquences :**
- ✗ Plus d'authentification possible
- ✗ Plus de nouveaux transferts
- ✗ Interface web inaccessible
- ✓ Fichiers déjà téléchargés restent sur chaque client

**Solution :** Redémarrer le serveur ou basculer sur un backup (HA).

---

### Q5 : Les fichiers transitent-ils par le serveur ?

**Oui**, dans cette architecture hybride :
1. PC1 upload fichier vers serveur
2. Serveur stocke dans `storage/PC2/`
3. PC2 download depuis serveur

**Alternative P2P pur :** Transfert direct PC1 → PC2, mais nécessite :
- Configuration routeur (port forwarding)
- IP publique pour chaque client
- Complexité accrue

---

## Schéma Résumé

```
┌────────────────────────────────────────────────────┐
│              SERVEUR CENTRAL                       │
│                                                    │
│  • Authentification (login, tokens)                │
│  • Annuaire des PC (peers table)                   │
│  • Métadonnées fichiers (files, transfers)         │
│  • Stockage temporaire (storage/)                  │
│  • Interface web (Flask)                           │
│                                                    │
│  UNIQUE dans tout le réseau                        │
└────────────────────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
┌────────────────┐          ┌────────────────┐
│  CLIENT PC1    │          │  CLIENT PC2    │
│                │          │                │
│  • Navigateur  │          │  • Navigateur  │
│  • Token       │          │  • Token       │
│  • Envoie      │──────────│  • Reçoit      │
│    fichier     │ via srv  │    fichier     │
└────────────────┘          └────────────────┘
```

---

## Commandes utiles

### Démarrer le serveur (local)

```bash
cd /home/rachidi/Base_de_données/Config_R-seau/reseau-partage
python server/main.py
```

### Vérifier les clients connectés

Ouvrir interface web → Section "PC Connectés"

Ou via API :
```bash
curl https://rachidi.pythonanywhere.com/api/peers
```

### Voir la base de données

```bash
sqlite3 server/peers.db
SELECT * FROM peers;
SELECT * FROM transfers;
```

---

## Conclusion

**Architecture hybride :**
- **1 serveur** = cerveau du réseau (annuaire, DB, interface)
- **N clients** = participants qui envoient/reçoivent fichiers

**Avantages :**
- ✓ Simple : pas de config réseau client
- ✓ Sécurisé : authentification centralisée
- ✓ Accessible : via navigateur uniquement

**Inconvénient :**
- Dépendance au serveur central (SPOF = Single Point of Failure)
- Solution : Haute Disponibilité (HA) avec backup

**Votre déploiement actuel :**
- Serveur : PythonAnywhere (https://rachidi.pythonanywhere.com)
- Clients : PC1, PC2, PC3, Rachidi... (tous via navigateur)
