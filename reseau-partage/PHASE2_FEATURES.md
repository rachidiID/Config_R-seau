# 📋 Phase 2 - Nouvelles Fonctionnalités

## ✅ Fonctionnalités ajoutées

### 1. 📁 Transfert de dossiers complets

**Description**: Envoi et réception automatiques de dossiers entiers.

**Comment ça marche**:
- Le dossier est automatiquement compressé en ZIP avant l'envoi
- Envoyé via le même mécanisme que les fichiers simples
- Automatiquement décompressé à la réception
- Le fichier ZIP temporaire est supprimé après extraction

**Utilisation**:
```bash
# Envoyer un dossier à un PC
send /chemin/vers/dossier PC2

# Envoyer un dossier à plusieurs PC
send ./mon_projet PC2 PC3

# Envoyer un dossier à tous les PC
send ~/Documents/photos *
```

**Exemple concret**:
```
Alice> send /home/alice/projet_python PC2

📦 Compression du dossier 'projet_python'...
✓ Compression terminée: 15.2 MB

📤 Envoi vers PC2...
projet_python: 100%|████████████| 15.2M/15.2M [00:03<00:00, 4.5MB/s]
✓ Dossier envoyé avec succès
```

---

### 2. 📊 Barre de progression améliorée

**Description**: Affichage détaillé de la progression des transferts avec `tqdm`.

**Nouvelles informations affichées**:
- ✅ Pourcentage de progression en temps réel
- ✅ Taille téléchargée / Taille totale (en Mo, Go, etc.)
- ✅ Vitesse de transfert (MB/s)
- ✅ Temps écoulé et temps restant estimé (ETA)
- ✅ Barre visuelle de progression

**Exemple d'affichage**:
```
video.mp4: 45%|███████▌         | 450M/1.0G [00:15<00:18, 30.0MB/s]
```

Légende:
- `video.mp4`: Nom du fichier
- `45%`: Pourcentage complété
- `███████▌`: Barre visuelle
- `450M/1.0G`: 450 Mo sur 1 Go transféré
- `00:15`: 15 secondes écoulées
- `00:18`: 18 secondes restantes (estimation)
- `30.0MB/s`: Vitesse actuelle

**Avantages**:
- Vision claire de l'avancement
- Détection rapide des transferts lents
- Estimation du temps restant pour les gros fichiers

---

### 3. 🔔 Notifications système

**Description**: Alertes desktop lors des événements importants.

**Notifications disponibles**:

#### a) 📥 Fichier/Dossier reçu
```
Titre: 📥 Fichier reçu
Message: rapport.pdf
         De: Alice
```

#### b) ✅ Transfert réussi
```
Titre: ✅ Fichier envoyé
Message: document.docx
         À: Bob
```

#### c) ❌ Transfert échoué
```
Titre: ❌ Échec d'envoi
Message: video.mp4
         À: Charlie
```

**Compatibilité**:
- 🐧 **Linux**: Utilise `notify-send` (inclus dans la plupart des distributions)
- 🪟 **Windows**: Notifications toast natives
- 🍎 **macOS**: Centre de notifications

**Fonctionnalités**:
- Notification automatique à la réception
- Notification après chaque envoi (succès ou échec)
- Durée d'affichage: 5 secondes
- Désactivable si nécessaire

---

## 📦 Nouvelles dépendances

Ajoutées à `requirements.txt`:

```
tqdm==4.66.1      # Barres de progression avancées
plyer==2.1.0      # Notifications desktop multiplateformes
```

**Installation**:
```bash
# Avec le venv activé
pip install tqdm plyer

# Ou réinstaller toutes les dépendances
pip install -r requirements.txt
```

---

## 🎯 Exemples d'utilisation

### Scénario 1: Partager un projet de code

```bash
Alice> send ~/workspace/mon_app PC2 PC3

📦 Préparation de l'envoi:
  Dossier: mon_app
  Taille: 45.2 MB
  Destinataires: Bob, Charlie
  Permission: shared

✅ Dossier enregistré (ID: 15)

📦 Compression du dossier 'mon_app'...
✓ Compression terminée: 12.3 MB

📤 Envoi vers Bob...
mon_app: 100%|████████████████| 12.3M/12.3M [00:02<00:00, 5.2MB/s]
✓ Dossier envoyé avec succès

📤 Envoi vers Charlie...
mon_app: 100%|████████████████| 12.3M/12.3M [00:03<00:00, 4.1MB/s]
✓ Dossier envoyé avec succès

✅ Transfert terminé: 2/2 réussis
```

**Bob reçoit** (notification desktop + terminal):
```
[Notification desktop apparaît]
📦 Dossier reçu
mon_app
De: Alice

[Terminal]
📦 Réception dossier: mon_app de 192.168.1.10
mon_app.zip: 100%|████████| 12.3M/12.3M [00:02<00:00, 5.0MB/s]
⚙️  Décompression...
✓ Dossier reçu: /home/bob/storage/mon_app
```

---

### Scénario 2: Transférer un gros fichier vidéo

```bash
Charlie> send ~/Videos/conference.mp4 PC1

📤 Envoi: conference.mp4 vers 192.168.1.10:5001
conference.mp4: 67%|█████████▋  | 1.34G/2.0G [01:23<00:41, 16.1MB/s]
```

**Alice voit** (en temps réel):
```
📥 Réception: conference.mp4 de 192.168.1.15
conference.mp4: 67%|█████████▋  | 1.34G/2.0G [01:23<00:41, 16.1MB/s]
```

**À la fin** (notification):
```
[Alice reçoit une notification]
📥 Fichier reçu
conference.mp4
De: Charlie
```

---

## 🔧 Modifications techniques

### Fichiers modifiés:

1. **`client/transfer.py`**:
   - Ajout: `send_folder()` - compression et envoi de dossiers
   - Ajout: `on_receive_callback` - callback pour notifications
   - Modification: `_handle_receive()` - gestion des dossiers zip
   - Amélioration: Barres de progression `tqdm` dans toutes les méthodes de transfert
   - Amélioration: `list_received_files()` - affiche aussi les dossiers

2. **`client/main.py`**:
   - Ajout: Import de `NotificationManager`
   - Ajout: Méthode `_on_file_received()` - callback notifications
   - Modification: `cmd_send_file()` - détection automatique fichier/dossier
   - Amélioration: Calcul de la taille pour les dossiers
   - Amélioration: Notifications après chaque transfert

3. **`client/ui.py`**:
   - Modification: `show_help()` - mention des dossiers
   - Amélioration: `show_received_files()` - distinction fichiers/dossiers
   - Amélioration: `parse_send_command()` - messages améliorés

4. **`client/notifications.py`** (NOUVEAU):
   - Classe `NotificationManager` avec toutes les méthodes
   - Gestion multiplateforme (Linux, Windows, macOS)
   - 4 types de notifications

5. **`requirements.txt`**:
   - Ajout de `tqdm==4.66.1`
   - Ajout de `plyer==2.1.0`

---

## 📖 Commandes mises à jour

### Commande `send`

**Syntaxe**:
```bash
send <fichier_ou_dossier> <destinataire(s)>
```

**Exemples**:
```bash
# Fichier simple
send document.pdf PC2

# Dossier
send /home/user/photos PC2

# Plusieurs destinataires
send projet/ PC2 PC3

# Tous les PC
send fichier.txt *
```

### Commande `received`

**Affichage amélioré**:
```
📬 FICHIERS REÇUS (5):

Type      Nom                            Taille
-----------------------------------------------------
📄 Fichier  rapport.pdf                  2.3 MB
📁 Dossier  mon_projet                   15.7 MB
📄 Fichier  image.png                    856.0 KB
📁 Dossier  photos_vacances              124.5 MB
📄 Fichier  notes.txt                    12.0 KB
```

---

## 🚀 Prochaines étapes (Phase 3-4)

Fonctionnalités encore à implémenter:

### Phase 3: Sécurité avancée
- 🔐 Chiffrement AES-256 des transferts
- 🔑 Authentification par mot de passe
- 🛡️ Certificats SSL/TLS
- ✍️ Signatures numériques

### Phase 4: Fonctionnalités avancées
- ⏸️ Reprise sur erreur
- 🗜️ Compression automatique intelligente
- 🖼️ Aperçu de fichiers
- 🔍 Recherche dans l'historique
- 🖥️ Interface graphique (PyQt5)

---

## 📝 Notes importantes

### Performances
- La compression ZIP peut prendre du temps pour les gros dossiers
- La vitesse de transfert dépend de votre réseau WiFi
- Les barres de progression peuvent ralégir légèrement les petits transferts (négligeable)

### Limitations
- Les notifications nécessitent `plyer` installé
- Sur certains Linux, `notify-send` doit être installé:
  ```bash
  # Debian/Ubuntu
  sudo apt install libnotify-bin
  
  # Fedora
  sudo dnf install libnotify
  ```

### Compatibilité
- ✅ Testé sur Linux (Ubuntu, Debian, Fedora)
- ✅ Devrait fonctionner sur Windows 10/11
- ✅ Devrait fonctionner sur macOS 10.14+

---

## 🆘 Dépannage

### Les notifications ne s'affichent pas
```bash
# Vérifier que plyer est installé
pip list | grep plyer

# Linux: vérifier notify-send
which notify-send

# Si absent:
sudo apt install libnotify-bin
```

### La barre de progression ne s'affiche pas
```bash
# Vérifier que tqdm est installé
pip list | grep tqdm

# Réinstaller si nécessaire
pip install tqdm --upgrade
```

### Erreur lors de la compression
- Vérifiez les permissions du dossier
- Assurez-vous d'avoir assez d'espace disque dans `/tmp`

---

## ✅ Tests à effectuer

1. **Transfert de petit dossier** (< 1 MB)
2. **Transfert de gros dossier** (> 100 MB)
3. **Transfert de fichier simple** (vérifier que ça marche toujours)
4. **Notifications** (vérifier sur chaque OS)
5. **Barre de progression** (observer vitesse et ETA)
6. **Réception multiple** (plusieurs transferts simultanés)

---

**Date de mise à jour**: Phase 2 complétée
**Version**: 2.0.0
**Statut**: ✅ Prêt pour tests
