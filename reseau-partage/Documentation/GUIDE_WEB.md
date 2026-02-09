# 🌐 Guide d'Utilisation - Interface Web

## 🎯 Vue d'Ensemble

L'interface web permet de **partager des fichiers** entre plusieurs ordinateurs **sans ligne de commande**.

## 📋 Workflow Complet

### Étape 1 : Démarrer le Serveur Central

**Sur UN ordinateur** (ou sur PythonAnywhere), démarrez le serveur :

```bash
# En local
python server/main.py
```

**Sur PythonAnywhere** : Déjà fait ! Le serveur tourne à `https://rachidi.pythonanywhere.com`

---

### Étape 2 : Connecter les Clients (PC)

Chaque PC qui veut partager des fichiers doit :

#### Option A : Via Navigateur (Simple)

1. Ouvrir le navigateur
2. Aller sur l'URL :
   ```
   https://rachidi.pythonanywhere.com/web?name=PC1&port=5001
   ```
   
   **Paramètres URL :**
   - `name=PC1` → Remplacer par le nom de votre PC (PC1, PC2, Rachidi, etc.)
   - `port=5001` → Port unique pour chaque PC (5001, 5002, 5003, etc.)

3. La page se charge et vous êtes **automatiquement connecté** !

**Exemples d'URLs pour différents PC :**

| PC | URL |
|----|-----|
| PC1 | `https://rachidi.pythonanywhere.com/web?name=PC1&port=5001` |
| PC2 | `https://rachidi.pythonanywhere.com/web?name=PC2&port=5002` |
| Rachidi | `https://rachidi.pythonanywhere.com/web?name=Rachidi&port=5003` |
| PC-Bureau | `https://rachidi.pythonanywhere.com/web?name=PC-Bureau&port=5004` |

#### Option B : Laisser Entrer Manuellement

Ouvrir simplement :
```
https://rachidi.pythonanywhere.com/web
```

Une popup demande :
- Nom du PC : `PC1` (par exemple)
- Port : `5001` (par exemple)

---

### Étape 3 : Vérifier la Connexion

Sur l'interface web, vous devez voir :

✅ **En haut à gauche** :
```
🌐 Réseau de Partage P2P v2.0
● Connecté
Nom: PC1
Port: 5001
```

✅ **Section "PCs connectés"** :
- Vous devez voir les **autres PC** connectés
- Exemple : "PC2", "Rachidi", etc.

Si vous ne voyez personne → Les autres PC ne sont pas encore connectés.

---

### Étape 4 : Envoyer un Fichier

#### 📤 Méthode 1 : Drag & Drop (Glisser-Déposer)

1. **Glissez un fichier** depuis votre explorateur
2. **Déposez-le** dans la zone "Envoyer un fichier"
3. Le fichier apparaît avec sa taille
4. **Sélectionnez le destinataire** :
   - Un PC spécifique (ex: PC2)
   - **"Tous les PC"** pour envoyer à tout le monde
5. Cliquez **"Envoyer le fichier"**
6. ✅ Notification de succès !

#### 📤 Méthode 2 : Cliquer pour Sélectionner

1. **Cliquez** sur la zone "📁 Cliquez ou glissez un fichier ici"
2. Une fenêtre s'ouvre → **Choisissez votre fichier**
3. Le fichier apparaît
4. **Sélectionnez le destinataire**
5. Cliquez **"Envoyer le fichier"**

---

### Étape 5 : Recevoir un Fichier

**Automatique !**

Quand quelqu'un vous envoie un fichier :

1. ✅ Notification apparaît : **"Fichier envoyé avec succès"**
2. Le fichier apparaît dans la section **"Fichiers reçus et envoyés"**
3. Badge bleu **"Reçu"** avec icône 📥
4. Indique **"De: NomDuPC"**

Le fichier est stocké dans :
```
storage/VotreNomPC/nom_du_fichier.ext
```

---

## 📱 Interface Web - Guide Visuel

### Zone 1 : Informations de Connexion (Haut)

```
🌐 Réseau de Partage P2P v2.0
┌────────────────────────────────┐
│ ● Connecté | Nom: PC1 | Port: 5001 | Serveur: Détection... │
└────────────────────────────────┘
```

### Zone 2 : PCs Connectés (Gauche)

```
┌─ PCs connectés (2) ────────┐
│                            │
│  PC2                       │
│  192.168.1.10:5002         │
│  [En ligne]                │
│                            │
│  Rachidi                   │
│  192.168.1.15:5003         │
│  [En ligne]                │
│                            │
└────────────────────────────┘
```

### Zone 3 : Envoyer un Fichier (Centre)

```
┌─ Envoyer un fichier ───────┐
│                            │
│      📁                    │
│  Cliquez ou glissez        │
│  un fichier ici            │
│                            │
│  Fichiers >1GB seront      │
│  automatiquement fragmentés│
│                            │
│  Destinataire:             │
│  [▼ Tous les PC (2)]       │
│                            │
│  [Envoyer le fichier]      │
│                            │
└────────────────────────────┘
```

### Zone 4 : Fichiers Reçus/Envoyés (Droite)

```
┌─ Fichiers reçus et envoyés (3) ─┐
│                                 │
│  📥 rapport.pdf                 │
│  2.5 MB • De: PC2               │
│  [Reçu]                         │
│                                 │
│  📤 presentation.pptx           │
│  8.3 MB • À: Rachidi            │
│  [Envoyé]                       │
│                                 │
│  📤 projet.zip                  │
│  125 MB • À: Plusieurs (2 PC)   │
│  [Envoyé]                       │
│                                 │
└─────────────────────────────────┘
```

---

## 🔄 Rafraîchissement Automatique

L'interface se met à jour **automatiquement toutes les 5 secondes** :

- Liste des PC connectés
- Nouveaux fichiers reçus
- État du réseau HA (si activé)

**Pas besoin de recharger la page !**

---

## ⚠️ Fragmentation Automatique

Pour les fichiers **> 1 GB** :

1. Vous voyez un message jaune :
   ```
   ⚠️ Fragmentation activée
   Fichier trop volumineux (1.5 GB)
   Sera découpé en 6 morceaux de 256 MB
   Distribution sur 2 PC avec redondance 2x
   ```

2. Le transfert se fait automatiquement
3. Le destinataire reçoit le fichier **reconstruit**

---

## 🚨 Notifications

### ✅ Notifications de Succès (Vertes)

- **"Connecté au serveur"** → Vous êtes en ligne
- **"Fichier envoyé avec succès"** → Transfert réussi
- **"Fichier téléchargé"** → Réception réussie

### ❌ Notifications d'Erreur (Rouges)

- **"Erreur de connexion au serveur"** → Serveur inaccessible
- **"Veuillez sélectionner un fichier et un destinataire"** → Oubli de sélection
- **"Erreur lors de l'envoi"** → Problème de transfert

### 💡 Correction du Bug des Notifications

✅ **Les anciennes notifications disparaissent automatiquement** après 3 secondes
✅ **Une seule notification visible à la fois** (les anciennes s'effacent)

---

## 🎮 Scénarios d'Usage

### Scénario 1 : Partage entre 2 PC (Simple)

**PC1** :
```
1. Ouvrir : https://rachidi.pythonanywhere.com/web?name=PC1&port=5001
2. Glisser fichier "rapport.pdf"
3. Sélectionner destinataire : PC2
4. Cliquer "Envoyer"
```

**PC2** :
```
1. Ouvrir : https://rachidi.pythonanywhere.com/web?name=PC2&port=5002
2. Attendre quelques secondes
3. Voir "rapport.pdf" apparaître dans "Fichiers reçus"
4. Fichier stocké dans storage/PC2/rapport.pdf
```

---

### Scénario 2 : Partage Multiple (À tous)

**PC1** :
```
1. Ouvrir l'interface web
2. Sélectionner fichier "presentation.pptx"
3. Destinataire : "Tous les PC (3)"
4. Envoyer
```

**Résultat** : PC2, PC3, et Rachidi reçoivent TOUS le fichier.

---

### Scénario 3 : Gros Fichier (Fragmentation)

**Rachidi** :
```
1. Ouvrir l'interface
2. Sélectionner fichier "video.mp4" (1.5 GB)
3. Message jaune apparaît : "⚠️ Fragmentation activée"
4. Envoyer à PC1
```

**En coulisse** :
- Fichier découpé en 6 morceaux de 256 MB
- Distribution automatique sur les PC disponibles
- PC1 reçoit le fichier reconstruit

---

## 🔧 Résolution de Problèmes

### Problème 1 : "Aucun PC connecté"

**Causes** :
- Les autres PC n'ont pas ouvert l'interface web
- Mauvaise connexion réseau

**Solutions** :
1. Vérifier que les autres PC ont ouvert l'URL
2. Attendre 5-10 secondes (rafraîchissement auto)
3. Vérifier que le serveur tourne

---

### Problème 2 : "Erreur de connexion au serveur"

**Causes** :
- Serveur PythonAnywhere arrêté
- URL incorrecte

**Solutions** :
1. Vérifier l'URL : `https://rachidi.pythonanywhere.com/web`
2. Vérifier que le serveur est "Running" sur PythonAnywhere
3. Cliquer "Reload" sur PythonAnywhere

---

### Problème 3 : Fichier non reçu

**Causes** :
- Destinataire déconnecté pendant le transfert
- Fichier trop volumineux (limite 100MB sur plan gratuit)

**Solutions** :
1. Vérifier que le destinataire est "En ligne"
2. Pour gros fichiers, upgrader PythonAnywhere ou utiliser VPS

---

### Problème 4 : Notifications restent affichées

✅ **CORRIGÉ !** 

Les notifications disparaissent maintenant automatiquement après 3 secondes.

Si ça persiste :
```bash
# Mettre à jour le code sur PythonAnywhere
cd ~/Config_R-seau/reseau-partage
git pull origin main
# Puis cliquer "Reload" sur PythonAnywhere
```

---

## 📊 Limites PythonAnywhere (Plan Gratuit)

### ✅ Ce qui fonctionne

- ✅ Interface web
- ✅ Partage de fichiers <100MB total
- ✅ Plusieurs PC connectés
- ✅ Base de données SQLite
- ✅ Notifications
- ✅ Auto-refresh

### ⚠️ Limitations

- ⚠️ Espace disque : 100MB total
- ⚠️ Upload max : ~10-20MB par fichier
- ⚠️ Pas de connexions P2P directes (tout passe par le serveur)
- ⚠️ HA (Haute Disponibilité) non fonctionnel sur plan gratuit
- ⚠️ CPU limité (peut être lent avec plusieurs utilisateurs)

### 💡 Pour Lever ces Limites

**Option 1 : PythonAnywhere Payant** (5$/mois)
- 1GB d'espace
- Fichiers jusqu'à 100MB
- Plus de CPU

**Option 2 : VPS DigitalOcean** (5$/mois)
- Espace illimité
- Fichiers illimités
- HA complet fonctionnel
- Connexions P2P directes

Voir [DEPLOIEMENT.md](DEPLOIEMENT.md) pour migrer.

---

## 🎯 Résumé Rapide

### Pour Partager un Fichier :

1. **Ouvrir** : `https://rachidi.pythonanywhere.com/web?name=VOTRE_NOM&port=5001`
2. **Glisser** votre fichier
3. **Choisir** le destinataire
4. **Cliquer** "Envoyer"
5. ✅ Fait !

### Pour Recevoir un Fichier :

1. **Ouvrir** l'interface web
2. **Attendre** (rafraîchissement auto toutes les 5s)
3. Le fichier apparaît dans "Fichiers reçus"
4. ✅ Disponible dans `storage/VotreNom/`

---

## 📞 Aide

Si vous avez des questions :
1. Consultez les logs sur PythonAnywhere (Error log)
2. Vérifiez que tous les PC ont des ports différents
3. Assurez-vous que le serveur est "Running"

**Astuce** : Mettez l'URL en favori pour y accéder rapidement !

---

**Bon partage !** 🚀
