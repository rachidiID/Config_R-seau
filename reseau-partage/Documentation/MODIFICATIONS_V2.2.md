# Modifications v2.2 - Gestion des statuts et nettoyage

## Nouvelles fonctionnalités

### 1. Statut des utilisateurs (Online/Offline)

**Problème résolu :** Les utilisateurs déconnectés apparaissaient toujours comme "En ligne"

**Solution :**
- Heartbeat automatique toutes les 2 minutes
- Statut "offline" après 5 minutes d'inactivité
- Suppression automatique après 10 heures de déconnexion

---

### 2. Interface sans emojis

**Problème résolu :** Interface encombrée par les emojis/stickers

**Solution :**
- Suppression de tous les emojis dans index.html, login.html, app.js
- Remplacement par du texte clair : [REÇU], [ENVOYÉ], [Fichiers], etc.
- Suppression de "v2.0" du titre

---

## Modifications techniques

### Backend (server/)

#### database.py
**3 nouvelles fonctions :**

```python
def update_peer_last_seen(name: str):
    """Mettre à jour last_seen lors du heartbeat"""
    UPDATE peers SET last_seen = NOW(), status = 'online'

def update_peers_status():
    """Marquer offline les peers inactifs >5 min"""
    UPDATE peers SET status = 'offline' 
    WHERE last_seen < NOW() - 5 minutes

def cleanup_inactive_peers():
    """Supprimer les peers inactifs >10h"""
    DELETE FROM peers 
    WHERE last_seen < NOW() - 10 hours
```

#### main.py
**Nouvelles routes :**

```python
@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Signal de vie d'un peer"""
    db.update_peer_last_seen(peer_name)
```

**Scheduler automatique :**

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scheduled_cleanup,  # update_peers_status + cleanup_inactive_peers
    trigger="interval",
    minutes=5  # Toutes les 5 minutes
)
scheduler.start()
```

---

### Frontend (web/)

#### app.js

**Heartbeat automatique :**

```javascript
function sendHeartbeat() {
    await fetch(`${API_BASE}/heartbeat`, {
        method: 'POST',
        body: JSON.stringify({ name: peerName })
    });
}

function startHeartbeat() {
    sendHeartbeat();  // Immédiat
    setInterval(sendHeartbeat, 120000);  // Toutes les 2 min
}
```

**Affichage statut :**

```javascript
async function loadPeers() {
    const response = await fetch(`${API_BASE}/peers`);  // Tous les peers
    
    allPeers.map(peer => {
        const isOnline = peer.status === 'online';
        const statusClass = isOnline ? 'peer-status-online' : 'peer-status-offline';
        const statusText = isOnline ? 'En ligne' : 'Hors ligne';
        
        // HTML avec classe CSS différente selon statut
    });
}
```

#### style.css

**Styles pour statuts :**

```css
.peer-status-online {
    background: #d1fae5;  /* Vert clair */
    color: #065f46;       /* Vert foncé */
}

.peer-status-offline {
    background: #f3f4f6;  /* Gris clair */
    color: #9ca3af;       /* Gris */
}

.peer-item.peer-offline {
    opacity: 0.6;  /* Transparence pour peers offline */
}
```

#### index.html

**Suppression emojis :**

```html
<!-- AVANT -->
<h1>🌐 Réseau de Partage P2P v2.0</h1>
<div class="upload-icon">📁</div>
<div class="empty-state-icon">👥</div>

<!-- APRÈS -->
<h1>Réseau de Partage P2P</h1>
<div class="upload-icon">[Fichier]</div>
<div class="empty-state-icon">[PCs]</div>
```

#### login.html

```html
<!-- AVANT -->
<div class="login-logo">🌐</div>
<h1>Réseau P2P v2.0</h1>

<!-- APRÈS -->
<div class="login-logo">[P2P]</div>
<h1>Réseau P2P</h1>
```

---

## Dépendances

**Nouveau paquet :**

```bash
pip install APScheduler==3.10.4
```

Ajouté dans [requirements.txt](../requirements.txt)

---

## Comportement attendu

### Scénario 1 : Connexion normale

```
1. PC1 se connecte → status='online', last_seen=NOW
2. Heartbeat toutes les 2 min → last_seen mis à jour
3. PC1 visible comme "En ligne" (vert)
```

### Scénario 2 : Déconnexion propre

```
1. PC1 clique "Se déconnecter" → Ferme navigateur
2. Pas de heartbeat pendant 5+ min
3. Scheduler marque PC1 comme offline
4. PC1 visible comme "Hors ligne" (gris, transparent)
```

### Scénario 3 : Déconnexion brutale

```
1. PC1 perd connexion internet / crash
2. Pas de heartbeat pendant 5+ min → status='offline'
3. Pas de heartbeat pendant 10+ heures → PC1 supprimé de la DB
```

### Scénario 4 : Reconnexion

```
1. PC1 se reconnecte après 2h d'absence
2. Heartbeat immédiat → status='online', last_seen=NOW
3. PC1 réapparaît comme "En ligne"
```

---

## Vérification des logs

### Logs serveur (local)

```bash
cd /home/rachidi/Base_de_données/Config_R-seau/reseau-partage
python server/main.py

# Sortie attendue toutes les 5 min :
Statuts mis à jour : 2 peer(s) marqués offline
✓ Nettoyage : 1 peer(s) inactif(s) supprimés: PC4
```

### Logs PythonAnywhere

**Error Log :**
```
/var/log/rachidi.pythonanywhere.com.error.log
```

**Console :**
```bash
tail -f /var/log/rachidi.pythonanywhere.com.error.log
```

---

## Tests

### Test 1 : Heartbeat

```javascript
// Console navigateur (F12)
fetch('/api/heartbeat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'PC1'})
}).then(r => r.json()).then(console.log)

// Résultat attendu : {status: 'ok'}
```

### Test 2 : Statut après déconnexion

```
1. PC1 connecté → Fermer navigateur
2. Attendre 6 minutes
3. PC2 ouvre interface → PC1 devrait être "Hors ligne"
```

### Test 3 : Suppression après 10h

```sql
-- Simuler un peer inactif depuis 11h
UPDATE peers SET last_seen = datetime('now', '-11 hours') WHERE name = 'PC_TEST';

-- Attendre 5 min (prochain scheduler run)
-- Vérifier suppression
SELECT * FROM peers WHERE name = 'PC_TEST';  -- Aucun résultat
```

---

## Déploiement

### Étape 1 : Commit et push

```bash
cd /home/rachidi/Base_de_données/Config_R-seau/reseau-partage

git add -A
git commit -m "✨ v2.2: Statut online/offline + auto-cleanup + suppression emojis"
git push
```

### Étape 2 : Update PythonAnywhere

**Console PythonAnywhere :**
```bash
cd ~/Config_R-seau

# Résoudre conflits git
git stash  # Sauvegarder changements locaux
# OU : git reset --hard HEAD  # Abandonner changements locaux

# Pull
git pull origin main

# Activer virtualenv
source reseau-partage/venv/bin/activate

# Installer (SANS --user)
pip install APScheduler==3.10.4
```

**Web tab :**
- Cliquer "Reload" 

### Étape 3 : Vérifier

1. Ouvrir https://rachidi.pythonanywhere.com
2. Connecter PC1 et PC2
3. Fermer onglet PC1
4. Attendre 6 minutes
5. Rafraîchir PC2 → PC1 doit être "Hors ligne"

---

## Architecture Serveur/Client

**Document complet :** [ARCHITECTURE_SERVEUR_CLIENT.md](ARCHITECTURE_SERVEUR_CLIENT.md)

### Résumé

**Serveur :**
- 1 seul (PythonAnywhere)
- Annuaire + DB + interface web
- Port 443 (HTTPS)

**Clients :**
- Tous les utilisateurs via navigateur
- PC1, PC2, PC3, Rachidi...
- Envoient heartbeat toutes les 2 min

**Principe :**
```
SERVEUR (Flask)
    │
    ├─► PC1 (client via browser)
    ├─► PC2 (client via browser)
    └─► PC3 (client via browser)
```

---

## Fichiers modifiés

```
server/
  ├─ database.py          [+3 fonctions]
  └─ main.py              [+1 route, +scheduler]

web/
  ├─ static/
  │  ├─ app.js            [+heartbeat, +statut visuel]
  │  └─ style.css         [+peer-status-online/offline]
  └─ templates/
     ├─ index.html        [-emojis, -v2.0]
     └─ login.html        [-emojis, -v2.0]

requirements.txt          [+APScheduler]

Documentation/
  ├─ MODIFICATIONS_V2.2.md           [ce fichier]
  └─ ARCHITECTURE_SERVEUR_CLIENT.md  [nouveau]
```

---

## Problèmes connus

### PythonAnywhere Free Tier

**Limitation :** APScheduler peut ne pas fonctionner sur free tier (pas de background processes).

**Solutions :**
1. Upgrade vers paid account ($5/mois)
2. Utiliser always-on task (paid feature)
3. Appeler manuellement l'API de cleanup :

```python
# Ajouter route pour trigger manuel
@app.route('/api/admin/cleanup', methods=['POST'])
def manual_cleanup():
    updated = db.update_peers_status()
    deleted = db.cleanup_inactive_peers()
    return jsonify({'updated': updated, 'deleted': deleted})
```

### Heartbeat en arrière-plan

Si l'utilisateur ferme l'onglet, le heartbeat s'arrête → normal, c'est l'objectif !

---

## Améliorations futures (v2.3)

- [ ] Notification push quand peer se connecte/déconnecte
- [ ] Historique des connexions (logs)
- [ ] Badge "Vu il y a X minutes" au lieu de juste online/offline
- [ ] Auto-reconnexion si serveur redémarre
- [ ] Export/import liste des peers

---

## Support

**Questions ?** Consultez :
- [ARCHITECTURE_SERVEUR_CLIENT.md](ARCHITECTURE_SERVEUR_CLIENT.md) - Architecture complète
- [SECURITE.md](SECURITE.md) - Sécurité et permissions
- [GUIDE_V2.1.md](GUIDE_V2.1.md) - Guide utilisateur

**Bugs ?** Vérifiez :
- Error Log PythonAnywhere
- Console navigateur (F12)
- Table `peers` dans SQLite
