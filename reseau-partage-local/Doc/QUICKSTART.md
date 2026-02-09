# Démarrage Rapide - Réseau P2P Local avec Haute Disponibilité

## Installation

1. **Créer un environnement virtuel** (recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

## Test sur un seul PC (développement)

### Terminal 1 - Serveur Principal (PC1)
```bash
python launcher.py --mode server --name PC1
```
Devrait afficher : "Rôle : PRIMAIRE"

### Terminal 2 - Serveur Secondaire (PC2)
```bash
python launcher.py --mode server --name PC2
```
Devrait afficher : "Rôle : SECONDAIRE"

### Terminal 3 - Client (PC3)
```bash
python launcher.py --mode client --name PC3
```
Le navigateur s'ouvre automatiquement sur le serveur primaire.

## Test sur plusieurs PCs (réseau local)

### Sur PC1 (192.168.1.10) :
```bash
python launcher.py --mode server --name PC1
```

### Sur PC2 (192.168.1.11) :
```bash
python launcher.py --mode server --name PC2
```

### Sur PC3 (192.168.1.12) :
```bash
python launcher.py --mode client --name PC3
```

## Mode Interactif

Si vous lancez sans arguments :
```bash
python launcher.py
```
Un menu apparaît :
```
1. Démarrer un serveur
2. Démarrer un client
Choix : 1
Nom du nœud : MonPC
```

## Vérification de l'état

### Via l'interface web :
- Ouvrez http://IP_SERVEUR:5000/web
- Connectez-vous (username/password)
- La liste des pairs montre les serveurs et clients

### Via API :
```bash
# État HA
curl http://localhost:5000/api/ha/status

# Santé du serveur
curl http://localhost:5000/api/health

# Liste des pairs
curl http://localhost:5000/api/peers
```

## Test de Basculement (Failover)

1. Démarrez PC1 (devient primaire) et PC2 (devient secondaire)
2. Arrêtez PC1 avec Ctrl+C
3. Attendez 15 secondes
4. PC2 devrait devenir primaire automatiquement
5. Les clients se reconnectent à PC2

## Scénarios de Test

### Scénario 1 : Démarrage progressif
1. Démarrez PC1 → primaire
2. Démarrez PC2 → secondaire (sync avec PC1)
3. Démarrez PC3 client → se connecte au primaire

### Scénario 2 : Panne du primaire
1. PC1 (primaire) + PC2 (secondaire) actifs
2. Arrêtez PC1
3. PC2 devient primaire en <15s
4. Créez un fichier sur PC2
5. Redémarrez PC1 → devient secondaire, sync le nouveau fichier

### Scénario 3 : Ajout dynamique
1. PC1 primaire + PC3 client actifs
2. Démarrez PC2 → devient secondaire, sync immédiat
3. PC3 voit PC2 dans la liste des pairs

## Vérification des Logs

Les serveurs affichent :
- Découverte des autres serveurs : "Serveur découvert : PC2 @ 192.168.1.11"
- Rôle attribué : "Rôle : PRIMAIRE" ou "Rôle : SECONDAIRE"
- Synchronisation : "Synchronisation avec le primaire réussie"
- Fichiers transférés : "Fichier reçu : test.txt (1234 bytes)"

## Dépannage

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Port 5000 déjà utilisé"
Tuez le processus existant :
```bash
lsof -i :5000
kill -9 <PID>
```

### "Aucun serveur découvert"
- Vérifiez que les PCs sont sur le même réseau local
- Désactivez le pare-feu ou autorisez UDP port 5555
- Vérifiez que netifaces détecte la bonne IP :
```python
import netifaces
netifaces.ifaddresses('eth0')  # ou 'wlan0'
```

### "Erreur de synchronisation"
- Le secondaire ne peut pas sync si le primaire est arrêté
- Attendez que le secondaire devienne primaire
- Vérifiez les logs : "Tentative de synchronisation..."

## Architecture

```
┌─────────┐     UDP broadcast      ┌─────────┐
│  PC1    │ ←──────────────────→  │  PC2    │
│ PRIMAIRE│         5555          │SECONDAIRE│
└────┬────┘                        └────┬────┘
     │                                  │
     │   HTTP sync DB (60s)            │
     │ ←────────────────────────────── │
     │                                  │
     └───────────┬──────────────────────┘
                 │
         HTTP client access
                 │
            ┌────┴────┐
            │  PC3    │
            │ CLIENT  │
            └─────────┘
```

## Fonctionnalités Principales

- **Découverte automatique** : Les serveurs se trouvent via UDP broadcast
- **Élection automatique** : Le serveur avec priorité la plus élevée devient primaire (ordre alphabétique)
- **Synchronisation** : Les secondaires synchronisent leur base de données avec le primaire toutes les 60s
- **Basculement** : Si le primaire tombe, le secondaire devient primaire en <15s
- **Heartbeat** : Les clients envoient un signal toutes les 2 minutes
- **Nettoyage** : Les pairs inactifs >10h sont supprimés automatiquement

## Commandes Utiles

```bash
# Voir les serveurs découverts
watch -n 1 'curl -s http://localhost:5000/api/ha/status | python -m json.tool'

# Tester le transfert de fichier
curl -X POST -F "file=@test.txt" http://localhost:5000/api/file/upload

# Lister les fichiers disponibles
curl http://localhost:5000/api/files

# Télécharger un fichier
curl http://localhost:5000/api/file/download/MonPC/test.txt -o test_dl.txt
```

## Limitations Connues

1. **Synchronisation des fichiers** : Actuellement, seule la base de données est synchronisée, pas le contenu du dossier `storage/`
2. **Split-brain** : Si le réseau se divise, chaque segment élira son propre primaire (pas de quorum)
3. **Ordre des messages** : Aucune garantie d'ordre global entre serveurs
4. **Sécurité** : Pas de chiffrement des communications (OK pour LAN privé)

## Support

Pour plus de détails, consultez :
- `README.md` : Architecture complète
- `config_local.py` : Configuration des ports et timers
- `discovery.py` : Algorithme de découverte et élection
- `ha_manager.py` : Logique de haute disponibilité
