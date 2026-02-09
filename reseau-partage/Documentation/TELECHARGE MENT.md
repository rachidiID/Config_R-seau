# 📥 Téléchargement de Fichiers - Guide Complet

## 🎯 Comment Ça Marche ?

### Architecture de Stockage

```
storage/
├── PC1/
│   ├── document.pdf      (envoyé par PC1)
│   └── photo.jpg         (reçu de PC2)
├── PC2/
│   ├── photo.jpg         (envoyé par PC2)
│   └── video.mp4         (reçu de PC3)
└── PC3/
    └── video.mp4         (envoyé par PC3)
```

**Principe :**
- Chaque PC a un dossier `storage/NomPC/`
- Les fichiers **envoyés** ET **reçus** sont stockés dans ce dossier
- Le serveur copie automatiquement les fichiers vers les destinataires

---

## 📥 Télécharger un Fichier Reçu

### Depuis l'Interface Web

1. **Accéder aux fichiers reçus**
   - Section "Fichiers reçus et envoyés" à droite
   - Les fichiers reçus ont un badge bleu **"Reçu"** et l'icône 📥

2. **Cliquer sur le bouton "📥 Télécharger"**
   - Le fichier se télécharge automatiquement dans votre dossier "Téléchargements"

3. **Notification**
   - "Téléchargement de nom_fichier.ext..."

### Exemple Visuel

```
┌─ Fichiers reçus et envoyés (2) ──────────┐
│                                           │
│  📥 rapport.pdf                           │
│  2.5 MB • De: PC2                         │
│  [Reçu]  [📥 Télécharger]  ←──── Cliquez ici
│                                           │
│  📤 presentation.pptx                     │
│  8.3 MB • À: PC3                          │
│  [Envoyé]                                 │
│                                           │
└───────────────────────────────────────────┘
```

---

## 🔧 API de Téléchargement

### Endpoint

```
GET /api/file/download/<peer_name>/<filename>
```

### Paramètres

- **peer_name** : Nom du PC propriétaire du fichier
- **filename** : Nom du fichier à télécharger

### Exemples

**Télécharger un fichier de PC1 :**
```bash
GET /api/file/download/PC1/rapport.pdf
```

**Télécharger un fichier de PC2 :**
```bash
GET /api/file/download/PC2/photo.jpg
```

### Réponse

- **200 OK** : Le fichier est téléchargé
- **404 Not Found** : Fichier introuvable

---

## 🎮 Scénarios d'Usage

### Scénario 1 : Téléchargement Simple

**PC1 envoie `rapport.pdf` à PC2**

1. PC1 : Sélectionne `rapport.pdf`, destinataire = PC2, envoie
2. Serveur : 
   - Stocke dans `storage/PC1/rapport.pdf`
   - Copie dans `storage/PC2/rapport.pdf`
3. PC2 : Voit `rapport.pdf` dans "Fichiers reçus"
4. PC2 : Clique "📥 Télécharger"
5. Navigateur : Télécharge depuis `storage/PC2/rapport.pdf`

---

### Scénario 2 : Téléchargement Multiple

**PC1 envoie `photo.jpg` à PC2 et PC3**

1. PC1 : Sélectionne `photo.jpg`, destinataire = "Tous les PC", envoie
2. Serveur :
   - Stocke dans `storage/PC1/photo.jpg`
   - Copie dans `storage/PC2/photo.jpg`
   - Copie dans `storage/PC3/photo.jpg`
3. PC2 et PC3 : Voient `photo.jpg` dans "Fichiers reçus"
4. PC2 : Clique "📥 Télécharger" → télécharge depuis `storage/PC2/`
5. PC3 : Clique "📥 Télécharger" → télécharge depuis `storage/PC3/`

---

### Scénario 3 : Accès Direct par URL

Si vous connaissez le nom du PC et le fichier, accès direct :

```
https://rachidi.pythonanywhere.com/api/file/download/PC1/rapport.pdf
```

**⚠️ Pas de vérification d'authentification pour le moment**
→ Tout le monde peut télécharger si l'URL est connue

---

## 🔒 Sécurité (À Venir)

### Limitations Actuelles

- ⚠️ Pas de vérification de permissions
- ⚠️ Pas de token requis
- ⚠️ URL directe = accès direct

### Améliorations Futures

1. **Vérifier le token** avant téléchargement
2. **Permissions** : Seul le destinataire peut télécharger
3. **Expiration** : Liens temporaires
4. **Chiffrement** : Fichiers chiffrés au repos

---

## 📊 Flux Complet

```
┌─────────┐  1. Upload    ┌──────────┐  2. Copie   ┌─────────┐
│   PC1   │ ────────────→ │ Serveur  │ ──────────→ │   PC2   │
│         │               │          │             │         │
│ Envoie  │               │ Storage: │             │ Reçoit  │
│ file.pdf│               │ PC1/ et  │             │ file.pdf│
└─────────┘               │ PC2/     │             └─────────┘
                          └──────────┘                   │
                                ↑                        │
                                │ 3. Download            │
                                └────────────────────────┘
```

**Étapes :**

1. **Upload** : PC1 envoie le fichier au serveur
2. **Copie** : Serveur copie le fichier vers le dossier de chaque destinataire
3. **Download** : PC2 télécharge depuis son propre dossier

---

## 💡 Bonnes Pratiques

### Pour les Utilisateurs

1. **Télécharger rapidement** : Les fichiers restent sur le serveur
2. **Espace limité** : Sur PythonAnywhere gratuit (100MB total)
3. **Nettoyer** : Supprimer les anciens fichiers (fonctionnalité à venir)

### Pour les Administrateurs

1. **Surveiller l'espace disque** : `du -sh storage/`
2. **Nettoyer périodiquement** : Scripts de nettoyage automatique
3. **Logs** : Vérifier qui télécharge quoi

---

## 🛠️ Dépannage

### Erreur 404 "Fichier introuvable"

**Causes :**
- Le fichier a été supprimé du serveur
- Nom de fichier incorrect
- Caractères spéciaux dans le nom

**Solutions :**
```bash
# Vérifier que le fichier existe
ls storage/PC1/

# Vérifier les permissions
chmod 644 storage/PC1/*.pdf
```

---

### Téléchargement ne démarre pas

**Causes :**
- Popup bloqué par le navigateur
- JavaScript désactivé
- Connexion coupée

**Solutions :**
1. Autoriser les popups pour le site
2. Réessayer en cliquant à nouveau
3. Utiliser l'URL directe

---

### Fichier corrompu après téléchargement

**Causes :**
- Interruption pendant la copie
- Problème de checksum

**Solutions :**
```bash
# Vérifier l'intégrité avec checksum
sha256sum storage/PC1/file.pdf
```

---

## 🚀 Améliorations Planifiées

### v2.2 (Prochaine Version)

- [ ] Bouton de téléchargement pour fichiers envoyés aussi
- [ ] Historique des téléchargements
- [ ] Statistiques (nombre de téléchargements)
- [ ] Bouton "Supprimer" pour les fichiers
- [ ] Aperçu avant téléchargement (images, PDF)

### v2.3 (Future)

- [ ] Téléchargement par lot (ZIP multiple fichiers)
- [ ] Partage de liens temporaires
- [ ] Chiffrement de bout en bout
- [ ] Quotas par utilisateur

---

## 📝 Code Source

### Backend (Flask)

```python
@app.route('/api/file/download/<peer_name>/<filename>', methods=['GET'])
def download_file(peer_name, filename):
    filename = secure_filename(filename)
    file_dir = os.path.join(WEB_UPLOAD_DIR, peer_name)
    
    if not os.path.exists(os.path.join(file_dir, filename)):
        return jsonify({'error': 'Fichier introuvable'}), 404
    
    return send_from_directory(
        file_dir, 
        filename, 
        as_attachment=True,
        download_name=filename
    )
```

### Frontend (JavaScript)

```javascript
function downloadFile(peerName, filename) {
    const downloadUrl = `${API_BASE}/file/download/${encodeURIComponent(peerName)}/${encodeURIComponent(filename)}`;
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification(`Téléchargement de ${filename}...`, 'info');
}
```

---

## 🎯 Résumé

**Téléchargement = 1 clic !**

✅ Bouton "📥 Télécharger" sur chaque fichier reçu  
✅ Téléchargement automatique dans votre navigateur  
✅ Notification de confirmation  
✅ Stockage sécurisé sur le serveur  
✅ Accès direct par URL aussi possible  

**C'est aussi simple que ça !** 🎉
