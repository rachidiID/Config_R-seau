# 🚀 Quick Start - Fonctionnalités Avancées

## Installation Rapide

```bash
cd reseau-partage

# Les modules sont déjà inclus, aucune dépendance supplémentaire
python demo_advanced.py
```

## 🎮 Démonstration Interactive

Testez les fonctionnalités avec le script de démonstration :

```bash
python demo_advanced.py

# Menu :
# 1. Fragmentation de fichiers  ← Voir le découpage en chunks
# 2. Haute disponibilité (HA)   ← Voir l'élection de serveur
# 3. Intégration                ← Scénario complet
# 4. Toutes les démonstrations  ← Tout voir d'un coup
```

## 🔄 Mode Haute Disponibilité (3 minutes)

### Étape 1 : Démarrer 3 serveurs

**Terminal 1** (Serveur Principal - PC1)
```bash
python server/main.py --ha --name Server1 --priority 3
```

**Terminal 2** (Serveur Backup - PC2)
```bash
python server/main.py --ha --name Server2 --priority 2 --port 5001
```

**Terminal 3** (Serveur Backup - PC3)
```bash
python server/main.py --ha --name Server3 --priority 1 --port 5002
```

Vous devriez voir :
```
[HA] Système de haute disponibilité démarré
[HA] Serveur primaire : Server1
[INFO] Serveur découvert: Server2
[INFO] Serveur découvert: Server3
```

### Étape 2 : Connecter un client

**Terminal 4** (Client - PC4)
```bash
python client/main.py --name PC4 --auto-discover
```

Le client se connecte automatiquement au serveur primaire.

### Étape 3 : Tester le basculement

1. Dans PC4, envoyez un fichier :
   ```
   PC4> send test.txt PC5
   ```

2. Arrêtez Server1 (Ctrl+C dans Terminal 1)

3. Attendez 15 secondes → Vous verrez :
   ```
   [HA] Serveur Server1 est hors ligne
   [HA] Serveur primaire : Server2
   ```

4. Dans PC4, envoyez à nouveau :
   ```
   PC4> send test2.txt PC5  # Fonctionne toujours !
   ```

✅ **Résultat** : Le réseau continue de fonctionner même après la panne !

## 📦 Mode Fragmentation (5 minutes)

### Étape 1 : Créer un gros fichier de test

```bash
# Créer un fichier de 1.5 GB
dd if=/dev/urandom of=bigfile.bin bs=1M count=1536
```

### Étape 2 : Démarrer le réseau

**Terminal 1** (Serveur)
```bash
python server/main.py
```

**Terminal 2-4** (3 Clients)
```bash
# Terminal 2
python client/main.py --name PC1 --server http://localhost:5000

# Terminal 3
python client/main.py --name PC2 --server http://localhost:5000

# Terminal 4
python client/main.py --name PC3 --server http://localhost:5000
```

### Étape 3 : Envoyer le gros fichier

Dans PC1 :
```bash
PC1> send bigfile.bin PC2
```

Vous verrez :
```
[...] Fichier de 1.5 GB détecté
[OK] Fragmentation activée : 6 chunks de 256 MB
[...] Calcul du hash du fichier complet...
[OK] Fragmentation terminée : 6 chunks créés

Distribution des chunks :
  Chunk 0 → PC2, PC3
  Chunk 1 → PC3, PC1
  Chunk 2 → PC1, PC2
  Chunk 3 → PC2, PC3
  Chunk 4 → PC3, PC1
  Chunk 5 → PC1, PC2

[...] Envoi des chunks en cours...
  [████████████████] 100% - Chunk 0/6 → PC2
  [████████████████] 100% - Chunk 0/6 → PC3
  ...
[OK] Transfert terminé : 6/6 chunks envoyés
```

### Étape 4 : Vérifier la distribution

```bash
# Sur PC1
ls -lh storage/PC1/*.chunk*

# Sur PC2
ls -lh storage/PC2/*.chunk*

# Sur PC3
ls -lh storage/PC3/*.chunk*
```

Chaque PC a une partie du fichier !

### Étape 5 : Reconstruire le fichier

Dans PC2 :
```bash
PC2> list
# Fichiers reçus :
#   [📦] bigfile.bin (1.5 GB, fragmenté)
#        Status: 6/6 chunks disponibles

PC2> reconstruct bigfile.bin
```

Vous verrez :
```
[...] Reconstruction de bigfile.bin...
  [OK] Chunk 1/6 récupéré
  [OK] Chunk 2/6 récupéré
  ...
[...] Vérification du hash du fichier reconstruit...
[OK] Fichier reconstruit avec succès
```

### Étape 6 : Vérifier l'intégrité

```bash
# Comparer les checksums
md5sum bigfile.bin
md5sum storage/PC2/bigfile.bin

# Doivent être identiques !
```

✅ **Résultat** : Fichier de 1.5 GB distribué sur 3 PCs et reconstruit avec succès !

## 🎯 Mode Intégré (HA + Fragmentation)

Combinez les deux fonctionnalités :

```bash
# 3 serveurs HA
python server/main.py --ha --name S1 --priority 3 &
python server/main.py --ha --name S2 --priority 2 --port 5001 &
python server/main.py --ha --name S3 --priority 1 --port 5002 &

# 5 clients
python client/main.py --name PC1 --auto-discover &
python client/main.py --name PC2 --auto-discover &
python client/main.py --name PC3 --auto-discover &
python client/main.py --name PC4 --auto-discover &
python client/main.py --name PC5 --auto-discover &

# Attendre 5 secondes pour la découverte
sleep 5

# Dans PC1, envoyer un gros fichier
# Le fichier sera fragmenté ET le réseau sera résilient
```

## 📊 Commandes Utiles

### Monitoring HA

```bash
# Voir les serveurs actifs
curl http://localhost:5000/api/ha/status

# Voir le serveur primaire
curl http://localhost:5000/api/ha/primary
```

### Gestion Fragmentation

```python
# Dans le client Python
from shared.fragmentation import FileFragmenter

# Fragmenter manuellement
fragmenter = FileFragmenter()
metadata = fragmenter.fragment_file("bigfile.dat", "chunks/")

# Reconstruire manuellement
fragmenter.reconstruct_file("chunks/", metadata, "output.dat")
```

### Nettoyage

```bash
# Supprimer les anciens chunks (>7 jours)
find storage/ -name "*.chunk*" -mtime +7 -delete

# Supprimer les métadonnées orphelines
find storage/ -name "*.metadata.json" -mtime +7 -delete
```

## ⚡ Configuration Rapide

Modifiez `server/config.py` :

```python
# Haute Disponibilité
HEARTBEAT_INTERVAL = 5      # Heartbeat toutes les 5s
SERVER_TIMEOUT = 15         # Timeout après 15s
DISCOVERY_PORT = 5555       # Port UDP discovery

# Fragmentation
FRAGMENTATION_THRESHOLD = 1 * 1024 * 1024 * 1024  # 1 GB
CHUNK_SIZE = 256 * 1024 * 1024                    # 256 MB
REDUNDANCY_FACTOR = 2                              # 2 copies/chunk
```

## 🐛 Dépannage Rapide

### Problème : Serveurs ne se découvrent pas
```bash
# Vérifier le firewall
sudo ufw allow 5555/udp

# Vérifier le broadcast
ip route | grep broadcast
```

### Problème : Chunks manquants
```bash
# Vérifier les chunks disponibles
ls -l storage/*/bigfile.bin.chunk*

# Télécharger depuis la redondance
python client/main.py
PC1> fetch-chunks bigfile.bin
```

### Problème : Serveur primaire bloqué
```bash
# Forcer l'élection
kill -SIGUSR1 $(pgrep -f "server/main.py")
```

## 📚 Prochaines Lectures

- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Documentation complète
- **[shared/fragmentation.py](shared/fragmentation.py)** - Code source fragmentation
- **[shared/high_availability.py](shared/high_availability.py)** - Code source HA

## 🎉 Vous êtes prêt !

Votre réseau P2P est maintenant :
- ✅ Hautement disponible (sans point de défaillance)
- ✅ Capable de gérer de gros fichiers (>1GB)
- ✅ Distribué sur plusieurs machines
- ✅ Résilient aux pannes

Bon partage de fichiers ! 🚀
