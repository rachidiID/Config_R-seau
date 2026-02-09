# 🏗️ Architecture du Système

## Vue d'ensemble globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                   RÉSEAU P2P HAUTE DISPONIBILITÉ                    │
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Serveur 1     │◄──►│   Serveur 2     │◄──►│   Serveur 3     │ │
│  │   (Primary)     │    │  (Secondary)    │    │  (Secondary)    │ │
│  │   Priorité: 3   │    │   Priorité: 2   │    │   Priorité: 1   │ │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘ │
│           │                      │                      │           │
│           │  UDP Heartbeats (5s) + DB Sync (30s)        │           │
│           │                      │                      │           │
│  ┌────────▼──────────────────────▼──────────────────────▼────────┐ │
│  │              Clients (découverte automatique)                  │ │
│  │                                                                 │ │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                 │ │
│  │  │ PC1 │  │ PC2 │  │ PC3 │  │ PC4 │  │ PC5 │                 │ │
│  │  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘                 │ │
│  │     │        │        │        │        │                     │ │
│  │     └────────┴────────┴────────┴────────┘                     │ │
│  │              Transferts P2P directs                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Architecture Haute Disponibilité (HA)

### Système de Découverte

```
Serveur 1                  Serveur 2                  Serveur 3
    │                         │                         │
    │  HEARTBEAT (UDP:5555)   │                         │
    ├────────────────────────►│                         │
    │                         │  HEARTBEAT              │
    │                         ├────────────────────────►│
    │  HEARTBEAT              │                         │
    │◄────────────────────────┤                         │
    │                         │  HEARTBEAT              │
    │                         │◄────────────────────────┤
    │  HEARTBEAT              │                         │
    ├─────────────────────────┼────────────────────────►│
    │                         │                         │
    ▼                         ▼                         ▼
  [Serveurs     ◄───────► [Serveurs    ◄───────►  [Serveurs
   connus]                  connus]                 connus]
   - S2, S3                 - S1, S3                - S1, S2
```

### Processus d'Élection du Primaire

```
Étape 1: Tous les serveurs envoient leurs infos
┌─────────┐
│Server 1 │  Priority: 3
│Server 2 │  Priority: 2
│Server 3 │  Priority: 1
└─────────┘

Étape 2: Tri par priorité (décroissant)
┌─────────┐
│Server 1 │  ← Élu PRIMAIRE
│Server 2 │
│Server 3 │
└─────────┘

Étape 3: En cas de panne du primaire
┌─────────┐
│Server 1 │  ✗ Hors ligne (timeout > 15s)
│Server 2 │  ← Nouveau PRIMAIRE
│Server 3 │
└─────────┘
```

### Synchronisation de Base de Données

```
Serveur Primaire (S1)              Serveurs Secondaires
┌──────────────────┐              ┌──────────────────┐
│                  │              │                  │
│  Base de données │              │  Base de données │
│  ┌────────────┐  │              │  ┌────────────┐  │
│  │  Peers     │  │              │  │  Peers     │  │
│  │  Files     │  │  PULL /30s   │  │  Files     │  │
│  │  Transfers │  ├──────────────►  │  Transfers │  │
│  │  ...       │  │              │  │  ...       │  │
│  └────────────┘  │              │  └────────────┘  │
│                  │              │                  │
└──────────────────┘              └──────────────────┘
                                  (S2, S3)
```

## Architecture Fragmentation de Fichiers

### Processus de Fragmentation

```
Fichier Original (2 GB)
┌────────────────────────────────────────────────────┐
│  bigfile.iso                                       │
│  SHA-256: abc123...                                │
└────────────────────────────────────────────────────┘
                    │
                    │ Seuil > 1 GB
                    │ Fragmentation activée
                    ▼
┌────────────────────────────────────────────────────┐
│         Découpage en chunks de 256 MB              │
└────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    Chunk 0     Chunk 1     Chunk 2    ...  Chunk 7
    256 MB      256 MB      256 MB           256 MB
    Hash: a1    Hash: b2    Hash: c3         Hash: h8
```

### Distribution des Chunks avec Redondance

```
Chunks                PCs Disponibles
                     PC1    PC2    PC3    PC4    PC5

Chunk 0  ───────────► ●      ●
Chunk 1  ───────────►        ●      ●
Chunk 2  ───────────►               ●      ●
Chunk 3  ───────────►                      ●      ●
Chunk 4  ───────────► ●                           ●
Chunk 5  ───────────► ●      ●
Chunk 6  ───────────►        ●      ●
Chunk 7  ───────────►               ●      ●

Redondance: 2 copies par chunk (minimum)
Distribution: Rotation circulaire
```

### Processus de Reconstruction

```
PC2 veut reconstruire bigfile.iso

Étape 1: Charger les métadonnées
┌────────────────────────────────┐
│ bigfile.iso.metadata.json      │
│  - Total chunks: 8             │
│  - Chunk size: 256 MB          │
│  - Original hash: abc123...    │
│  - Chunks: [...]               │
└────────────────────────────────┘

Étape 2: Localiser les chunks
Chunk 0 → disponible sur PC1 ✓
Chunk 1 → disponible localement ✓
Chunk 2 → disponible sur PC3 ✓
...

Étape 3: Téléchargement parallèle
┌────┐ ┌────┐ ┌────┐
│ C0 │ │ C2 │ │ C4 │  ← Depuis PC1
└────┘ └────┘ └────┘
┌────┐ ┌────┐ ┌────┐
│ C1 │ │ C5 │ │ C7 │  ← Depuis local/cache
└────┘ └────┘ └────┘
┌────┐ ┌────┐
│ C3 │ │ C6 │         ← Depuis PC3
└────┘ └────┘

Étape 4: Reconstruction
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ C0 │ C1 │ C2 │ C3 │ C4 │ C5 │ C6 │ C7 │
└────┴────┴────┴────┴────┴────┴────┴────┘
                    │
                    ▼
        Vérification hash SHA-256
                    │
                    ▼
        ┌────────────────────┐
        │  bigfile.iso       │ ✓
        │  Intégrité OK      │
        └────────────────────┘
```

## Flux de Données Complet

### Scénario : PC1 envoie 2GB à PC2 (avec HA + Fragmentation)

```
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 1 : Connexion au réseau                                    │
└──────────────────────────────────────────────────────────────────┘

PC1 ──[Découverte]──► Serveur 1, 2, 3
                      │
                      ▼
                   Serveur 1 (Primary)
                      │
PC1 ◄─[Connexion]─────┘


┌──────────────────────────────────────────────────────────────────┐
│ PHASE 2 : Initiation du transfert                                │
└──────────────────────────────────────────────────────────────────┘

PC1: send bigfile.dat PC2
    │
    ├─► Détection: 2 GB > 1 GB → Fragmentation
    │
    ├─► Calcul hash original: SHA-256
    │
    └─► Fragmentation: 8 chunks × 256 MB


┌──────────────────────────────────────────────────────────────────┐
│ PHASE 3 : Distribution des chunks                                │
└──────────────────────────────────────────────────────────────────┘

PC1 ──[Métadonnées]──► Serveur 1 (Primary)
                       │
                       ├─► Enregistrement DB
                       ├─► Calcul distribution
                       │   (PC2, PC3, PC4, PC5)
                       │
PC1 ◄──[Distribution]──┘

PC1 ──[Chunk 0]──► PC2, PC3
PC1 ──[Chunk 1]──► PC3, PC4
PC1 ──[Chunk 2]──► PC4, PC5
...


┌──────────────────────────────────────────────────────────────────┐
│ PHASE 4 : Panne du serveur primaire                              │
└──────────────────────────────────────────────────────────────────┘

Serveur 1 ✗ PANNE
    │
    ▼ (15 secondes)
Serveur 2 détecte timeout
    │
    ▼
Élection automatique
    │
    ▼
Serveur 2 devient Primary


┌──────────────────────────────────────────────────────────────────┐
│ PHASE 5 : Reconstruction par PC2                                 │
└──────────────────────────────────────────────────────────────────┘

PC2 ──[Requête métadonnées]──► Serveur 2 (nouveau Primary)
                               │
PC2 ◄──[Métadonnées + Map]────┘

PC2 télécharge chunks:
    ├─► Chunk 0 depuis local
    ├─► Chunk 1 depuis PC3
    ├─► Chunk 2 depuis PC4
    └─► ...

PC2 reconstruit:
    └─► Fichier complet (2 GB)
        └─► Vérification hash ✓
```

## Avantages de l'Architecture

### Résilience

```
Scénario de Panne          Impact              Récupération
─────────────────────────  ──────────────────  ──────────────────
1 serveur tombe            Aucun (basculement) < 15 secondes
2 serveurs tombent         Service dégradé     1 serveur suffit
Tous serveurs tombent      Service arrêté      Redémarrage manuel

1 PC avec chunks tombe     Aucun (redondance)  Immédiat
2+ PCs tombent             Possible si >2 red  Dépend de la red.
```

### Scalabilité

```
Nombre de Serveurs    Capacité            Résilience
───────────────────   ─────────────────   ──────────────────
1                     Baseline            Aucune
2                     Baseline            Panne 1 serveur OK
3                     Baseline            Panne 2 serveurs OK
3+                    Baseline            Haute résilience

Nombre de PCs         Capacité            Distribution
───────────────────   ─────────────────   ──────────────────
1-2                   Limitée             Pas de redondance
3-5                   Moyenne             Redondance x2
5-10                  Élevée              Redondance x2-3
10+                   Très élevée         Redondance x3+
```

## Technologies Utilisées

```
Composant                Technologie          Port/Protocole
────────────────────────────────────────────────────────────
Serveur Web              Flask 3.0            HTTP:5000-5002
Base de données          SQLite 3             Fichier local
Découverte serveurs      UDP Broadcast        UDP:5555
Transferts P2P           TCP Sockets          TCP:5001+
Synchronisation DB       HTTP REST            HTTP:5000/api
Heartbeats               UDP Broadcast        UDP:5555
Fragmentation            Fichiers locaux      -
Hashing                  SHA-256/MD5          -
```

## Métriques et Performance

### Temps de Basculement (HA)

```
Événement                      Temps
───────────────────────────────────────────────
Détection panne serveur        5-15 secondes
Élection nouveau primaire      < 1 seconde
Synchronisation DB             0-30 secondes
Total temps de basculement     < 20 secondes
```

### Performance Fragmentation

```
Taille Fichier    Chunks    Distribution    Reconstruction
──────────────────────────────────────────────────────────────
1 GB              4         ~2 secondes     ~5 secondes
2 GB              8         ~4 secondes     ~10 secondes
5 GB              20        ~10 secondes    ~25 secondes
10 GB             40        ~20 secondes    ~50 secondes
```

### Overhead

```
Fonctionnalité            Overhead CPU    Overhead Réseau    Overhead Disque
─────────────────────────────────────────────────────────────────────────────
HA Heartbeats             < 1%            ~10 KB/s           Négligeable
DB Synchronisation        < 5%            ~100 KB/30s        Négligeable
Fragmentation             5-10%           Aucun              2x (redondance)
Reconstruction            10-15%          Variable           Temporaire
```

---

**Version** : 2.0.0  
**Dernière mise à jour** : Février 2026
