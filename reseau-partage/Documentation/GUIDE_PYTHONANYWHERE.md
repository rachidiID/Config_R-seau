# 🚀 Guide Déploiement PythonAnywhere - Pas à Pas

## ✅ Prérequis
- [x] Compte PythonAnywhere créé
- [x] Code pushé sur GitHub

## 📝 Instructions Détaillées

### Étape 1 : Console Bash PythonAnywhere

1. Aller sur https://www.pythonanywhere.com
2. Se connecter
3. Onglet **"Consoles"** → Cliquer **"Bash"**

### Étape 2 : Cloner le Projet

```bash
# Remplacer USERNAME et REPO par vos valeurs
git clone https://github.com/USERNAME/REPO.git
cd REPO

# Vérifier que tout est là
ls -la
```

### Étape 3 : Créer l'Environnement Virtuel

```bash
# Créer venv
python3.10 -m venv venv

# Activer
source venv/bin/activate

# Installer dépendances
pip install flask flask-cors

# Vérifier
pip list
```

### Étape 4 : Tester Localement (Console)

```bash
# Vérifier que Flask démarre
python server/main.py
# Ctrl+C pour arrêter
```

### Étape 5 : Créer la Web App

1. **Onglet "Web"** dans PythonAnywhere
2. Cliquer **"Add a new web app"**
3. Choisir votre domaine : `username.pythonanywhere.com`
4. Sélectionner **"Manual configuration"**
5. Choisir **"Python 3.10"**
6. Cliquer **"Next"**

### Étape 6 : Configuration de la Web App

Dans la page de configuration :

**Section "Code" :**
- **Source code:** `/home/username/reseau-partage`
- **Working directory:** `/home/username/reseau-partage`

**Section "Virtualenv" :**
- Cliquer **"Enter path to virtualenv"**
- Entrer : `/home/username/reseau-partage/venv`

**Section "WSGI configuration file" :**
- Cliquer sur le lien du fichier WSGI (exemple: `/var/www/username_pythonanywhere_com_wsgi.py`)
- **SUPPRIMER TOUT** le contenu du fichier
- **REMPLACER** par ce code :

```python
import sys
import os

# IMPORTANT: Remplacer 'username' par votre nom d'utilisateur PythonAnywhere
project_home = '/home/username/reseau-partage'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from server.main import app as application
application.config['DEBUG'] = False
application.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
```

- Sauvegarder (bouton **"Save"** en haut)

### Étape 7 : Configuration Statique (Optionnel)

Dans la section **"Static files"** :

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/username/reseau-partage/web/static/` |

Cliquer **"+"** pour ajouter.

### Étape 8 : Recharger l'Application

- Retourner en haut de la page Web
- Cliquer le gros bouton vert **"Reload username.pythonanywhere.com"**

### Étape 9 : Tester !

Ouvrir dans votre navigateur :
```
https://username.pythonanywhere.com/web?name=PC1&port=5001
```

## 🔧 Résolution de Problèmes

### Erreur "ImportError"

**Console Bash :**
```bash
cd ~/reseau-partage
source venv/bin/activate
python -c "from server.main import app; print('OK')"
```

Si erreur, installer dépendances manquantes :
```bash
pip install flask flask-cors
```

### Erreur "500 Internal Server Error"

1. Aller dans **"Web" → "Log files"**
2. Ouvrir **"Error log"**
3. Lire la dernière erreur
4. Corriger le problème

### Application ne se charge pas

1. Vérifier que le chemin `project_home` dans WSGI est correct
2. Vérifier que le venv est activé
3. Cliquer **"Reload"** à nouveau

### Fichiers statiques (CSS/JS) ne chargent pas

1. Vérifier la section **"Static files"**
2. Chemin doit être : `/home/username/reseau-partage/web/static/`
3. Cliquer **"Reload"**

## ⚠️ Limitations Plan Gratuit

- ✅ 100MB d'espace disque
- ✅ 1 web app
- ⚠️ Pas de connexions sortantes (pas de requêtes API externes)
- ⚠️ CPU limité
- ⚠️ Redémarre tous les 3 mois (doit recharger manuellement)
- ⚠️ Pas de custom domain sur plan gratuit

**Impact sur votre projet :**
- ✅ Interface web : Fonctionne
- ✅ Upload fichiers : Fonctionne (<100MB total)
- ✅ Base de données SQLite : Fonctionne
- ⚠️ HA Discovery (UDP) : Ne fonctionnera pas
- ⚠️ Connexions P2P directes : Limitées

## 💡 Astuces

### Garder l'App Active

PythonAnywhere arrête les apps inactives après 3 mois. Pour éviter :
1. Se connecter tous les 2-3 mois
2. Cliquer "Reload"

### Logs en Temps Réel

```bash
# Console Bash
tail -f /var/log/username.pythonanywhere.com.error.log
```

### Mise à Jour du Code

```bash
cd ~/reseau-partage
git pull origin main
# Puis cliquer "Reload" dans l'onglet Web
```

## 🎯 Checklist Finale

- [ ] Console Bash ouverte
- [ ] Repo cloné dans `/home/username/reseau-partage`
- [ ] Venv créé et Flask installé
- [ ] Web App créée (Manual + Python 3.10)
- [ ] Source code configuré
- [ ] Working directory configuré
- [ ] Virtualenv configuré
- [ ] Fichier WSGI modifié et sauvegardé
- [ ] Static files configuré (optionnel)
- [ ] Bouton "Reload" cliqué
- [ ] URL testée dans le navigateur

## 📞 Besoin d'Aide ?

Si vous bloquez à une étape, envoyez-moi :
1. Le message d'erreur exact
2. Le contenu du error log (onglet Web → Log files)
3. L'étape où ça bloque

---

**Temps estimé :** 10-15 minutes ⏱️
**Niveau :** Débutant 🟢
