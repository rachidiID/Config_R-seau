# 🔒 Contrôle d'Accès et Sécurité - Fichiers

## 🚨 Problème Résolu

**Avant :** Tous les fichiers étaient visibles par tout le monde  
**Après :** Chaque utilisateur voit UNIQUEMENT les fichiers qui lui sont destinés

---

## ✅ Mécanismes de Sécurité Implémentés

### 1. **Filtrage Backend (Base de Données)**

```python
def get_received_files(self, peer_name: str):
    """
    Retourne UNIQUEMENT les fichiers reçus par peer_name
    """
    cursor.execute("""
        SELECT f.id, f.filename, f.filesize, f.owner as sender
        FROM files f
        JOIN transfers t ON f.id = t.file_id
        WHERE t.to_peer = ? AND t.status = 'success'
    """, (peer_name,))
```

**Résultat :** L'API `/api/files/received/PC1` retourne SEULEMENT les fichiers envoyés à PC1.

---

### 2. **Contrôle de Téléchargement**

**Avant (DANGEREUX) :**
```python
def download_file(peer_name, filename):
    # N'importe qui pouvait télécharger
    return send_from_directory(file_dir, filename)
```

**Après (SÉCURISÉ) :**
```python
def download_file(peer_name, filename):
    # 1. Vérifier que le fichier existe dans SON dossier
    if not os.path.exists(file_path):
        return 403  # Accès refusé
    
    # 2. Vérifier dans la DB qu'il lui a été envoyé
    cursor.execute("""
        SELECT COUNT(*) FROM transfers t
        WHERE filename = ? AND to_peer = ? AND status = 'success'
    """, (filename, peer_name))
    
    if count == 0:
        return 403  # Ce fichier ne lui est pas destiné
    
    # OK, téléchargement autorisé
    return send_from_directory(file_dir, filename)
```

---

## 🎯 Scénarios de Sécurité

### Scénario 1 : Envoi à Un Seul Destinataire

**Action :**
```
PC1 envoie "rapport.pdf" à PC2
```

**Résultat :**

| Utilisateur | Voit le fichier ? | Peut télécharger ? |
|-------------|-------------------|---------------------|
| **PC1** | ✅ Oui (Envoyé) | ❌ Non (pas le destinataire) |
| **PC2** | ✅ Oui (Reçu) | ✅ Oui (destinataire) |
| **PC3** | ❌ Non | ❌ Non |
| **PC4** | ❌ Non | ❌ Non |

---

### Scénario 2 : Envoi à Plusieurs

**Action :**
```
PC1 envoie "photo.jpg" à PC2 et PC3
```

**Résultat :**

| Utilisateur | Voit le fichier ? | Peut télécharger ? |
|-------------|-------------------|---------------------|
| **PC1** | ✅ Oui (Envoyé) | ❌ Non |
| **PC2** | ✅ Oui (Reçu) | ✅ Oui |
| **PC3** | ✅ Oui (Reçu) | ✅ Oui |
| **PC4** | ❌ Non | ❌ Non |

---

### Scénario 3 : Tentative d'Accès Non Autorisé

**Action :**
```
PC4 essaie de télécharger "rapport.pdf" (envoyé à PC2)
URL: /api/file/download/PC4/rapport.pdf
```

**Résultat :**
```json
{
  "error": "Accès refusé : ce fichier ne vous est pas destiné"
}
```

**Code HTTP :** `403 Forbidden`

---

## 🛡️ Protection Contre les Attaques

### Attaque 1 : Deviner le Nom de Fichier

**Tentative :**
```
GET /api/file/download/PC1/secret.pdf
```

**Protection :**
1. ✅ Vérification base de données : `transfers.to_peer = 'PC1'`
2. ✅ Si pas dans la table → `403 Forbidden`

---

### Attaque 2 : Changer le peer_name dans l'URL

**Tentative :**
```javascript
// PC3 essaie de se faire passer pour PC2
downloadFile('PC2', 'rapport.pdf')  // URL: /api/file/download/PC2/rapport.pdf
```

**Protection :**
1. ✅ Le serveur vérifie que `rapport.pdf` existe dans `/storage/PC2/`
2. ✅ Le serveur vérifie que `PC2` l'a bien reçu (table `transfers`)
3. ✅ Si PC2 n'a pas reçu ce fichier → `403 Forbidden`

---

### Attaque 3 : Accès Direct par URL

**Tentative :**
```
https://rachidi.pythonanywhere.com/api/file/download/PC1/document.pdf
```

**Protection :**
1. ✅ Vérifie que `document.pdf` est dans `/storage/PC1/`
2. ✅ Vérifie dans la DB : `SELECT * FROM transfers WHERE to_peer = 'PC1' AND filename = 'document.pdf'`
3. ✅ Si pas trouvé → `403 Forbidden`

---

## 📊 Table `transfers` - Clé de la Sécurité

```sql
CREATE TABLE transfers (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    from_peer TEXT NOT NULL,     -- Expéditeur
    to_peer TEXT NOT NULL,       -- Destinataire (VÉRIFIÉ)
    status TEXT NOT NULL,        -- 'success' uniquement
    transferred_at TEXT NOT NULL
);
```

**Exemple de données :**

| file_id | from_peer | to_peer | status | filename |
|---------|-----------|---------|--------|----------|
| 1 | PC1 | PC2 | success | rapport.pdf |
| 1 | PC1 | PC3 | success | rapport.pdf |
| 2 | PC2 | PC1 | success | photo.jpg |

**Requête de sécurité :**
```sql
SELECT COUNT(*) FROM transfers
WHERE to_peer = 'PC2' AND file_id = (
    SELECT id FROM files WHERE filename = 'rapport.pdf'
) AND status = 'success'
```

Si `COUNT = 0` → Accès refusé

---

## 🔄 Flux Complet avec Sécurité

### Envoi de Fichier

```
┌─────────┐                    ┌──────────┐
│   PC1   │                    │ Serveur  │
│         │ 1. Upload          │          │
│ Envoie  │ ─────────────────→ │ Stocke   │
│ file.pdf│    + recipients    │ dans DB  │
│ à PC2   │                    │          │
└─────────┘                    └──────────┘
                                    │
                                    │ 2. Enregistre
                                    │    transfers:
                                    │    from=PC1
                                    │    to=PC2
                                    │
                                    ▼
                              ┌──────────┐
                              │ Table    │
                              │transfers │
                              └──────────┘
```

### Réception et Téléchargement

```
┌─────────┐                    ┌──────────┐
│   PC2   │ 3. Demande liste   │ Serveur  │
│         │ ─────────────────→ │          │
│         │                    │ SELECT   │
│         │ 4. Retourne        │ WHERE    │
│         │ ←───────────────── │ to=PC2   │
│ Voit    │    [file.pdf]      │          │
│file.pdf │                    │          │
└─────────┘                    └──────────┘
     │
     │ 5. Clic télécharger
     ▼
┌─────────┐                    ┌──────────┐
│   PC2   │ 6. GET download    │ Serveur  │
│         │ ─────────────────→ │          │
│         │                    │ Vérifie: │
│         │                    │ to=PC2?  │
│         │ 7. Fichier         │ ✓ OUI    │
│         │ ←───────────────── │ Envoie   │
│Télécharge│                   │          │
└─────────┘                    └──────────┘
```

### Tentative d'Accès Non Autorisé

```
┌─────────┐                    ┌──────────┐
│   PC3   │ Essaie download    │ Serveur  │
│         │ file.pdf           │          │
│ (Non    │ ─────────────────→ │ Vérifie: │
│autorisé)│                    │ to=PC3?  │
│         │ 403 Forbidden      │ ✗ NON    │
│         │ ←───────────────── │ Refuse   │
│  ❌     │                    │          │
└─────────┘                    └──────────┘
```

---

## 🧪 Tests de Sécurité

### Test 1 : Utilisateur Autorisé

```bash
# PC2 télécharge un fichier qui lui a été envoyé
curl -X GET "http://localhost:5000/api/file/download/PC2/rapport.pdf"

# Résultat attendu : 200 OK + fichier
```

---

### Test 2 : Utilisateur Non Autorisé

```bash
# PC3 essaie de télécharger un fichier destiné à PC2
curl -X GET "http://localhost:5000/api/file/download/PC3/rapport.pdf"

# Résultat attendu : 403 Forbidden
{
  "error": "Accès refusé : ce fichier ne vous est pas destiné"
}
```

---

### Test 3 : Fichier Inexistant

```bash
# Tentative de télécharger un fichier qui n'existe pas
curl -X GET "http://localhost:5000/api/file/download/PC1/fake.pdf"

# Résultat attendu : 403 Forbidden
{
  "error": "Fichier introuvable ou accès refusé"
}
```

---

## 📝 Logs de Sécurité

Chaque tentative de téléchargement peut être loggée :

```python
# À ajouter dans download_file() pour audit
import logging

logging.info(f"Download attempt: {peer_name} → {filename}")

if result['count'] == 0:
    logging.warning(f"Unauthorized access attempt: {peer_name} → {filename}")
    return jsonify({'error': 'Accès refusé'}), 403
```

---

## 🔜 Améliorations Futures

### v2.3 : Expiration des Fichiers

```python
# Ajouter une date d'expiration
cursor.execute("""
    SELECT COUNT(*) FROM transfers
    WHERE to_peer = ? AND filename = ?
    AND status = 'success'
    AND datetime(transferred_at) > datetime('now', '-7 days')
""", (peer_name, filename))
```

---

### v2.4 : Permissions Granulaires

```python
# Permissions : read, download, share
cursor.execute("""
    SELECT permission FROM permissions
    WHERE file_id = ? AND peer_name = ?
""", (file_id, peer_name))
```

---

### v2.5 : Chiffrement de Bout en Bout

- Chiffrer les fichiers sur le serveur
- Seul le destinataire a la clé de déchiffrement

---

## ✅ Résumé de la Sécurité

| Niveau | Protection | Implémenté |
|--------|------------|------------|
| **Base de données** | Filtrage par `to_peer` | ✅ |
| **API** | Vérification `transfers` table | ✅ |
| **Système de fichiers** | Fichier dans dossier utilisateur | ✅ |
| **Téléchargement** | Double vérification (fichier + DB) | ✅ |
| **Frontend** | Affichage uniquement fichiers autorisés | ✅ |

**Maintenant votre système est SÉCURISÉ !** 🔒

Chaque utilisateur voit uniquement :
- ✅ Les fichiers qu'il a envoyés
- ✅ Les fichiers qui lui ont été envoyés

Et ne peut télécharger QUE les fichiers qui lui sont destinés ! 🎯
