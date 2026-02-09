# 🌐 Guide de Déploiement - Réseau P2P v2.0

## ❌ GitHub Pages - NON Compatible

**GitHub Pages ne peut PAS héberger ce projet** car :

- ❌ GitHub Pages = sites **statiques uniquement** (HTML/CSS/JS)
- ❌ Votre projet = serveur **Python/Flask** (backend dynamique)
- ❌ Pas de support Python, base de données, ou WebSockets sur GitHub Pages

**Ce qui fonctionnerait sur GitHub Pages :**
- ✅ Uniquement le frontend (HTML/CSS/JS)
- ❌ Pas le serveur backend
- ❌ Pas les transferts de fichiers
- ❌ Pas la base de données

## ✅ Solutions de Déploiement Recommandées

### Option 1 : Serveur VPS (Recommandé pour Production)

#### Avantages
- ✅ Contrôle total
- ✅ Performances maximales
- ✅ IP fixe
- ✅ Support HA complet
- ✅ Bande passante dédiée

#### Providers Recommandés

**1. DigitalOcean (5-10$/mois)**
```bash
# 1. Créer un Droplet Ubuntu 22.04

# 2. Se connecter en SSH
ssh root@votre_ip

# 3. Installer les dépendances
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y

# 4. Cloner votre projet
git clone https://github.com/votre-username/reseau-partage.git
cd reseau-partage

# 5. Créer l'environnement
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configurer le firewall
ufw allow 5000/tcp
ufw allow 5555/udp
ufw enable

# 7. Lancer avec systemd (voir ci-dessous)
```

**2. Linode, Vultr, Hetzner (similaire à DigitalOcean)**

**3. Contabo (3-5€/mois, moins cher)**

#### Configuration Systemd (Démarrage Automatique)

```bash
# Créer le fichier service
sudo nano /etc/systemd/system/reseau-p2p.service
```

Contenu :
```ini
[Unit]
Description=Réseau P2P Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/reseau-partage
Environment="PATH=/root/reseau-partage/venv/bin"
ExecStart=/root/reseau-partage/venv/bin/python server/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable reseau-p2p
sudo systemctl start reseau-p2p
sudo systemctl status reseau-p2p
```

#### Nginx comme Reverse Proxy (Optionnel mais recommandé)

```bash
# Installer Nginx
apt install nginx -y

# Configuration
nano /etc/nginx/sites-available/reseau-p2p
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /root/reseau-partage/web/static;
    }
}
```

Activer :
```bash
ln -s /etc/nginx/sites-available/reseau-p2p /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### SSL avec Let's Encrypt (HTTPS)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d votre-domaine.com
```

### Option 2 : PythonAnywhere (Gratuit/Payant)

#### Avantages
- ✅ Gratuit pour petits projets
- ✅ Pas de configuration serveur
- ✅ Interface web simple

#### Limitations
- ⚠️ Plan gratuit : connexions sortantes limitées
- ⚠️ Pas de support WebSockets direct
- ⚠️ CPU/RAM limités

#### Étapes

1. Créer un compte sur [PythonAnywhere](https://www.pythonanywhere.com)

2. Upload votre code via Git :
```bash
git clone https://github.com/votre-username/reseau-partage.git
cd reseau-partage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configuration Web App :
- Aller dans "Web" tab
- Add new web app
- Flask
- Python 3.10
- Source code: `/home/username/reseau-partage`
- Working directory: `/home/username/reseau-partage`
- Virtualenv: `/home/username/reseau-partage/venv`

4. Modifier `server/main.py` :
```python
# Remplacer la fin du fichier
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # PythonAnywhere utilise 8000
```

### Option 3 : Heroku (Payant, ancien gratuit supprimé)

#### Configuration

Créer `Procfile` :
```
web: python server/main.py
```

Créer `runtime.txt` :
```
python-3.11.2
```

Déployer :
```bash
heroku login
heroku create mon-reseau-p2p
git push heroku main
```

### Option 4 : Railway.app (5$/mois après crédit gratuit)

#### Avantages
- ✅ Simple à déployer
- ✅ Git push = auto-deploy
- ✅ Base de données PostgreSQL incluse
- ✅ Domaine gratuit

#### Étapes

1. Se connecter sur [Railway.app](https://railway.app)

2. New Project → Deploy from GitHub

3. Sélectionner votre repo

4. Variables d'environnement :
```
PORT=5000
FLASK_ENV=production
```

5. Deploy automatique !

### Option 5 : Render.com (Gratuit/Payant)

#### Avantages
- ✅ Plan gratuit disponible
- ✅ SSL automatique
- ✅ Déploiement Git

#### Configuration

Créer `render.yaml` :
```yaml
services:
  - type: web
    name: reseau-p2p
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python server/main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.2
```

### Option 6 : Serveur Local avec DynDNS (Gratuit)

#### Pour utiliser votre PC personnel comme serveur

**Avantages :**
- ✅ Totalement gratuit
- ✅ Contrôle total
- ✅ Pas de limite de bande passante

**Inconvénients :**
- ⚠️ Votre PC doit rester allumé 24/7
- ⚠️ IP dynamique (besoin de DynDNS)
- ⚠️ Sécurité à gérer

**Étapes :**

1. **Configurer le port forwarding sur votre routeur**
   - Port 5000 (HTTP)
   - Port 5555 (UDP pour HA)

2. **Installer un service DynDNS**
   ```bash
   # No-IP (gratuit)
   wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz
   tar xf noip-duc-linux.tar.gz
   cd noip-2.1.9-1/
   make install
   ```

3. **Lancer le serveur**
   ```bash
   python server/main.py
   ```

4. **Accès externe**
   - URL : `http://votre-domaine.ddns.net:5000`

## 🔐 Sécurité pour Production

### 1. Variables d'environnement

Créer `.env` :
```bash
SECRET_KEY=votre_clé_secrète_longue_et_aléatoire
DATABASE_PATH=/var/lib/reseau-p2p/network.db
FLASK_ENV=production
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

Charger dans le code :
```python
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. Firewall (UFW)

```bash
# Autoriser seulement les ports nécessaires
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5000/tcp  # Serveur P2P
ufw allow 5555/udp  # HA Discovery
ufw enable
```

### 3. Fail2Ban (Protection contre brute-force)

```bash
apt install fail2ban -y

# Créer /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
```

### 4. Désactiver DEBUG en production

Dans `server/config.py` :
```python
DEBUG = False  # IMPORTANT !
```

### 5. HTTPS obligatoire

Avec Let's Encrypt (voir configuration Nginx ci-dessus).

## 📊 Comparaison des Options

| Provider | Prix/mois | Setup | HA Support | Performance | Recommandation |
|----------|-----------|-------|------------|-------------|----------------|
| **VPS (DigitalOcean)** | 5-10$ | ⭐⭐⭐ | ✅ Complet | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ Production |
| **PythonAnywhere** | 0-5$ | ⭐⭐⭐⭐⭐ | ⚠️ Limité | ⭐⭐⭐ | ⭐⭐⭐ Prototypes |
| **Railway.app** | 5$ | ⭐⭐⭐⭐⭐ | ✅ Oui | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ Simplicité |
| **Render.com** | 0-7$ | ⭐⭐⭐⭐ | ⚠️ Limité | ⭐⭐⭐ | ⭐⭐⭐ Gratuit |
| **Heroku** | 7$ | ⭐⭐⭐⭐ | ✅ Oui | ⭐⭐⭐⭐ | ⭐⭐⭐ Cher |
| **Serveur Local** | 0$ | ⭐⭐ | ⚠️ DIY | Variable | ⭐⭐ Expérimentation |

## 🎯 Recommandation Finale

### Pour Débuter (Tests/Prototypes)
➡️ **Render.com** (gratuit) ou **Railway.app** (5$ de crédit)

### Pour Production Sérieuse
➡️ **DigitalOcean VPS** avec Nginx + SSL + Systemd

### Pour Maximum de Simplicité
➡️ **Railway.app** (git push = deploy)

### Pour Budget Zéro
➡️ **Serveur Local** + No-IP + Port Forwarding

## 📝 Checklist Avant Déploiement

- [ ] `DEBUG = False` dans config.py
- [ ] Variables sensibles dans `.env`
- [ ] Firewall configuré (UFW)
- [ ] SSL/HTTPS activé (Let's Encrypt)
- [ ] Logs configurés
- [ ] Backup automatique de la DB
- [ ] Monitoring (Uptime Robot, etc.)
- [ ] Tests de charge effectués
- [ ] Documentation à jour

## 🚀 Déploiement Rapide (DigitalOcean)

Script complet :
```bash
#!/bin/bash
# deploy.sh

# 1. Mise à jour système
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y

# 2. Clone projet
cd /opt
git clone https://github.com/votre-username/reseau-partage.git
cd reseau-partage

# 3. Environnement Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
ufw allow 5555/udp
ufw --force enable

# 5. Systemd service (voir config ci-dessus)
# ... copier la configuration systemd ...

# 6. Nginx (voir config ci-dessus)
# ... copier la configuration nginx ...

# 7. SSL
certbot --nginx -d votre-domaine.com

echo "✅ Déploiement terminé !"
echo "🌐 Accès : https://votre-domaine.com"
```

## 📞 Support

Pour des questions de déploiement, consultez :
- [Documentation DigitalOcean](https://docs.digitalocean.com)
- [Guide Flask Production](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Résumé** : GitHub Pages ❌ | VPS ✅ | PaaS (Railway/Render) ✅
