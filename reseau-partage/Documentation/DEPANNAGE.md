# Guide de Dépannage - PythonAnywhere

## Problèmes de Déploiement

### ❌ Erreur : "Your local changes would be overwritten by merge"

**Symptôme :**
```bash
error: Your local changes to the following files would be overwritten by merge:
        reseau-partage/venv/bin/pip
Please commit your changes or stash them before you merge.
```

**Cause :** Le dossier `venv/` a été modifié localement (PythonAnywhere) et est aussi dans git.

**Solution 1 : Stash (sauvegarde temporaire)**
```bash
cd ~/Config_R-seau
git stash
git pull origin main
git stash pop  # Récupérer changements (optionnel)
```

**Solution 2 : Reset (abandonner changements)**
```bash
cd ~/Config_R-seau
git reset --hard HEAD
git pull origin main
```

**Solution 3 : Ignorer venv (recommandé)**
```bash
# Sur votre PC local
cd ~/Base_de_données/Config_R-seau/reseau-partage

# Ajouter .gitignore
echo "venv/" >> .gitignore

# Supprimer venv/ du git
git rm -r --cached venv/
git commit -m "Remove venv from git"
git push

# PythonAnywhere recréera son propre venv
```

---

### ❌ Erreur : "Can not perform a '--user' install"

**Symptôme :**
```bash
pip install --user APScheduler==3.10.4
ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.
```

**Cause :** Le flag `--user` ne fonctionne pas dans un virtualenv.

**Solution :**
```bash
# MAUVAIS (dans virtualenv)
pip install --user APScheduler==3.10.4

# BON (dans virtualenv)
pip install APScheduler==3.10.4

# BON (hors virtualenv)
pip3.10 install --user APScheduler==3.10.4
```

**Comment savoir si je suis dans un virtualenv ?**
```bash
# Si le prompt commence par (venv) → dans virtualenv
(venv) 14:40 ~/Config_R-seau$  # ← Virtualenv actif

# Sinon → hors virtualenv
14:40 ~/Config_R-seau$  # ← Pas de virtualenv
```

---

### ❌ Erreur : "Error reloading web app"

**Symptôme :** Bouton "Reload" sur PythonAnywhere → erreur

**Causes possibles :**

1. **Import manquant**
```python
# Error Log : ModuleNotFoundError: No module named 'apscheduler'
```

**Solution :**
```bash
source reseau-partage/venv/bin/activate
pip install APScheduler==3.10.4
```

2. **Syntaxe Python incorrecte**
```python
# Error Log : SyntaxError: invalid syntax
```

**Solution :** Vérifier le code, corriger l'erreur, push, pull, reload.

3. **app.run() dans production**
```python
# MAUVAIS pour PythonAnywhere
if __name__ == '__main__':
    app.run()  # ← Bloque le WSGI
```

**Solution :** Voir [FIX_PYTHONANYWHERE.md](FIX_PYTHONANYWHERE.md)

---

### ⚠️ Warning : APScheduler ne démarre pas

**Symptôme :** Pas d'erreur, mais les peers offline ne sont pas nettoyés.

**Cause :** PythonAnywhere Free ne supporte pas les background processes.

**Vérification :**
```bash
# Error Log devrait afficher (toutes les 5 min) :
Statuts mis à jour : X peer(s) marqués offline
✓ Nettoyage : Y peer(s) inactifs supprimés

# Si rien → scheduler ne tourne pas
```

**Solutions :**

1. **Upgrade vers paid account** ($5/mois)
   - Always-on tasks disponibles
   - Pas de restrictions background processes

2. **Trigger manuel via cron**
   - Schedule tab → Créer daily task
   ```bash
   curl -X POST https://rachidi.pythonanywhere.com/api/admin/cleanup
   ```
   - Nécessite d'ajouter la route dans [server/main.py](../server/main.py)

3. **Accepter les limites**
   - Les heartbeats fonctionnent
   - Le statut se met à jour lors des requêtes
   - Le cleanup se fait progressivement

---

## Problèmes de Base de Données

### ❌ Erreur : "database is locked"

**Symptôme :**
```
sqlite3.OperationalError: database is locked
```

**Cause :** Plusieurs requêtes simultanées sur SQLite.

**Solution :**
```python
# Dans database.py, ajouter timeout
conn = sqlite3.connect(self.db_path, timeout=10.0)
```

---

### ❌ Base de données corrompue

**Symptôme :** Erreurs aléatoires, données manquantes.

**Solution :**
```bash
# Backup
cp server/peers.db server/peers.db.backup

# Réinitialiser
rm server/peers.db
python server/main.py  # Recrée la DB
```

---

## Problèmes de Session

### ❌ Déconnexion automatique

**Symptôme :** Utilisateur déconnecté après quelques minutes.

**Cause :** Token expiré (24h par défaut).

**Solution :**
```javascript
// Dans web/static/app.js, augmenter durée
const SESSION_DURATION = 7 * 24 * 60 * 60 * 1000;  // 7 jours
```

---

### ❌ "Session expired" mais token valide

**Cause :** Peer supprimé de la DB (inactif >10h).

**Solution :** Se reconnecter (crée nouveau peer).

---

## Problèmes de Fichiers

### ❌ "Accès refusé" au téléchargement

**Symptôme :** Erreur 403 lors du téléchargement.

**Causes :**

1. **Fichier pas destiné à cet utilisateur**
   - Voir [SECURITE.md](SECURITE.md)
   - Vérifier table `transfers`

2. **Fichier supprimé du disque**
```bash
ls -la storage/PC1/
# Si vide → fichier perdu
```

**Solution :** Renvoyer le fichier.

---

### ❌ Upload échoue (500 MB)

**Symptôme :** Barre de progression bloquée à 100%.

**Cause :** PythonAnywhere Free limite : 100 MB disk.

**Solution :**
- Nettoyer anciens fichiers
- Upgrade vers paid account
- Utiliser fragmentation (<1 GB)

---

## Vérifications Systématiques

### Checklist après déploiement

```bash
# 1. Vérifier installation
pip list | grep -i apscheduler

# 2. Tester connexion
curl https://rachidi.pythonanywhere.com/web

# 3. Tester heartbeat
curl -X POST https://rachidi.pythonanywhere.com/api/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"name":"TEST"}'

# 4. Voir error log
tail -f /var/log/rachidi.pythonanywhere.com.error.log
```

---

### Checklist avant commit/push

```bash
# 1. Tester localement
python server/main.py

# 2. Vérifier syntaxe
python -m py_compile server/main.py

# 3. Vérifier .gitignore
git status  # Ne devrait PAS voir venv/

# 4. Commit
git add -A
git commit -m "Description"
git push
```

---

## Commandes Utiles

### Git

```bash
# Voir état
git status

# Annuler changements locaux
git checkout -- fichier.py

# Voir différences
git diff

# Historique
git log --oneline -10
```

### PythonAnywhere Console

```bash
# Activer virtualenv
source reseau-partage/venv/bin/activate

# Désactiver virtualenv
deactivate

# Installer tous requirements
pip install -r requirements.txt

# Voir packages installés
pip list

# Upgrade pip
pip install --upgrade pip
```

### SQLite

```bash
# Ouvrir DB
sqlite3 server/peers.db

# Voir tables
.tables

# Voir peers
SELECT name, status, last_seen FROM peers;

# Supprimer peer
DELETE FROM peers WHERE name = 'TEST';

# Quitter
.quit
```

---

## Support

### Logs à consulter

1. **PythonAnywhere Error Log**
   - Web tab → "Log files" section
   - `/var/log/rachidi.pythonanywhere.com.error.log`

2. **Console Navigateur (F12)**
   - Tab Console
   - Rechercher erreurs rouges

3. **SQLite Database**
   ```bash
   sqlite3 server/peers.db "SELECT * FROM peers;"
   ```

### Informations à fournir

Lors d'un problème, incluez :
- Message d'erreur exact
- Error log (dernières lignes)
- Commandes exécutées
- Version Python : `python --version`
- Packages : `pip list`

---

## Ressources

- [FIX_PYTHONANYWHERE.md](FIX_PYTHONANYWHERE.md) - Erreurs deployment
- [SECURITE.md](SECURITE.md) - Problèmes permissions
- [ARCHITECTURE_SERVEUR_CLIENT.md](ARCHITECTURE_SERVEUR_CLIENT.md) - Comment ça marche
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
