# Tests Complets - Réseau P2P Local avec HA

## Configuration de Test

### Matériel Nécessaire
- **Option 1** : 3 PCs/laptops sur le même réseau local
- **Option 2** : 1 PC avec 3 terminaux (tests basiques uniquement)
- **Option 3** : 3 VMs avec réseau bridgé

### Prérequis Réseau
- Tous les nœuds sur le même sous-réseau (ex: 192.168.1.x)
- Port UDP 5555 accessible (pare-feu désactivé ou règle autorisée)
- Port TCP 5000 accessible

## Phase 1 : Tests de Base

### Test 1.1 : Démarrage Serveur Seul

**Objectif** : Vérifier qu'un serveur seul devient primaire

**Procédure** :
1. Sur PC1 :
```bash
python launcher.py --mode server --name PC1
```

**Résultat Attendu** :
```
===========================================
RÉSEAU P2P LOCAL AVEC HAUTE DISPONIBILITÉ
===========================================
Nom du nœud : PC1
Rôle : serveur
Port : 5000
Base de données : /path/to/network.db
En attente de découverte...
Rôle : PRIMAIRE  <--- IMPORTANT
Serveurs dans le réseau : 1
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Validation** :
```bash
curl http://localhost:5000/api/ha/status
```
Doit retourner :
```json
{
  "ha_enabled": true,
  "role": "primary",
  "servers_count": 1,
  "servers": [
    {"name": "PC1", "ip": "192.168.1.x", "port": 5000, "priority": xxx}
  ]
}
```

### Test 1.2 : Ajout d'un Serveur Secondaire

**Objectif** : Vérifier l'élection automatique et la synchronisation

**Procédure** :
1. PC1 toujours actif (primaire)
2. Sur PC2 :
```bash
python launcher.py --mode server --name PC2
```

**Résultat Attendu sur PC2** :
```
Rôle : SECONDAIRE  <--- PC2 doit être secondaire car PC1 < PC2 alphabétiquement
Serveurs dans le réseau : 2
```

**Résultat Attendu sur PC1** :
```
Serveur découvert : PC2 @ 192.168.1.y:5000
```

**Validation** :
```bash
# Sur PC2
curl http://localhost:5000/api/ha/status
```
Doit montrer `"role": "secondary"` et 2 serveurs

**Test de Synchronisation** :
1. Sur PC1 (primaire), uploadez un fichier via web ou API
2. Attendez 60 secondes (intervalle de sync)
3. Sur PC2, vérifiez :
```bash
curl http://localhost:5000/api/files
```
Le fichier doit apparaître !

### Test 1.3 : Connexion d'un Client

**Objectif** : Vérifier que le client trouve le primaire

**Procédure** :
1. PC1 (primaire) et PC2 (secondaire) actifs
2. Sur PC3 :
```bash
python launcher.py --mode client --name PC3
```

**Résultat Attendu** :
```
=== Serveurs Disponibles ===
[PRIMAIRE] PC1 @ 192.168.1.x:5000 (priorité: xxx)
            PC2 @ 192.168.1.y:5000 (priorité: yyy)

Connexion au serveur primaire : PC1 (192.168.1.x:5000)
Ouverture du navigateur...
```

**Validation** :
- Le navigateur s'ouvre sur http://192.168.1.x:5000/web
- L'interface affiche la liste des pairs (PC1, PC2, PC3)

## Phase 2 : Tests de Basculement (Failover)

### Test 2.1 : Panne du Primaire

**Objectif** : Vérifier que le secondaire devient primaire

**Configuration Initiale** :
- PC1 : primaire
- PC2 : secondaire
- PC3 : client connecté à PC1

**Procédure** :
1. Arrêtez PC1 avec Ctrl+C
2. Observez les logs de PC2

**Résultat Attendu sur PC2** :
```
[2024-01-15 10:30:15] Échec de connexion au primaire
[2024-01-15 10:30:25] Changement de rôle : secondary → primary
Rôle : PRIMAIRE
```

**Délai Attendu** : Maximum 15 secondes (timeout + cleanup)

**Validation** :
```bash
# Sur PC2, doit maintenant retourner primary
curl http://localhost:5000/api/ha/status
```

**Test de Continuité** :
1. Uploadez un nouveau fichier sur PC2 (maintenant primaire)
2. Vérifiez qu'il est accessible
3. Le client PC3 devrait pouvoir se reconnecter à PC2

### Test 2.2 : Retour du Serveur Défaillant

**Objectif** : Vérifier que l'ancien primaire devient secondaire

**Configuration Initiale** :
- PC1 : arrêté
- PC2 : primaire (suite au failover)

**Procédure** :
1. Redémarrez PC1 :
```bash
python launcher.py --mode server --name PC1
```

**Résultat Attendu sur PC1** :
```
Serveur découvert : PC2 @ 192.168.1.y:5000
Rôle : PRIMAIRE  <--- PC1 redevient primaire car priorité plus élevée!
```

**ATTENTION** : Dans l'implémentation actuelle, PC1 redevient primaire car la priorité est statique (ordre alphabétique). Pour éviter ce comportement (sticky primary), il faudrait modifier `_calculate_priority()` pour tenir compte du temps d'activité.

**Alternative** : Si vous voulez que PC2 reste primaire :
- Modifiez `discovery.py` ligne ~85
```python
def _calculate_priority(self, name: str) -> int:
    # Priorité basée sur le temps de démarrage (pas juste le nom)
    return int(time.time() * 1000) - (ord(name[0]) * 100)
```

### Test 2.3 : Panne Simultanée des Deux Serveurs

**Objectif** : Vérifier la récupération totale

**Procédure** :
1. Arrêtez PC1 et PC2 simultanément
2. Attendez 1 minute
3. Redémarrez PC2, puis PC1

**Résultat Attendu** :
- PC2 démarre → primaire (seul serveur)
- PC1 démarre → devient secondaire ou primaire selon ordre

**Validation** :
- Les données uploadées avant l'arrêt doivent être préservées (DB SQLite persistante)

## Phase 3 : Tests de Synchronisation

### Test 3.1 : Synchronisation Base de Données

**Procédure** :
1. PC1 primaire, PC2 secondaire
2. Sur PC1 (via API) :
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name": "TestPeer", "role": "client"}'
```
3. Attendez 60 secondes (intervalle de sync)
4. Sur PC2 :
```bash
curl http://localhost:5000/api/peers
```

**Résultat Attendu** :
Le peer "TestPeer" doit apparaître sur PC2

### Test 3.2 : Délai de Synchronisation

**Objectif** : Mesurer le temps de sync

**Procédure** :
1. Uploadez un fichier sur PC1 à 10:00:00
2. Vérifiez sur PC2 toutes les 10 secondes
3. Notez le moment où le fichier apparaît

**Résultat Attendu** :
- Première sync : 0-60 secondes (selon le cycle)
- Syncs suivantes : toutes les 60 secondes

### Test 3.3 : Conflit de Synchronisation

**Objectif** : Vérifier que le primaire a toujours raison

**Procédure** :
1. PC1 primaire avec fichier A
2. Arrêtez PC1
3. PC2 devient primaire, uploadez fichier B
4. Redémarrez PC1

**Résultat Attendu** :
- PC1 devient secondaire
- PC1 synchronise avec PC2
- PC1 obtient le fichier B
- Le fichier A est perdu (sauf si également présent sur PC2)

**Note** : C'est une limitation de l'architecture. Pour éviter les pertes, il faudrait une réplication bidirectionnelle ou un système de versioning.

## Phase 4 : Tests de Charge

### Test 4.1 : Uploads Multiples

**Procédure** :
```bash
for i in {1..10}; do
  echo "Test $i" > file$i.txt
  curl -X POST -F "file=@file$i.txt" http://localhost:5000/api/file/upload
done
```

**Validation** :
```bash
curl http://localhost:5000/api/files | python -m json.tool
```
Doit lister 10 fichiers

### Test 4.2 : Clients Simultanés

**Procédure** :
1. Lancez 5 clients en parallèle
2. Chaque client upload un fichier unique
3. Vérifiez que tous les fichiers sont enregistrés

**Commandes** :
```bash
# Terminal 1-5
python launcher.py --mode client --name Client1 &
python launcher.py --mode client --name Client2 &
python launcher.py --mode client --name Client3 &
python launcher.py --mode client --name Client4 &
python launcher.py --mode client --name Client5 &
```

## Phase 5 : Tests d'Edge Cases

### Test 5.1 : Réseau Fragmenté (Split-Brain)

**Configuration** :
- PC1 : 192.168.1.10
- PC2 : 192.168.1.11
- Bloquer le trafic entre PC1 et PC2 (iptables ou firewall)

**Résultat Attendu** :
- PC1 et PC2 deviennent TOUS DEUX primaires (split-brain)
- Chaque segment du réseau a son propre primaire
- **Limitation connue** : Pas de quorum, donc pas de protection contre split-brain

### Test 5.2 : Démarrage Simultané

**Procédure** :
1. Lancez PC1, PC2, PC3 exactement en même temps (script)
```bash
python launcher.py --mode server --name PC1 &
python launcher.py --mode server --name PC2 &
python launcher.py --mode server --name PC3 &
```

**Résultat Attendu** :
- Après 2-3 secondes, l'élection converge
- Le serveur avec le nom alphabétiquement premier devient primaire

### Test 5.3 : Port Déjà Utilisé

**Procédure** :
1. Lancez PC1 sur port 5000
2. Lancez PC2 sur le même PC (port 5000 déjà occupé)

**Résultat Attendu** :
```
OSError: [Errno 98] Address already in use
```

**Solution** : Modifier `SERVER_PORT` dans `config_local.py` ou utiliser des PCs différents

## Phase 6 : Tests de Performance

### Test 6.1 : Taille de Fichier

**Procédure** :
```bash
# Créer un fichier de 100 MB
dd if=/dev/urandom of=large.bin bs=1M count=100

# Uploader
time curl -X POST -F "file=@large.bin" http://localhost:5000/api/file/upload
```

**Validation** :
- Upload réussi
- Temps mesuré
- Fichier synchronisé sur secondaire dans les 60s

### Test 6.2 : Nombre de Fichiers

**Procédure** :
```bash
# Créer 1000 petits fichiers
for i in {1..1000}; do
  echo "File $i" > f$i.txt
  curl -X POST -F "file=@f$i.txt" http://localhost:5000/api/file/upload &
done
wait
```

**Validation** :
```bash
curl http://localhost:5000/api/files | python -m json.tool | grep name | wc -l
```
Doit retourner 1000

## Métriques de Succès

| Test | Critère | Valeur Attendue |
|------|---------|----------------|
| Élection primaire | Temps | < 3 secondes |
| Failover | Temps de détection | < 15 secondes |
| Synchronisation DB | Intervalle | 60 secondes |
| Upload 1 MB | Temps | < 1 seconde (LAN) |
| Upload 100 MB | Temps | < 10 secondes (LAN) |
| Découverte réseau | Temps | < 3 secondes |

## Logs Utiles

### Activer les logs détaillés
Modifiez `config_local.py` :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Surveiller en temps réel
```bash
# État HA
watch -n 1 'curl -s http://localhost:5000/api/ha/status | python -m json.tool'

# Peers actifs
watch -n 2 'curl -s http://localhost:5000/api/peers | python -m json.tool'

# Santé serveur
watch -n 1 'curl -s http://localhost:5000/api/health'
```

## Troubleshooting

### Problème : Secondaire ne synchronise pas

**Symptômes** :
```
Erreur lors de la synchronisation avec le primaire
```

**Causes Possibles** :
1. Le primaire est arrêté
2. Firewall bloque le port 5000
3. Le secondaire pense qu'il est primaire (split-brain)

**Solution** :
```bash
# Vérifier l'état du primaire
curl http://IP_PRIMAIRE:5000/api/health

# Vérifier le rôle du secondaire
curl http://localhost:5000/api/ha/status
```

### Problème : Plusieurs primaires

**Symptômes** :
```bash
curl PC1:5000/api/ha/status → "role": "primary"
curl PC2:5000/api/ha/status → "role": "primary"
```

**Cause** : Split-brain (réseau fragmenté)

**Solution** :
- Vérifier que PC1 et PC2 se voient : `ping IP_AUTRE_PC`
- Redémarrer tous les serveurs

### Problème : Client ne trouve pas de serveur

**Symptômes** :
```
Aucun serveur découvert après 3 secondes
```

**Causes** :
1. Aucun serveur actif
2. Firewall bloque UDP 5555
3. Pas sur le même réseau

**Solution** :
```bash
# Tester UDP manuellement
nc -u -l 5555  # Sur PC1
echo "test" | nc -u PC1_IP 5555  # Sur PC2
```

## Conclusion

Ces tests couvrent :
- ✅ Fonctionnement basique (démarrage, découverte)
- ✅ Haute disponibilité (failover, élection)
- ✅ Synchronisation (DB, heartbeat)
- ✅ Performance (uploads multiples, gros fichiers)
- ✅ Edge cases (split-brain, démarrage simultané)

Pour un environnement de production :
- Implémenter quorum (minimum 3 serveurs)
- Ajouter chiffrement SSL/TLS
- Logger dans des fichiers (pas stdout)
- Monitorer avec Prometheus/Grafana
- Ajouter tests automatisés (pytest)
