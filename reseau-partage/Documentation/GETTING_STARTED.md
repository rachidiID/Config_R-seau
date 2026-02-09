# 🚀 Guide de Démarrage - 5 Minutes

## Ce que vous avez maintenant

Votre système de partage P2P a été amélioré avec **2 fonctionnalités majeures** :

### 🔄 Haute Disponibilité
```
Avant: 1 serveur → panne = tout s'arrête ❌
Après: 3+ serveurs → basculement automatique ✅
```

### 📦 Fragmentation de Fichiers  
```
Avant: Fichier 5GB sur 1 PC ❌
Après: 20 chunks de 256MB sur plusieurs PCs ✅
```

## Test Rapide (Choisis ton niveau)

### Niveau 1 : Démo Interactive (2 minutes)
```bash
python demo_advanced.py
# Choisir option 3 (Intégration)
```

### Niveau 2 : Test HA Réel (5 minutes)
```bash
# Terminal 1 (Serveur principal)
python server/main.py --ha --name Server1 --priority 3

# Terminal 2 (Serveur backup)  
python server/main.py --ha --name Server2 --priority 2 --port 5001

# Terminal 3 (Client)
python client/main.py --name PC1 --auto-discover
# Taper: send test.txt PC2

# Dans Terminal 1: Ctrl+C (tuer le serveur)
# Observer: Basculement automatique vers Server2 !
```

### Niveau 3 : Test Fragmentation (10 minutes)
```bash
# Créer fichier test 1.5GB
dd if=/dev/urandom of=bigfile.bin bs=1M count=1536

# Lancer réseau (3 terminaux)
python server/main.py                          # Terminal 1
python client/main.py --name PC1               # Terminal 2  
python client/main.py --name PC2               # Terminal 3

# Dans PC1
send bigfile.bin PC2
# Observer: Fragmentation en 6 chunks + distribution

# Dans PC2
list
reconstruct bigfile.bin
# Observer: Reconstruction automatique !
```

## Documentation

**Pressé ?** → [QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md)
**Curieux ?** → [RESUME_V2.md](RESUME_V2.md)
**Technique ?** → [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
**Architecture ?** → [ARCHITECTURE.md](ARCHITECTURE.md)
**Tout voir ?** → [INDEX.md](INDEX.md)

## Besoin d'Aide ?

```bash
# Voir toutes les commandes
python demo_advanced.py --help

# Tester les modules
python -c "from shared.fragmentation import FileFragmenter; print('OK')"
python -c "from shared.high_availability import ServerDiscovery; print('OK')"
```

## C'est Parti ! 🎉

Tu as maintenant un réseau P2P **production-ready** avec :
- ✅ Zéro temps d'arrêt (HA)
- ✅ Support gros fichiers (Fragmentation)  
- ✅ Redondance automatique
- ✅ Documentation complète

**Go !** → `python demo_advanced.py`
