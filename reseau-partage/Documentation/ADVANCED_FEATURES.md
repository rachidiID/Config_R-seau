# 🚀 Guide des Fonctionnalités Avancées

## Vue d'ensemble

Ce document explique deux fonctionnalités avancées ajoutées au système de partage de fichiers P2P :

1. **Haute Disponibilité (HA)** - Réseau multi-serveurs sans point de défaillance unique
2. **Fragmentation de Fichiers** - Distribution automatique des gros fichiers (>1GB) sur plusieurs PCs

---

## 🔄 1. Haute Disponibilité (Multi-Serveurs)

### Problème Résolu

❌ **Avant** : Le réseau dépendait d'un seul serveur central. Si ce PC tombait en panne, tout le réseau s'arrêtait.

✅ **Maintenant** : Plusieurs serveurs peuvent fonctionner simultanément avec basculement automatique.

### Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Serveur 1  │◄────►│  Serveur 2  │◄────►│  Serveur 3  │
│  (Primary)  │      │ (Secondary) │      │ (Secondary) │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │  Heartbeats + Élection + Synchronisation
       │                    │                    │
┌──────▼─────────────────────▼─────────────────────▼──────┐
│                        Clients                          │
│  (se connectent automatiquement au serveur primaire)    │
└──────────────────────────────────────────────────────────┘
```

### Fonctionnalités

#### 1. **Découverte Automatique**
- Les serveurs se découvrent automatiquement via UDP broadcast (port 5555)
- Heartbeats envoyés toutes les 5 secondes
- Détection automatique des serveurs hors ligne (timeout 15s)

#### 2. **Élection du Serveur Primaire**
- Le serveur avec la **plus haute priorité** devient primaire
- En cas d'égalité, ordre alphabétique par nom
- Basculement automatique si le primaire tombe

#### 3. **Réplication de Données**
- Synchronisation automatique de la base de données toutes les 30s
- Les serveurs secondaires se synchronisent avec le primaire
- Basculement sans perte de données

### Configuration

#### Démarrer un serveur en mode HA

**Serveur 1 (Priorité haute - deviendra primaire)**
```bash
python server/main.py --ha --name Server1 --priority 3
```

**Serveur 2 (Priorité moyenne - backup)**
```bash
python server/main.py --ha --name Server2 --priority 2
```

**Serveur 3 (Priorité basse - backup)**
```bash
python server/main.py --ha --name Server3 --priority 1
```

#### Options de ligne de commande

- `--ha` : Activer le mode haute disponibilité
- `--name NAME` : Nom unique du serveur
- `--priority N` : Priorité (1-10, plus élevé = prioritaire)

### Utilisation Client

Les clients n'ont **rien à changer** ! Ils se connectent automatiquement :

1. Le client interroge le réseau pour trouver les serveurs disponibles
2. Se connecte automatiquement au serveur primaire
3. Bascule automatiquement si le primaire tombe

```bash
# Le client découvre automatiquement le serveur primaire
python client/main.py --name PC1 --auto-discover
```

### Monitoring

Les serveurs affichent en temps réel :
```
[HA] Système de haute disponibilité démarré
     Serveur: Server1 (192.168.1.10:5000)
     Priorité: 3
[HA] Serveur primaire : Server1 (ancien: Aucun)
[HA] Je suis maintenant le serveur PRIMAIRE
[INFO] Serveur découvert: Server2
[INFO] Serveur découvert: Server3
```

---

## 📦 2. Fragmentation de Fichiers (>1GB)

### Problème Résolu

❌ **Avant** : 
- Fichiers volumineux saturaient un seul PC
- Transferts lents et fragiles
- Pas de distribution de charge

✅ **Maintenant** : 
- Fichiers >1GB divisés automatiquement en chunks de 256MB
- Chaque chunk stocké sur 2+ PCs différents (redondance)
- Reconstruction transparente
- Distribution de charge optimale

### Architecture

```
Fichier de 2.5 GB
        │
        ├─► Chunk 0 (256MB) → PC1, PC2
        ├─► Chunk 1 (256MB) → PC2, PC3
        ├─► Chunk 2 (256MB) → PC3, PC1
        ├─► Chunk 3 (256MB) → PC1, PC2
        ├─► Chunk 4 (256MB) → PC2, PC3
        ├─► Chunk 5 (256MB) → PC3, PC1
        ├─► Chunk 6 (256MB) → PC1, PC2
        ├─► Chunk 7 (256MB) → PC2, PC3
        ├─► Chunk 8 (256MB) → PC3, PC1
        └─► Chunk 9 (228MB) → PC1, PC2
```

### Fonctionnalités

#### 1. **Fragmentation Automatique**
- Seuil : 1 GB (configurable)
- Taille des chunks : 256 MB (configurable)
- Hash SHA-256 pour chaque chunk
- Métadonnées JSON sauvegardées

#### 2. **Distribution Intelligente**
- Algorithme de rotation circulaire
- Redondance : 2 copies minimum par chunk
- Équilibrage de charge automatique
- Évite la surcharge d'un seul PC

#### 3. **Reconstruction Transparente**
- Récupération automatique des chunks
- Vérification d'intégrité (hash)
- Téléchargement parallèle
- Reconstruction même si un PC est HS (grâce à la redondance)

### Configuration

#### Dans `server/config.py`

```python
# Fragmentation
FRAGMENTATION_THRESHOLD = 1024 * 1024 * 1024  # 1 GB
CHUNK_SIZE = 256 * 1024 * 1024  # 256 MB
REDUNDANCY_FACTOR = 2  # Nombre de copies par chunk
```

### Utilisation

#### Envoi d'un gros fichier (automatique)

```bash
# Le système détecte automatiquement la taille
PC1> send /path/to/large_file.iso PC2

# Sortie :
[...] Fichier de 2.5 GB détecté
[OK] Fragmentation activée : 10 chunks de 256 MB
[...] Calcul du hash du fichier complet...
[OK] Fragmentation terminée : 10 chunks créés
[...] Distribution des chunks :
      Chunk 0 → PC2, PC3
      Chunk 1 → PC3, PC1
      Chunk 2 → PC1, PC2
      ...
[OK] Envoi des chunks en cours...
  [█████████████████] 100% - Chunk 0/10 → PC2
  [█████████████████] 100% - Chunk 0/10 → PC3
  [█████████████████] 100% - Chunk 1/10 → PC3
  ...
[OK] Transfert terminé : 10/10 chunks envoyés
```

#### Réception et reconstruction (automatique)

```bash
PC2> list

# Sortie :
Fichiers reçus :
  [📦] large_file.iso (2.5 GB, fragmenté)
       Status: 10/10 chunks disponibles
       Depuis: PC1
       
PC2> reconstruct large_file.iso

# Sortie :
[...] Reconstruction de large_file.iso...
  [OK] Chunk 1/10 récupéré depuis PC2
  [OK] Chunk 2/10 récupéré depuis PC3
  ...
[...] Vérification du hash du fichier reconstruit...
[OK] Fichier reconstruit avec succès : /storage/PC2/large_file.iso
```

### API Fragmentation

#### Fragmenter manuellement un fichier

```python
from shared.fragmentation import FileFragmenter

fragmenter = FileFragmenter(chunk_size=256 * 1024 * 1024)

# Fragmenter
metadata = fragmenter.fragment_file(
    filepath="/path/to/bigfile.dat",
    output_dir="/tmp/chunks"
)

print(f"Créé {metadata.total_chunks} chunks")
```

#### Reconstruire manuellement un fichier

```python
from shared.fragmentation import FileFragmenter, FragmentedFileMetadata

# Charger les métadonnées
metadata = FragmentedFileMetadata.load_from_file("/tmp/chunks/bigfile.dat.metadata.json")

# Reconstruire
fragmenter = FileFragmenter()
success = fragmenter.reconstruct_file(
    chunks_dir="/tmp/chunks",
    metadata=metadata,
    output_path="/output/bigfile.dat"
)
```

#### Calculer la distribution optimale

```python
from shared.fragmentation import get_chunk_distribution

distribution = get_chunk_distribution(
    chunks_count=10,
    available_peers=["PC1", "PC2", "PC3"],
    redundancy=2
)

# Résultat : {0: ['PC1', 'PC2'], 1: ['PC2', 'PC3'], 2: ['PC3', 'PC1'], ...}
```

---

## 🔧 Tests et Validation

### Test HA (Haute Disponibilité)

```bash
# Terminal 1 : Démarrer Server1 (primaire)
python server/main.py --ha --name Server1 --priority 3

# Terminal 2 : Démarrer Server2 (backup)
python server/main.py --ha --name Server2 --priority 2 --port 5001

# Terminal 3 : Client
python client/main.py --name PC1 --auto-discover

# Dans PC1, envoyer un fichier (via Server1)
PC1> send test.txt PC2

# Terminal 1 : Tuer Server1 (Ctrl+C)

# Le système bascule automatiquement sur Server2
[HA] Serveur Server1 est hors ligne
[HA] Serveur primaire : Server2 (ancien: Server1)

# Dans PC1, envoyer à nouveau (via Server2 maintenant)
PC1> send test2.txt PC2  # Fonctionne toujours !
```

### Test Fragmentation

```bash
# Créer un gros fichier de test (2 GB)
dd if=/dev/urandom of=bigfile.bin bs=1M count=2048

# Terminal 1 : Serveur
python server/main.py

# Terminal 2 : PC1
python client/main.py --name PC1 --server http://localhost:5000

# Terminal 3 : PC2
python client/main.py --name PC2 --server http://localhost:5000

# Terminal 4 : PC3
python client/main.py --name PC3 --server http://localhost:5000

# Dans PC1, envoyer le gros fichier
PC1> send bigfile.bin PC2

# Vérifier les chunks créés
ls -lh storage/PC1/
# bigfile.bin.chunk0000  (256 MB)
# bigfile.bin.chunk0001  (256 MB)
# ...
# bigfile.bin.metadata.json

# Dans PC2, reconstruire
PC2> list
PC2> reconstruct bigfile.bin

# Vérifier l'intégrité
md5sum bigfile.bin storage/PC2/bigfile.bin  # Doivent être identiques
```

---

## 📊 Avantages et Limitations

### Haute Disponibilité

#### ✅ Avantages
- Zéro temps d'arrêt
- Basculement automatique
- Scalabilité horizontale
- Pas de point de défaillance unique

#### ⚠️ Limitations
- Latence de synchronisation (30s max)
- Nécessite 2+ serveurs pour être efficace
- Consommation réseau accrue (heartbeats)

### Fragmentation

#### ✅ Avantages
- Distribution de charge
- Redondance automatique
- Transferts parallèles plus rapides
- Résilience aux pannes

#### ⚠️ Limitations
- Overhead de 2-3% (métadonnées + hashes)
- Nécessite 2+ PCs pour la redondance
- Espace disque 2x (chaque chunk sur 2 PCs)

---

## 🎯 Bonnes Pratiques

### Pour la Haute Disponibilité

1. **Priorités** : Donnez des priorités différentes aux serveurs
   - Serveur principal : priorité 5-10
   - Backups : priorité 1-4

2. **Répartition géographique** : Placez les serveurs sur des réseaux différents

3. **Monitoring** : Surveillez les logs pour les basculements

### Pour la Fragmentation

1. **Nombre de PCs** : Au minimum 3 PCs pour une bonne distribution

2. **Espace disque** : Prévoir 2x l'espace pour les fichiers fragmentés

3. **Nettoyage** : Supprimer régulièrement les anciens chunks
   ```bash
   # Trouver les chunks orphelins (>7 jours)
   find storage/ -name "*.chunk*" -mtime +7 -delete
   ```

4. **Seuil de fragmentation** : Ajustez selon vos besoins
   ```python
   # Pour fragmenter à partir de 500 MB
   FRAGMENTATION_THRESHOLD = 500 * 1024 * 1024
   ```

---

## 🔍 Dépannage

### HA : Les serveurs ne se découvrent pas

**Problème** : Serveurs sur des sous-réseaux différents
```bash
# Vérifier le broadcast
ip route | grep broadcast

# Solution : Utiliser le mode unicast (à implémenter)
python server/main.py --ha --peers 192.168.1.10,192.168.1.20
```

### Fragmentation : Chunks manquants

**Problème** : Un PC avec des chunks est déconnecté
```bash
# Vérifier les chunks disponibles
PC2> check bigfile.bin

# Sortie :
Chunks disponibles : 8/10
Chunks manquants : [3, 7]
Chunks disponibles sur d'autres PCs :
  Chunk 3 : PC1 (redondance)
  Chunk 7 : PC3 (redondance)
  
# Récupérer depuis la redondance
PC2> fetch-chunks bigfile.bin
[OK] Chunk 3 récupéré depuis PC1
[OK] Chunk 7 récupéré depuis PC3
```

---

## 📚 Références Techniques

- **Algorithme d'élection** : Bully Algorithm (priorité-based)
- **Protocole de découverte** : UDP Broadcast multicast
- **Hashing** : SHA-256 pour intégrité
- **Distribution** : Round-robin avec redondance
- **Format métadonnées** : JSON

---

## 🚀 Prochaines Étapes

Fonctionnalités futures possibles :
- [ ] Compression des chunks (zlib, lz4)
- [ ] Chiffrement des chunks (AES-256)
- [ ] Interface web pour monitoring HA
- [ ] Réparation automatique des chunks corrompus
- [ ] Support du protocole Raft pour consensus distribué
- [ ] Métriques et statistiques avancées

---

**Auteurs** : Équipe Réseau de Partage P2P
**Version** : 2.0.0
**Date** : Février 2026
