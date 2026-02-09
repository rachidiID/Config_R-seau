# 🚨 Correction Erreur PythonAnywhere

## Problème Rencontré

```
Error Reloading web app
```

## 🔍 Diagnostics

### Causes Identifiées

1. ❌ **app.run()** dans server/main.py (incompatible avec PythonAnywhere)
2. ❌ **DEBUG = True** dans config.py (doit être False en production)
3. ⚠️ **Fichier WSGI** doit pointer vers le bon chemin

---

## ✅ Solutions Appliquées

### 1. Correction de server/main.py

**Avant (incompatible) :**
```python
if __name__ == '__main__':
    main()
```

**Après (compatible) :**
```python
if __name__ == '__main__':
    main()
else:
    # En mode WSGI (PythonAnywhere), l'application est déjà prête
    application = app
```

✅ **Correction automatique appliquée !**

---

### 2. Désactiver DEBUG en Production

**Fichier à modifier** : `server/config.py`

```python
# DEBUG
DEBUG = False  # ← Changer à False pour PythonAnywhere
```

---

### 3. Vérifier le Fichier WSGI sur PythonAnywhere

Le fichier `/var/www/rachidi_pythonanywhere_com_wsgi.py` doit contenir :

```python
import sys
import os

# IMPORTANT: Remplacer Rachidi par votre vrai username PythonAnywhere
project_home = '/home/Rachidi/Config_R-seau/reseau-partage'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importer l'application Flask
from server.main import app as application

# Configuration production
application.config['DEBUG'] = False
application.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

**⚠️ Points critiques :**
- ✅ Chemin absolu correct : `/home/Rachidi/Config_R-seau/reseau-partage`
- ✅ Import : `from server.main import app as application`
- ✅ DEBUG = False
- ❌ **PAS** de `app.run()` nulle part

---

## 🚀 Procédure de Correction Complète

### Sur Votre Machine Locale

```bash
cd ~/Base_de_données/Config_R-seau/reseau-partage

# Mettre à jour config.py
echo "# DEBUG
DEBUG = False" >> server/config.py

# Commiter les changements
git add -A
git commit -m "🔧 Fix: Compatible avec PythonAnywhere (pas de app.run, DEBUG=False)"
git push origin main
```

---

### Sur PythonAnywhere

#### Étape 1 : Mettre à Jour le Code

```bash
# Console Bash PythonAnywhere
cd ~/Config_R-seau/reseau-partage
git pull origin main
```

#### Étape 2 : Vérifier le Fichier WSGI

1. **Onglet Web** → Cliquer sur le lien WSGI
2. **Vérifier le contenu** (voir code ci-dessus)
3. **Sauvegarder** (bouton Save)

#### Étape 3 : Vérifier les Dépendances

```bash
# Console Bash PythonAnywhere
cd ~/Config_R-seau/reseau-partage
source venv/bin/activate
pip list

# Vérifier que Flask et flask-cors sont installés
pip show flask
pip show flask-cors

# Si manquants :
pip install flask flask-cors
```

#### Étape 4 : Tester l'Import

```bash
# Console Bash PythonAnywhere
cd ~/Config_R-seau/reseau-partage
source venv/bin/activate
python3 -c "from server.main import app; print('✅ Import OK')"
```

**Si erreur :**
- Lire le message d'erreur
- Vérifier les imports manquants
- Installer les dépendances manquantes

#### Étape 5 : Recharger l'Application

1. **Onglet Web**
2. Bouton vert **"Reload rachidi.pythonanywhere.com"**
3. Attendre 20-30 secondes
4. ✅ **Devrait fonctionner !**

---

## 🔍 Vérification Post-Reload

### Tester l'Application

```
https://rachidi.pythonanywhere.com/web
```

**Page attendue :** Page de connexion avec formulaire

**Si erreur 502/504 :**
```bash
# Console Bash PythonAnywhere
cd ~/Config_R-seau/reseau-partage
python3 -c "from server.main import app; print('OK')"
```

### Consulter les Logs

**En cas d'erreur, vérifier :**

1. **Error Log** (onglet Web → Log files)
   - Erreurs Python
   - Imports manquants
   - Exceptions

2. **Server Log**
   - Messages "harakiri" (timeout 5 min)
   - Problèmes de démarrage

3. **Access Log**
   - Requêtes HTTP
   - Codes de statut

---

## 🛠️ Problèmes Courants et Solutions

### Problème 1 : ModuleNotFoundError

```
ModuleNotFoundError: No module named 'flask'
```

**Solution :**
```bash
cd ~/Config_R-seau/reseau-partage
source venv/bin/activate
pip install flask flask-cors
```

---

### Problème 2 : ImportError (circular import)

```
ImportError: cannot import name 'app' from partially initialized module
```

**Solution :** Vérifier qu'il n'y a pas de `app.run()` en dehors du bloc `if __name__ == '__main__'`

---

### Problème 3 : 502 Bad Gateway

**Causes :**
- Mauvais chemin dans le WSGI
- Import échoue
- Venv non activé

**Solution :**
```bash
# Vérifier le chemin exact
pwd
# Doit afficher : /home/Rachidi/Config_R-seau/reseau-partage

# Tester l'import manuellement
python3 -c "import sys; sys.path.insert(0, '/home/Rachidi/Config_R-seau/reseau-partage'); from server.main import app; print('OK')"
```

---

### Problème 4 : Timeout (20 secondes)

**Causes :**
- Code qui s'exécute au démarrage
- Imports lents

**Solution :** Mettre les opérations lourdes en asynchrone ou lazy loading

---

### Problème 5 : Harakiri (5 minutes)

**Causes :**
- Requête qui prend >5 minutes
- Boucle infinie

**Solution :** Vérifier le code pour des opérations bloquantes

---

## 📋 Checklist de Déploiement

Avant de cliquer "Reload" :

- [ ] `DEBUG = False` dans config.py
- [ ] Pas de `app.run()` dans le code principal
- [ ] WSGI file correctement configuré
- [ ] Chemin absolu correct dans WSGI
- [ ] `flask` et `flask-cors` installés dans venv
- [ ] Test d'import réussi : `python3 -c "from server.main import app"`
- [ ] Code pushé sur GitHub
- [ ] `git pull` effectué sur PythonAnywhere
- [ ] Venv activé

---

## 🎯 Commandes Rapides

### Test Complet

```bash
# Sur PythonAnywhere
cd ~/Config_R-seau/reseau-partage
source venv/bin/activate

# Test 1 : Import
python3 -c "from server.main import app; print('✅ Import OK')"

# Test 2 : Dépendances
pip list | grep -i flask

# Test 3 : Chemin
pwd
# Doit afficher : /home/Rachidi/Config_R-seau/reseau-partage

# Test 4 : Structure
ls -la server/
# Doit montrer : main.py, config.py, database.py, __init__.py
```

### Logs en Temps Réel

```bash
# Console Bash
tail -f /var/log/rachidi.pythonanywhere.com.error.log
```

---

## ✅ Résumé

**3 Corrections Principales :**

1. ✅ **server/main.py** : Exposer `application = app` pour WSGI
2. ✅ **server/config.py** : `DEBUG = False`
3. ✅ **WSGI file** : Chemin correct + import correct

**Après ces corrections :**
```bash
git pull origin main
# Vérifier WSGI file
# Cliquer "Reload"
```

**🎉 Ça devrait fonctionner !**

---

## 📞 Si Ça Ne Marche Toujours Pas

1. Copier **le message d'erreur exact** du Error Log
2. Copier **les dernières lignes** du Server Log
3. Vérifier **le code de statut** (502, 504, 500)
4. Essayer **d'importer manuellement** dans la console Bash

**Message typique de succès :**
```
✅ Application loaded successfully
```

**Bon déploiement !** 🚀
