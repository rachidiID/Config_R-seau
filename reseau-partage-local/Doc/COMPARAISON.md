# Comparaison Version Cloud vs Version Locale

## Architecture

### Version Cloud (reseau-partage/)
```
┌──────────────────┐
│  PythonAnywhere  │
│  (1 Serveur)     │
└────────┬─────────┘
         │
         │ Internet
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ PC1   │ │ PC2   │
│Client │ │Client │
└───────┘ └───────┘
```

### Version Locale (reseau-partage-local/)
```
       LAN (UDP + HTTP)
┌─────────────────────────┐
│                         │
┌▼──────┐  ┌─────────┐  ┌▼──────┐
│ PC1   │  │  PC2    │  │ PC3   │
│Serveur│◄─┤Serveur  │  │Client │
│PRIMARY│  │SECONDARY│  │       │
└───────┘  └─────────┘  └───────┘
```

## Fonctionnalités

| Fonctionnalité | Cloud | Locale |
|----------------|-------|--------|
| Serveur unique | ✅ | ❌ |
| Multi-serveurs | ❌ | ✅ |
| Haute disponibilité | ❌ | ✅ |
| Failover automatique | ❌ | ✅ |
| Découverte réseau | ❌ | ✅ UDP |
| Synchronisation DB | ❌ | ✅ HTTP |
| Accès Internet requis | ✅ | ❌ |
| Accès LAN uniquement | ❌ | ✅ |
| Heartbeat | ✅ | ✅ |
| Status online/offline | ✅ | ✅ |
| Upload/Download | ✅ | ✅ |
| Fragmentation | ✅ | ✅ |
| Interface Web | ✅ | ✅ |

## Technologies

### Version Cloud
- **Flask** : Serveur web
- **SQLite** : Base de données unique
- **APScheduler** : Tâches planifiées (heartbeat cleanup)
- **PythonAnywhere** : Hébergement
- **Navigateur** : Interface client uniquement

### Version Locale
- **Flask** : Serveur web (même code)
- **SQLite** : Base de données (répliquée)
- **APScheduler** : Tâches + synchronisation
- **UDP Broadcast** : Découverte des serveurs
- **netifaces** : Détection IP locale
- **Threading** : Découverte + HA en arrière-plan
- **HTTP** : Communication inter-serveurs

## Fichiers Spécifiques

### Cloud (reseau-partage/)
```
server/
  ├── main.py        ← Serveur Flask principal
  ├── database.py    ← DB SQLite unique
  └── config.py      ← Config serveur
web/
  ├── templates/     ← HTML
  └── static/        ← JS + CSS
```

### Locale (reseau-partage-local/)
```
discovery.py       ← NOUVEAU : Découverte UDP
ha_manager.py      ← NOUVEAU : Haute disponibilité
server_local.py    ← Serveur Flask avec HA
database.py        ← DB avec export/import
launcher.py        ← NOUVEAU : CLI serveur/client
config_local.py    ← Config HA
web/               ← Copié depuis cloud
```

## Configuration

### Cloud
```python
# server/config.py
HOST = '0.0.0.0'
PORT = 5000
DATABASE = 'network.db'
```

### Locale
```python
# config_local.py
DISCOVERY_PORT = 5555        # UDP
SERVER_PORT = 5000           # HTTP
BROADCAST_INTERVAL = 10      # secondes
HEARTBEAT_INTERVAL = 120     # secondes
HA_ENABLED = True
SYNC_INTERVAL = 60           # secondes
```

## Utilisation

### Cloud : Déploiement
```bash
# Sur PythonAnywhere
cd /home/Rachidi/reseau-partage
source venv/bin/activate
pip install -r requirements.txt
python server/main.py

# Sur Client (navigateur)
http://rachidi.pythonanywhere.com
```

### Locale : Test
```bash
# PC1 - Serveur
python launcher.py --mode server --name PC1

# PC2 - Serveur
python launcher.py --mode server --name PC2

# PC3 - Client
python launcher.py --mode client --name PC3
```

## Scénarios d'Usage

### Quand Utiliser la Version Cloud ?

✅ **Accès depuis n'importe où**
- Partage de fichiers entre maison, bureau, smartphone
- Collaboration avec des personnes distantes

✅ **Pas de serveur à gérer**
- PythonAnywhere s'occupe de l'hébergement
- Pas de configuration réseau

✅ **Coût minimal**
- Gratuit jusqu'à 500 MB
- Pas d'infrastructure locale

❌ **Limitations**
- Dépend d'Internet
- Un seul serveur (pas de redondance)
- Vitesse limitée par la bande passante

### Quand Utiliser la Version Locale ?

✅ **Réseau local uniquement**
- Bureau avec plusieurs PCs
- Maison avec réseau privé
- Événement temporaire (LAN party)

✅ **Haute disponibilité**
- Besoin de redondance (2+ serveurs)
- Failover automatique

✅ **Performance**
- Vitesse réseau local (gigabit)
- Pas de latence Internet

✅ **Confidentialité**
- Données restent sur LAN
- Pas de transit Internet

❌ **Limitations**
- Nécessite plusieurs PCs
- Configuration réseau requise
- Pas d'accès distant

## Migration

### Cloud → Locale

1. **Exporter les données** :
```bash
# Sur PythonAnywhere
scp Rachidi@ssh.pythonanywhere.com:/home/Rachidi/reseau-partage/network.db .
scp -r Rachidi@ssh.pythonanywhere.com:/home/Rachidi/reseau-partage/storage .
```

2. **Importer dans locale** :
```bash
# Sur PC local
cp network.db reseau-partage-local/
cp -r storage reseau-partage-local/
```

3. **Lancer** :
```bash
cd reseau-partage-local
python launcher.py --mode server --name MonPC
```

### Locale → Cloud

1. **Exporter DB primaire** :
```bash
curl http://PRIMARY_IP:5000/api/sync/export > network.db
```

2. **Upload vers PythonAnywhere** :
```bash
scp network.db Rachidi@ssh.pythonanywhere.com:/home/Rachidi/reseau-partage/
scp -r storage/* Rachidi@ssh.pythonanywhere.com:/home/Rachidi/reseau-partage/storage/
```

3. **Redémarrer serveur cloud** :
```bash
# Via PythonAnywhere Web Interface
# Reload app
```

## Maintenance

### Cloud
```bash
# Mise à jour
git pull origin main
pip install -r requirements.txt --upgrade

# Logs
tail -f /var/log/pythonanywhere/server.log

# Redémarrage
# Via Web Interface → Reload
```

### Locale
```bash
# Mise à jour
git pull origin main
pip install -r requirements.txt --upgrade

# Logs
# Affichés dans le terminal

# Redémarrage
Ctrl+C puis relancer python launcher.py
```

## Sécurité

### Cloud
- HTTPS fourni par PythonAnywhere
- Authentication username/password
- Base de données non exposée

### Locale
- **⚠️ HTTP non chiffré** (OK pour LAN privé)
- Authentication username/password
- Réseau local seulement (pas d'exposition Internet)
- Recommandé : Firewall pour bloquer accès externe

## Performance

### Cloud
- **Upload** : ~1 MB/s (dépend connexion Internet)
- **Download** : ~5 MB/s (limite PythonAnywhere Free)
- **Latence** : 50-200 ms (dépend localisation)

### Locale
- **Upload** : ~100 MB/s (gigabit LAN)
- **Download** : ~100 MB/s (gigabit LAN)
- **Latence** : 1-5 ms (LAN local)

## Évolutivité

### Cloud
- **Max clients** : ~10 simultanés (Free tier)
- **Max stockage** : 500 MB (Free tier)
- **Upgrade** : Passer à compte payant

### Locale
- **Max clients** : Limité par RAM/CPU des serveurs
- **Max stockage** : Limité par disque dur
- **Upgrade** : Ajouter plus de serveurs

## Coût

### Cloud
- **Gratuit** : 500 MB storage, 1 worker
- **Payant** : $5-20/mois selon besoin

### Locale
- **Matériel** : PCs existants (coût électricité)
- **Logiciel** : Gratuit (open source)

## Cas d'Usage Réels

### Exemple 1 : Entreprise
- **Besoin** : Partage fichiers entre 5 PCs bureau
- **Solution** : Version locale
  * PC1 et PC2 : serveurs (HA)
  * PC3, PC4, PC5 : clients
  * Failover si PC1 crash

### Exemple 2 : Famille
- **Besoin** : Partager photos entre téléphones/PCs
- **Solution** : Version cloud
  * Accès depuis n'importe où
  * Pas de serveur à gérer

### Exemple 3 : Événement
- **Besoin** : Partage fichiers pendant conférence (100 personnes)
- **Solution** : Version locale
  * 3 serveurs pour redondance
  * Vitesse réseau local
  * Pas de dépendance Internet

### Exemple 4 : Développement
- **Besoin** : Tester système distribué
- **Solution** : Version locale
  * 1 PC, 3 terminaux
  * Test failover facilement
  * Pas de coût hébergement

## Recommandations

**Utilisez la version Cloud si** :
- Vous avez ≤ 3 utilisateurs
- Besoin d'accès distant
- Pas de serveur local disponible
- Budget limité

**Utilisez la version Locale si** :
- Vous avez ≥ 2 PCs disponibles
- Réseau local uniquement
- Besoin de haute disponibilité
- Performance critique
- Confidentialité importante

**Utilisez les DEUX si** :
- Cloud pour accès distant
- Locale pour usage quotidien bureau
- Synchronisation périodique entre les deux
