#  Guide Visuel - Scénarios d'Utilisation Réels

##  Scénario 1 : Partage de Photos de Vacances

### Situation
Alice revient de vacances avec 50 photos. Elle veut :
- Envoyer TOUTES les photos à Bob
- Charlie n'en veut pas

### Sur le PC d'Alice

```bash
# 1. Vérifier que Bob est connecté
Alice> list

 PC CONNECTÉS (2):
Nom             Adresse IP           Port       Statut
-------------------------------------------------------
Bob             192.168.1.20         5001       🟢 En ligne
Charlie         192.168.1.30         5001       🟢 En ligne

# 2. Envoyer toutes les photos (une par une)
Alice> send /home/alice/Vacances/photo1.jpg Bob
 Transfert terminé: 1/1 réussis

Alice> send /home/alice/Vacances/photo2.jpg Bob
 Transfert terminé: 1/1 réussis

# ... (répéter pour les 50 photos)
```

### Résultat
-  Bob reçoit les 50 photos dans `storage/Bob/`
-  Charlie ne voit rien (c'était privé)

---

##  Scénario 2 : Projet d'Équipe

### Situation
Alice, Bob et Charlie travaillent ensemble. Alice a créé le rapport final et veut que Bob ET Charlie le relisent.

### Sur le PC d'Alice

```bash
Alice> send /home/alice/Documents/Rapport_Final.pdf Bob Charlie

📦 Préparation de l'envoi:
  Fichier: Rapport_Final.pdf
  Taille: 1.2 MB
  Destinataires: Bob, Charlie
  Permission: shared

 Fichier enregistré (ID: 5)

📤 Envoi vers Bob...
Progression: 100.0%
✓ Fichier envoyé avec succès

📤 Envoi vers Charlie...
Progression: 100.0%
✓ Fichier envoyé avec succès

 Transfert terminé: 2/2 réussis
```

### Sur le PC de Bob (automatiquement)

```bash
Bob> 
📥 Réception: Rapport_Final.pdf (1.2 MB) de 192.168.1.10
Progression: 100.0%
✓ Fichier reçu: storage/Bob/Rapport_Final.pdf

Bob> received

 FICHIERS REÇUS (1):
Rapport_Final.pdf              1.2 MB
```

### Sur le PC de Charlie (automatiquement)

```bash
Charlie> 
📥 Réception: Rapport_Final.pdf (1.2 MB) de 192.168.1.10
✓ Fichier reçu: storage/Charlie/Rapport_Final.pdf
```

### Résultat
-  Bob a le rapport
-  Charlie a le rapport
-  Ils peuvent tous les deux le relire en même temps

---

##  Scénario 3 : Annonce Générale

### Situation
Alice veut informer TOUT LE MONDE qu'il y a une réunion demain.

### Étape 1 : Créer le Message

```bash
# Sur le PC d'Alice, dans un autre terminal
echo " RÉUNION IMPORTANTE
Date : Demain 14h
Lieu : Salle de réunion
Ordre du jour : Présentation du projet" > /tmp/annonce.txt
```

### Étape 2 : Envoyer à Tous

```bash
Alice> send /tmp/annonce.txt *

 Envoi public à 2 PC

📦 Préparation de l'envoi:
  Fichier: annonce.txt
  Taille: 124 B
  Destinataires: Bob, Charlie
  Permission: public

 Fichier enregistré (ID: 6)

📤 Envoi vers Bob...
✓ Fichier envoyé avec succès

📤 Envoi vers Charlie...
✓ Fichier envoyé avec succès

 Transfert terminé: 2/2 réussis
```

### Sur TOUS les PC (Bob, Charlie, et même David s'il se connecte)

```bash
📥 Réception: annonce.txt (124 B) de 192.168.1.10
✓ Fichier reçu
```

### Résultat
-  Tout le monde a reçu l'annonce
-  Si un nouveau PC (David) se connecte, il peut aussi la recevoir (fichier public)

---

##  Scénario 4 : Bob Répond à Alice

### Situation
Bob a relu le rapport et veut envoyer ses corrections à Alice.

### Sur le PC de Bob

```bash
# 1. Voir qui est connecté
Bob> list

 PC CONNECTÉS (2):
Nom             Adresse IP           Port       Statut
-------------------------------------------------------
Alice           192.168.1.10         5001       🟢 En ligne
Charlie         192.168.1.30         5001       🟢 En ligne

# 2. Envoyer les corrections (UNIQUEMENT à Alice, pas Charlie)
Bob> send /home/bob/Documents/Corrections.pdf Alice

📦 Préparation de l'envoi:
  Fichier: Corrections.pdf
  Taille: 320 KB
  Destinataires: Alice
  Permission: private

 Transfert terminé: 1/1 réussis
```

### Sur le PC d'Alice (automatiquement)

```bash
Alice> 
📥 Réception: Corrections.pdf (320 KB) de 192.168.1.20
✓ Fichier reçu: storage/Alice/Corrections.pdf

Alice> received

 FICHIERS REÇUS (1):
Corrections.pdf                320 KB
```

### Résultat
-  Alice reçoit les corrections de Bob
-  Charlie ne les voit pas (normal, c'est entre Alice et Bob)

---

##  Scénario 5 : Partage de Code Source

### Situation
Charlie a créé un script Python que Bob et Alice doivent tester.

### Sur le PC de Charlie

```bash
# 1. Créer le script
# (Dans un autre terminal)
cat > /tmp/script.py << 'EOF'
#!/usr/bin/env python3
print("Hello from Charlie!")

def calcul(a, b):
    return a + b

print(calcul(5, 3))
EOF

# 2. Envoyer à Alice et Bob
Charlie> send /tmp/script.py Alice Bob

📦 Préparation de l'envoi:
  Fichier: script.py
  Taille: 142 B
  Destinataires: Alice, Bob
  Permission: shared

 Transfert terminé: 2/2 réussis
```

### Sur le PC d'Alice

```bash
Alice> 
📥 Réception: script.py (142 B) de 192.168.1.30
✓ Fichier reçu

# Tester le script
Alice> quit
$ python3 storage/Alice/script.py
Hello from Charlie!
8
```

### Sur le PC de Bob

```bash
Bob> 
📥 Réception: script.py (142 B) de 192.168.1.30
✓ Fichier reçu

# Tester le script
Bob> quit
$ python3 storage/Bob/script.py
Hello from Charlie!
8
```

### Résultat
-  Alice et Bob ont tous les deux le script
-  Ils peuvent le tester indépendamment

---

##  Scénario 6 : Gros Fichier Vidéo

### Situation
Alice a une vidéo de 500 MB qu'elle veut envoyer à Bob.

### Sur le PC d'Alice

```bash
Alice> send /home/alice/Vidéos/presentation.mp4 Bob

📦 Préparation de l'envoi:
  Fichier: presentation.mp4
  Taille: 524.3 MB
  Destinataires: Bob
  Permission: private

 Fichier enregistré (ID: 10)

📤 Envoi vers Bob...
Progression: 12.5%
Progression: 25.0%
Progression: 37.5%
Progression: 50.0%
Progression: 62.5%
Progression: 75.0%
Progression: 87.5%
Progression: 100.0%
✓ Fichier envoyé avec succès

 Transfert terminé: 1/1 réussis

Temps écoulé: 45 secondes
Vitesse moyenne: 11.6 MB/s
```

### Sur le PC de Bob

```bash
Bob> 
📥 Réception: presentation.mp4 (524.3 MB) de 192.168.1.10
Progression: 100.0%
✓ Fichier reçu: storage/Bob/presentation.mp4
  Checksum: f3a2b1c4...

# Vérifier que le fichier n'est pas corrompu
Bob> quit
$ ls -lh storage/Bob/presentation.mp4
-rw-r--r-- 1 bob bob 525M déc 8 15:30 storage/Bob/presentation.mp4

$ vlc storage/Bob/presentation.mp4
# La vidéo se lit parfaitement !
```

### Résultat
-  Vidéo de 500 MB transférée en 45 secondes (réseau local rapide)
-  Intégrité vérifiée par checksum
-  Bien plus rapide qu'avec Internet (qui prendrait 20+ minutes)

---

##  Scénario 7 : Vérifier l'Historique

### Situation
Alice veut savoir ce qu'elle a envoyé aujourd'hui.

### Sur le PC du Serveur

```bash
# Aller dans le serveur
$ cd ~/Documents/reseau-partage

# Activer l'environnement
$ source venv/bin/activate

# Interroger la base de données
$ sqlite3 server/network.db

sqlite> -- Voir tous les transferts
sqlite> SELECT * FROM transfers;

id|file_id|from_peer|to_peer|status|transferred_at
1|1|Alice|Bob|success|2025-12-08T14:15:23
2|2|Alice|Bob|success|2025-12-08T14:20:45
3|3|Alice|Charlie|success|2025-12-08T14:25:10
4|4|Alice|Bob|success|2025-12-08T14:30:15
5|4|Alice|Charlie|success|2025-12-08T14:30:16
6|5|Bob|Alice|success|2025-12-08T14:35:20

sqlite> -- Voir seulement les envois d'Alice
sqlite> SELECT * FROM transfers WHERE from_peer = 'Alice';

sqlite> -- Voir combien de fichiers Alice a envoyés
sqlite> SELECT COUNT(*) FROM transfers WHERE from_peer = 'Alice';
5

sqlite> .quit
```

### Résultat
-  Historique complet de tous les transferts
-  Possibilité de filtrer par expéditeur, destinataire, date
-  Statistiques (nombre de fichiers envoyés, reçus)

---

##  Scénario 8 : Nouvelle Personne Arrive (David)

### Situation
David vient d'arriver et veut rejoindre le réseau.

### Sur le PC de David

```bash
# 1. Installer le projet (même procédure que les autres)
$ cd ~/Documents
$ git clone https://github.com/rachidiID/neo4j-graphes-amitie.git
$ cd neo4j-graphes-amitie/reseau-partage
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# 2. Demander à Alice l'IP du serveur
# Alice : "C'est 192.168.1.10"

# 3. Se connecter
$ python client/main.py --name David --port 5001 --server http://192.168.1.10:5000

==================================================
🌐  RÉSEAU DE PARTAGE P2P - David
==================================================
✓ Enregistré sur le serveur en tant que: David
  IP: 192.168.1.40:5001

✓ Serveur de réception démarré sur le port 5001

 Client prêt ! Tapez 'help' pour voir les commandes.

David> list

 PC CONNECTÉS (3):
Nom             Adresse IP           Port       Statut
-------------------------------------------------------
Alice           192.168.1.10         5001       🟢 En ligne
Bob             192.168.1.20         5001       🟢 En ligne
Charlie         192.168.1.30         5001       🟢 En ligne
```

### Résultat
-  David est connecté en 2 minutes
-  Il peut envoyer et recevoir des fichiers immédiatement
-  Les autres voient David dans leur `list`

---

##  Tableau Récapitulatif des Scénarios

| Scénario | Commande | Permission | Qui Reçoit ? |
|----------|----------|------------|--------------|
| Photo privée | `send photo.jpg Bob` | private | Bob uniquement |
| Rapport équipe | `send rapport.pdf Bob Charlie` | shared | Bob et Charlie |
| Annonce générale | `send annonce.txt *` | public | Tout le monde |
| Correction privée | `send corrections.pdf Alice` | private | Alice uniquement |
| Code partagé | `send script.py Alice Bob` | shared | Alice et Bob |
| Grosse vidéo | `send video.mp4 Bob` | private | Bob (avec progression) |

---

##  Points Clés à Retenir

### 1. Permission = Qui Voit Quoi

```
UN destinataire  → send fichier.txt Bob      → PRIVÉ
PLUSIEURS        → send fichier.txt Bob Charlie → PARTAGÉ
TOUS (*)         → send fichier.txt *        → PUBLIC
```

### 2. Les Fichiers Vont dans `storage/NomDuPC/`

```
Alice envoie photo.jpg à Bob
→ Bob le trouve dans: storage/Bob/photo.jpg

Charlie envoie script.py à Alice
→ Alice le trouve dans: storage/Alice/script.py
```

### 3. Chaque PC Peut Envoyer et Recevoir

```
Alice peut envoyer à Bob
Bob peut envoyer à Alice
Charlie peut envoyer à Alice et Bob
Etc.
```

### 4. Le Serveur Doit Toujours Tourner

```
Si le serveur s'arrête:
  → Plus personne ne peut s'enregistrer
  → Plus personne ne peut envoyer de nouveaux fichiers
  → Mais les transferts en cours continuent (P2P direct)
```

---

##  Prochaines Fonctionnalités (À Implémenter)

1. **Transfert de Dossiers Complets**
   ```bash
   Alice> send /home/alice/Photos/ Bob
   → Envoie tout le dossier avec ses sous-dossiers
   ```

2. **Reprise sur Erreur**
   ```bash
   # Si la connexion coupe pendant un gros transfert
   Alice> resume fichier.mp4 Bob
   → Reprend là où ça s'était arrêté
   ```

3. **Interface Graphique**
   ```
   [Fenêtre avec boutons]
   - Glisser-déposer un fichier
   - Cocher les destinataires
   - Cliquer "Envoyer"
   ```

4. **Compression Automatique**
   ```bash
   Alice> send gros_dossier/ Bob --compress
   → Compresse avant d'envoyer (plus rapide)
   ```

5. **Chiffrement**
   ```bash
   Alice> send secret.txt Bob --encrypt
   → Chiffré, personne ne peut lire même si intercepté
   ```

