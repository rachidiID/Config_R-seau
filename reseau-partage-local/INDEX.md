# 📋 INDEX - Documentation Complète

## 🚀 Démarrage Rapide

**Vous êtes pressé ?** Lisez dans cet ordre :
1. [README.md](README.md) - Vue d'ensemble (2 min)
2. [Doc/QUICKSTART.md](Doc/QUICKSTART.md) - Démarrage en 5 min
3. Lancez `./test_demo.sh` pour tester

## 📚 Documentation par Objectif

### Je veux comprendre le projet
- [README.md](README.md) - Introduction et architecture
- [RESUME.md](RESUME.md) - Résumé complet avec checklist
- [Doc/COMPARAISON.md](Doc/COMPARAISON.md) - Cloud vs Local détaillé

### Je veux installer et tester
- [Doc/QUICKSTART.md](Doc/QUICKSTART.md) - Installation et premiers tests
- [verify.sh](verify.sh) - Script de vérification (lance avec `./verify.sh`)
- [test_demo.sh](test_demo.sh) - Démo automatique (lance avec `./test_demo.sh`)

### Je veux tester en profondeur
- [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) - 30+ scénarios de test
  * Tests de base (démarrage, découverte)
  * Tests de failover (panne serveur)
  * Tests de synchronisation
  * Tests de performance
  * Tests d'edge cases

### Je veux comprendre les changements
- [CHANGELOG.md](CHANGELOG.md) - Historique des fonctionnalités
  * Nouvelles features
  * Modifications techniques
  * Limitations connues
  * Roadmap future

### Je veux comparer avec la version cloud
- [Doc/COMPARAISON.md](Doc/COMPARAISON.md) - Comparaison détaillée
  * Architectures différentes
  * Fonctionnalités
  * Performance
  * Cas d'usage
  * Migration entre versions

## 📁 Structure des Fichiers

```
reseau-partage-local/
│
├── 📄 Documentation (lisez-moi en premier)
│   ├── README.md                    ← Commencez ici !
│   ├── RESUME.md                    ← Vue d'ensemble complète
│   ├── CHANGELOG.md                 ← Historique
│   ├── INDEX.md                     ← Ce fichier
│   └── Doc/
│       ├── QUICKSTART.md            ← Guide 5 minutes
│       ├── TESTS_COMPLETS.md        ← 30+ scénarios de test
│       └── COMPARAISON.md           ← Cloud vs Local
│
├── 🔧 Fichiers Core Python
│   ├── launcher.py                  ← Point d'entrée (CLI)
│   ├── server_local.py              ← Serveur Flask avec HA
│   ├── discovery.py                 ← Découverte UDP
│   ├── ha_manager.py                ← Gestion HA
│   ├── database.py                  ← SQLite avec sync
│   └── config_local.py              ← Configuration
│
├── 🌐 Interface Web
│   └── web/
│       ├── templates/
│       │   ├── index.html           ← Page principale
│       │   └── login.html           ← Page connexion
│       └── static/
│           ├── app.js               ← JavaScript
│           └── style.css            ← Styles
│
├── 🧪 Scripts de Test
│   ├── test_demo.sh                 ← Démo automatique (3 nœuds)
│   └── verify.sh                    ← Vérification projet
│
├── ⚙️ Configuration
│   ├── requirements.txt             ← Dépendances Python
│   └── .gitignore                   ← Exclusions git
│
└── 📦 Généré à l'exécution
    ├── venv/                        ← Environnement virtuel (créé par vous)
    ├── network.db                   ← Base de données (créée au runtime)
    └── storage/                     ← Fichiers uploadés (créé au runtime)
```

## 🎯 Guides par Scénario

### Scénario 1 : Premier Test (1 PC)
**Objectif** : Tester rapidement sur une seule machine

**Étapes** :
1. Lisez [Doc/QUICKSTART.md](Doc/QUICKSTART.md) section "Test sur un seul PC"
2. Installez les dépendances : `pip install -r requirements.txt`
3. Lancez : `./test_demo.sh`
4. 3 terminaux s'ouvrent (2 serveurs + 1 client)

**Durée** : 5 minutes

---

### Scénario 2 : Test Réseau Local (3 PCs)
**Objectif** : Tester sur vrai réseau avec redondance

**Étapes** :
1. Lisez [Doc/QUICKSTART.md](Doc/QUICKSTART.md) section "Test sur plusieurs PCs"
2. Sur chaque PC, copiez le dossier `reseau-partage-local/`
3. PC1 : `python launcher.py --mode server --name PC1`
4. PC2 : `python launcher.py --mode server --name PC2`
5. PC3 : `python launcher.py --mode client --name PC3`
6. Testez le failover (arrêtez PC1, PC2 devient primaire)

**Durée** : 15 minutes

---

### Scénario 3 : Test de Failover
**Objectif** : Vérifier la haute disponibilité

**Étapes** :
1. Lancez 2 serveurs (PC1 primaire, PC2 secondaire)
2. Uploadez un fichier sur PC1
3. Arrêtez PC1 avec Ctrl+C
4. Attendez 15 secondes
5. Vérifiez que PC2 est devenu primaire : `curl http://localhost:5000/api/ha/status`
6. Vérifiez que le fichier est toujours accessible sur PC2

**Détails** : [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) → Phase 2 : Tests de Basculement

**Durée** : 10 minutes

---

### Scénario 4 : Test de Performance
**Objectif** : Mesurer vitesse upload/download

**Étapes** :
1. Créez un fichier de 100 MB : `dd if=/dev/urandom of=large.bin bs=1M count=100`
2. Uploadez : `time curl -X POST -F "file=@large.bin" http://localhost:5000/api/file/upload`
3. Notez le temps (attendu : < 1 seconde sur gigabit LAN)

**Détails** : [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) → Phase 6 : Tests de Performance

**Durée** : 5 minutes

---

### Scénario 5 : Migration depuis Cloud
**Objectif** : Récupérer données depuis version PythonAnywhere

**Étapes** :
1. Lisez [Doc/COMPARAISON.md](Doc/COMPARAISON.md) → Section "Migration"
2. Exportez DB cloud : `scp Rachidi@ssh.pythonanywhere.com:network.db .`
3. Copiez vers local : `cp network.db reseau-partage-local/`
4. Lancez serveur local : `python launcher.py --mode server --name MonPC`

**Durée** : 10 minutes

## 🔍 Recherche Rapide

### Commandes Utiles
Voir [Doc/QUICKSTART.md](Doc/QUICKSTART.md) → Section "Commandes Utiles"
- `curl http://localhost:5000/api/ha/status` - État HA
- `curl http://localhost:5000/api/peers` - Liste peers
- `curl http://localhost:5000/api/health` - Santé serveur

### Configuration
Voir [config_local.py](config_local.py)
- `DISCOVERY_PORT = 5555` - Port UDP
- `SERVER_PORT = 5000` - Port HTTP
- `SYNC_INTERVAL = 60` - Sync toutes les 60s

### Dépannage
Voir [Doc/QUICKSTART.md](Doc/QUICKSTART.md) → Section "Dépannage"
- "No module named 'flask'" → `pip install -r requirements.txt`
- "Port 5000 déjà utilisé" → `lsof -i :5000` puis `kill -9 <PID>`
- "Aucun serveur découvert" → Vérifier pare-feu (autoriser UDP 5555)

### Limitations
Voir [CHANGELOG.md](CHANGELOG.md) → Section "Limitations Connues"
1. Pas de sync fichiers `storage/` (seulement DB)
2. Split-brain possible (pas de quorum)
3. HTTP non chiffré (OK pour LAN privé)

## 📊 Métriques Clés

| Métrique | Valeur | Source |
|----------|--------|--------|
| **Temps d'élection** | < 3 secondes | [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) |
| **Failover** | < 15 secondes | [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) |
| **Sync DB** | Toutes les 60s | [config_local.py](config_local.py) |
| **Upload LAN** | ~100 MB/s | [Doc/COMPARAISON.md](Doc/COMPARAISON.md) |
| **Latence LAN** | 1-5 ms | [Doc/COMPARAISON.md](Doc/COMPARAISON.md) |

## 🛠️ Maintenance

### Mise à Jour
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Backup Base de Données
```bash
# Sur serveur primaire
curl http://localhost:5000/api/sync/export > backup_$(date +%Y%m%d).db
```

### Monitoring
```bash
# État HA en temps réel
watch -n 1 'curl -s http://localhost:5000/api/ha/status | python -m json.tool'
```

## 🆘 Support

### Problème ? Consultez dans cet ordre :
1. **Vérification** : Lancez `./verify.sh` pour diagnostiquer
2. **Dépannage** : [Doc/QUICKSTART.md](Doc/QUICKSTART.md) → Section "Dépannage"
3. **Tests** : [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md) → Section "Troubleshooting"
4. **Comparaison** : [Doc/COMPARAISON.md](Doc/COMPARAISON.md) si confusion cloud/local

### Questions Fréquentes

**Q : Puis-je utiliser les deux versions (cloud + local) ?**
A : Oui ! Voir [Doc/COMPARAISON.md](Doc/COMPARAISON.md) → "Utilisez les DEUX si"

**Q : Comment tester sans plusieurs PCs ?**
A : Utilisez 3 terminaux : `./test_demo.sh`

**Q : Combien de serveurs minimum ?**
A : Minimum 1, recommandé 2+ pour HA

**Q : Les fichiers sont-ils synchronisés ?**
A : Non, seulement la base de données. Voir [CHANGELOG.md](CHANGELOG.md) → Limitations

**Q : Comment chiffrer les communications ?**
A : Actuellement HTTP uniquement. TLS en roadmap future.

## 🚀 Prochaines Étapes

### Vous avez tout lu ?
1. ✅ Installez les dépendances
2. ✅ Lancez `./test_demo.sh`
3. ✅ Testez le failover (arrêtez PC1)
4. ✅ Uploadez des fichiers
5. ✅ Testez sur vrai réseau (3 PCs)

### Vous voulez contribuer ?
1. Lisez [CHANGELOG.md](CHANGELOG.md) → "Améliorations Futures"
2. Implémentez une feature
3. Testez avec [Doc/TESTS_COMPLETS.md](Doc/TESTS_COMPLETS.md)
4. Pull Request !

## 📝 Checklist Complète

Avant de déployer en production, vérifiez :

- [ ] Tests de base réussis (démarrage, découverte)
- [ ] Tests de failover réussis (<15s)
- [ ] Tests de synchronisation réussis (60s)
- [ ] Tests de performance OK (vitesse LAN)
- [ ] Documentation lue et comprise
- [ ] Pare-feu configuré (UDP 5555 + TCP 5000)
- [ ] Backup DB planifié
- [ ] Monitoring configuré
- [ ] Équipe formée sur les commandes de base

## 🎓 Ressources Externes

### Technologies Utilisées
- **Flask** : https://flask.palletsprojects.com/
- **APScheduler** : https://apscheduler.readthedocs.io/
- **netifaces** : https://pypi.org/project/netifaces/
- **SQLite** : https://www.sqlite.org/

### Concepts
- **UDP Broadcast** : https://en.wikipedia.org/wiki/Broadcasting_(networking)
- **Haute Disponibilité** : https://en.wikipedia.org/wiki/High_availability
- **Primary/Secondary** : https://en.wikipedia.org/wiki/Primary/backup
- **Database Replication** : https://en.wikipedia.org/wiki/Replication_(computing)

---

## 📞 Contact

Pour questions ou bugs :
- Ouvrez une issue sur GitHub
- Consultez d'abord la documentation (vous gagnerez du temps !)

---

**Dernière mise à jour** : 2024-01-15

**Version** : Locale 1.0

**Statut** : ✅ Prêt pour tests

---

*Bonne chance avec votre réseau P2P local ! 🚀*
