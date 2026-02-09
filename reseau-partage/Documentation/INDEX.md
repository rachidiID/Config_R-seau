# 📖 Index de la Documentation - Réseau P2P v2.0

## 🎯 Par Niveau d'Utilisation

### Débutant - Je découvre le projet
1. **[README.md](README.md)** - Vue d'ensemble et installation
2. **[QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md)** - Démarrage rapide (5-15 min)
3. **[demo_advanced.py](demo_advanced.py)** - Démonstrations interactives

### Intermédiaire - Je veux comprendre
1. **[RESUME_V2.md](RESUME_V2.md)** - Résumé des fonctionnalités v2.0
2. **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Documentation technique complète
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Diagrammes et architecture

### Avancé - Je veux développer
1. **[shared/fragmentation.py](shared/fragmentation.py)** - Code source fragmentation
2. **[shared/high_availability.py](shared/high_availability.py)** - Code source HA
3. **[server/main.py](server/main.py)** - Code serveur

---

## 📚 Par Fonctionnalité

### Haute Disponibilité (HA)
- **Documentation** : [ADVANCED_FEATURES.md § Haute Disponibilité](ADVANCED_FEATURES.md#1-haute-disponibilité-multi-serveurs)
- **Guide rapide** : [QUICKSTART_ADVANCED.md § Mode HA](QUICKSTART_ADVANCED.md#-mode-haute-disponibilité-3-minutes)
- **Architecture** : [ARCHITECTURE.md § Architecture HA](ARCHITECTURE.md#architecture-haute-disponibilité-ha)
- **Code source** : [shared/high_availability.py](shared/high_availability.py)
- **Démo** : `python demo_advanced.py` → Option 2

### Fragmentation de Fichiers
- **Documentation** : [ADVANCED_FEATURES.md § Fragmentation](ADVANCED_FEATURES.md#2-fragmentation-de-fichiers-1gb)
- **Guide rapide** : [QUICKSTART_ADVANCED.md § Mode Fragmentation](QUICKSTART_ADVANCED.md#-mode-fragmentation-5-minutes)
- **Architecture** : [ARCHITECTURE.md § Architecture Fragmentation](ARCHITECTURE.md#architecture-fragmentation-de-fichiers)
- **Code source** : [shared/fragmentation.py](shared/fragmentation.py)
- **Démo** : `python demo_advanced.py` → Option 1

### Interface Web
- **Documentation** : [WEB_INTERFACE.md](WEB_INTERFACE.md)
- **Guide** : [GUIDE_WEB.md](GUIDE_WEB.md)
- **Code source** : [web/](web/)

---

## 🔍 Par Type de Document

### Guides Pratiques
| Document | Description | Temps de lecture |
|----------|-------------|------------------|
| [QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md) | Démarrage rapide v2.0 | 5 min |
| [GUIDE_WEB.md](GUIDE_WEB.md) | Guide interface web | 10 min |
| [SCENARIOS.md](SCENARIOS.md) | Scénarios d'utilisation | 15 min |

### Documentation Technique
| Document | Description | Temps de lecture |
|----------|-------------|------------------|
| [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) | Fonctionnalités avancées complètes | 30 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture système détaillée | 20 min |
| [RESUME_V2.md](RESUME_V2.md) | Résumé version 2.0 | 10 min |

### Documentation Projet
| Document | Description | Temps de lecture |
|----------|-------------|------------------|
| [README.md](README.md) | Vue d'ensemble projet | 5 min |
| [PROJET_CREE.md](PROJET_CREE.md) | Historique du projet | 15 min |
| [TESTS_PHASE2.md](TESTS_PHASE2.md) | Tests et validation | 10 min |

### Code et Scripts
| Fichier | Description | Lignes |
|---------|-------------|--------|
| [demo_advanced.py](demo_advanced.py) | Script de démonstration | 340 |
| [shared/fragmentation.py](shared/fragmentation.py) | Module fragmentation | 349 |
| [shared/high_availability.py](shared/high_availability.py) | Module HA | 292 |

---

## 🎓 Parcours d'Apprentissage Recommandés

### Parcours 1 : Utilisateur Final (1 heure)
```
1. README.md (5 min)
   ↓
2. QUICKSTART_ADVANCED.md (15 min)
   ↓
3. python demo_advanced.py (15 min)
   ↓
4. Tests pratiques (25 min)
```

### Parcours 2 : Administrateur Système (2 heures)
```
1. README.md (5 min)
   ↓
2. QUICKSTART_ADVANCED.md (15 min)
   ↓
3. ADVANCED_FEATURES.md (30 min)
   ↓
4. ARCHITECTURE.md (20 min)
   ↓
5. Tests HA complets (30 min)
   ↓
6. Tests Fragmentation (20 min)
```

### Parcours 3 : Développeur (4 heures)
```
1. README.md (5 min)
   ↓
2. ARCHITECTURE.md (30 min)
   ↓
3. ADVANCED_FEATURES.md (45 min)
   ↓
4. shared/fragmentation.py (30 min)
   ↓
5. shared/high_availability.py (30 min)
   ↓
6. Tests et modifications (90 min)
```

---

## 🚀 Commandes Rapides

### Lancer une Démo
```bash
python demo_advanced.py
```

### Test HA Minimal
```bash
# Terminal 1
python server/main.py --ha --name S1 --priority 3

# Terminal 2
python server/main.py --ha --name S2 --priority 2 --port 5001

# Terminal 3
python client/main.py --name PC1 --auto-discover
```

### Test Fragmentation Minimal
```bash
# Créer fichier test 1GB
dd if=/dev/urandom of=test1gb.bin bs=1M count=1024

# Démarrer réseau
python server/main.py &
python client/main.py --name PC1 &
python client/main.py --name PC2 &

# Dans PC1
send test1gb.bin PC2
```

---

## 📞 Besoin d'Aide ?

### Par Sujet
- **Installation** → [README.md § Installation](README.md#-installation)
- **Première utilisation** → [QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md)
- **Configuration** → [ADVANCED_FEATURES.md § Configuration](ADVANCED_FEATURES.md#configuration)
- **Dépannage** → [ADVANCED_FEATURES.md § Dépannage](ADVANCED_FEATURES.md#-dépannage)
- **Architecture** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **API** → [ADVANCED_FEATURES.md § API](ADVANCED_FEATURES.md#api-fragmentation)

### Par Problème
- **Serveurs ne communiquent pas** → [QUICKSTART_ADVANCED.md § Dépannage](QUICKSTART_ADVANCED.md#-dépannage-rapide)
- **Chunks manquants** → [ADVANCED_FEATURES.md § Dépannage Fragmentation](ADVANCED_FEATURES.md#fragmentation--chunks-manquants)
- **Interface web ne marche pas** → [GUIDE_WEB.md](GUIDE_WEB.md)

---

## 📊 Statistiques du Projet

- **Version actuelle** : 2.0.0
- **Date de création** : 2025
- **Dernière mise à jour** : Février 2026
- **Lignes de code** : ~3500
- **Lignes de documentation** : ~2500
- **Modules Python** : 12
- **Fichiers de documentation** : 11

---

## 🔄 Mises à Jour

### Version 2.0.0 (Février 2026)
- ✅ Haute disponibilité (multi-serveurs)
- ✅ Fragmentation de fichiers (>1GB)
- ✅ Documentation complète
- ✅ Script de démonstration

### Version 1.0.0 (2025)
- ✅ Transferts P2P basiques
- ✅ Interface CLI
- ✅ Interface Web
- ✅ Gestion des permissions

---

## 📝 Notes

- Tous les chemins sont relatifs au dossier `reseau-partage/`
- Les commandes supposent Python 3.8+
- Les tests nécessitent plusieurs terminaux simultanés
- La documentation est en français

---

**Dernière mise à jour** : Février 2026
**Mainteneur** : Équipe Réseau P2P
