# Guide Complet - Interface Web P2P

## Vue d'ensemble

L'interface web offre une alternative graphique moderne au CLI pour gérer vos transferts de fichiers P2P.

## Démarrage rapide

### 1. Démarrer le serveur

```bash
cd ~/Base_de_données/reseau-partage
source venv/bin/activate
python server/main.py
```

Le serveur démarre sur http://localhost:5000

### 2. Accéder à l'interface web

Ouvrez votre navigateur et allez à:
```
http://localhost:5000/web?name=PC1&port=5001
```

**Paramètres URL:**
- `name` : Nom de votre PC (ex: PC1, PC2, PC3)
- `port` : Port pour recevoir les fichiers (5001, 5002, 5003...)

## Utilisation multi-PC

### Configuration PC1
```
http://localhost:5000/web?name=PC1&port=5001
```

### Configuration PC2  
```
http://localhost:5000/web?name=PC2&port=5002
```

### Configuration PC3
```
http://localhost:5000/web?name=PC3&port=5003
```

## Fonctionnalités

### 📤 Envoyer des fichiers

1. **Sélectionner un fichier:**
   - Cliquez sur la zone de dépôt
   - OU glissez-déposez un fichier

2. **Choisir le destinataire:**
   - Un PC spécifique
   - Tous les PC (option *)

3. **Envoyer:**
   - Cliquez sur "Envoyer le fichier"
   - Suivez la progression en temps réel

### 👥 PC Connectés

- **Liste en temps réel** de tous les PC en ligne
- **Rafraîchissement automatique** toutes les 5 secondes
- **Informations affichées:**
  - Nom du PC
  - Adresse IP
  - Port
  - Statut (En ligne)

### 📥 Fichiers Reçus

- Liste de tous les fichiers/dossiers reçus
- Type (Fichier/Dossier)
- Taille formatée

## Design & Interface

### Thème Moderne
- **Couleurs:** Dégradé violet/bleu professionnel
- **Typographie:** Inter (Google Fonts)
- **Style:** Cards avec ombres douces, coins arrondis

### Responsive
- ✅ Desktop (1200px+)
- ✅ Tablette (768px-1200px)
- ✅ Mobile (< 768px)

### Interactions
- **Glisser-déposer** pour upload
- **Notifications** pour chaque action
- **Barre de progression** animée
- **Auto-refresh** intelligent

## Notifications

Le système affiche automatiquement des notifications pour:
- ✅ Connexion réussie au serveur
- ✅ Fichier envoyé avec succès
- ❌ Erreurs de transfert
- ℹ️ Messages informatifs

Les notifications disparaissent après 3 secondes.

## Comparaison CLI vs Web

| Fonctionnalité | CLI | Web |
|----------------|-----|-----|
| Envoi fichiers | ✅ | ✅ |
| Envoi dossiers | ✅ | 🔄 En cours |
| Liste PC | ✅ | ✅ |
| Fichiers reçus | ✅ | ✅ |
| Progression | Texte | Barre visuelle |
| Interface | Terminal | Navigateur |
| Auto-refresh | ❌ | ✅ |
| Glisser-déposer | ❌ | ✅ |
| Notifications | ❌ | ✅ |

## Utilisation simultanée

Vous pouvez utiliser **CLI et Web en même temps** !

**Terminal 1:** Serveur
```bash
python server/main.py
```

**Terminal 2:** Client CLI PC1
```bash
python client/main.py --name PC1 --port 5001
```

**Navigateur:** Interface Web PC2
```
http://localhost:5000/web?name=PC2&port=5002
```

Les deux clients (CLI et Web) peuvent échanger des fichiers !

## Architecture technique

### Frontend (JavaScript)
- **Vanilla JS** - Pas de framework, léger et rapide
- **Fetch API** - Requêtes HTTP vers le serveur
- **Crypto API** - Calcul des checksums (SHA-256)
- **File API** - Gestion des uploads

### Backend (Flask)
- **Routes API** - Endpoints REST existants
- **Templates** - Rendu HTML avec Jinja2
- **CORS** - Support cross-origin
- **Static files** - CSS/JS servis par Flask

### Communication
```
Interface Web (JS)
    ↓ HTTP/JSON
Serveur Flask (Python)
    ↓ REST API
Base de données SQLite
```

## Sécurité

### Implémenté
- ✅ Validation des fichiers côté client
- ✅ Checksum SHA-256 pour intégrité
- ✅ CORS configuré
- ✅ Enregistrement des transferts

### À venir (Phase 3)
- 🔄 Chiffrement AES-256
- 🔄 Authentification par mot de passe
- 🔄 SSL/HTTPS
- 🔄 Signatures numériques

## Personnalisation

### Changer les couleurs

Éditez `web/static/style.css`:

```css
:root {
    --primary: #2563eb;      /* Bleu principal */
    --success: #10b981;      /* Vert succès */
    --danger: #ef4444;       /* Rouge erreur */
    /* ... */
}
```

### Changer le rafraîchissement

Éditez `web/static/app.js`:

```javascript
// Ligne ~320
refreshInterval = setInterval(() => {
    loadPeers();
    loadFiles();
}, 5000); // 5000ms = 5 secondes
```

## Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le venv est activé
source venv/bin/activate

# Vérifier les dépendances
pip install -r requirements.txt
```

### L'interface ne charge pas
1. Vérifiez l'URL: http://localhost:5000/web
2. Vérifiez que le serveur est démarré
3. Vérifiez la console navigateur (F12)

### Les PC n'apparaissent pas
1. Vérifiez que le serveur est accessible
2. Ouvrez la console (F12) pour voir les erreurs
3. Vérifiez que le nom et port sont corrects dans l'URL

### L'envoi échoue
1. Vérifiez que le destinataire est en ligne
2. Vérifiez la taille du fichier (< 1GB)
3. Regardez la console pour les erreurs

## Raccourcis clavier

- **Ctrl+R** : Rafraîchir la page
- **F5** : Recharger complètement
- **F12** : Ouvrir les outils développeur
- **Ctrl+Shift+I** : Inspecter un élément

## Compatibilité navigateurs

| Navigateur | Version | Support |
|------------|---------|---------|
| Chrome | 90+ | ✅ Complet |
| Firefox | 88+ | ✅ Complet |
| Safari | 14+ | ✅ Complet |
| Edge | 90+ | ✅ Complet |
| Opera | 76+ | ✅ Complet |

## Performance

- **Taille page:** ~15 KB (HTML + CSS + JS)
- **Chargement:** < 100ms
- **Rafraîchissement:** Toutes les 5s
- **Mémoire:** ~5-10 MB par onglet

## Prochaines améliorations

- [ ] Upload de dossiers (drag & drop)
- [ ] WebSockets pour temps réel
- [ ] Historique des transferts
- [ ] Recherche de fichiers
- [ ] Aperçu des fichiers
- [ ] Mode sombre
- [ ] Multi-langues
- [ ] PWA (app installable)

## Support

Pour toute question ou problème, consultez:
- `README.md` - Documentation générale
- `GUIDE_DEBUTANT.md` - Guide débutant complet
- `SCENARIOS.md` - Exemples d'utilisation
