#  Démarrage Rapide - Réseau de Partage P2P

## Installation (1 fois)

```bash
cd reseau-partage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test Local (Simuler 3 PC)

### Terminal 1 - Serveur
```bash
cd reseau-partage
source venv/bin/activate
python server/main.py
```

Résultat attendu :
```
==================================================
 SERVEUR DE PARTAGE P2P
==================================================
Host: 0.0.0.0
Port: 5000
...
✓ Base de données initialisée
```

### Terminal 2 - PC1
```bash
cd reseau-partage
source venv/bin/activate
python client/main.py --name PC1 --port 5001
```

### Terminal 3 - PC2
```bash
cd reseau-partage
source venv/bin/activate
python client/main.py --name PC2 --port 5002
```

### Terminal 4 - PC3
```bash
cd reseau-partage
source venv/bin/activate
python client/main.py --name PC3 --port 5003
```

## Commandes de Test

### Sur PC1 : Voir les autres PC
```
PC1> list
```

### Sur PC1 : Créer un fichier de test
```bash
# Dans un autre terminal
echo "Bonjour depuis PC1" > test.txt
```

### Sur PC1 : Envoyer à PC2 uniquement (PRIVÉ)
```
PC1> send test.txt PC2
```

### Sur PC2 : Vérifier réception
```
PC2> received
```

### Sur PC1 : Envoyer à tout le monde (PUBLIC)
```
PC1> send test.txt *
```

### Sur PC1 : Envoyer à PC2 et PC3 (PARTAGÉ)
```
PC1> send test.txt PC2 PC3
```

## Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `list` | Voir les PC connectés |
| `send <fichier> <dest>` | Envoyer un fichier |
| `received` | Voir les fichiers reçus |
| `status` | Statut du serveur |
| `help` | Aide |
| `quit` | Quitter |

## Exemples Complets

### Scénario 1 : Envoi Privé
```
PC1> send rapport.pdf PC2
  → Seul PC2 reçoit le fichier
```

### Scénario 2 : Envoi Partagé
```
PC1> send presentation.pptx PC2 PC3
  → PC2 et PC3 reçoivent, PC4 ne voit rien
```

### Scénario 3 : Envoi Public
```
PC1> send annonce.txt *
  → Tous les PC en ligne reçoivent
```

## Structure des Dossiers

```
reseau-partage/
├── storage/          # Fichiers reçus par chaque PC
│   ├── PC1/         # Fichiers reçus par PC1
│   ├── PC2/         # Fichiers reçus par PC2
│   └── PC3/         # Fichiers reçus par PC3
└── server/
    └── network.db   # Base de données SQLite
```

## Vérifier les Fichiers Reçus

```bash
# Voir les fichiers reçus par PC2
ls -lh storage/PC2/

# Lire un fichier reçu
cat storage/PC2/test.txt
```

## Arrêter Tout

- Ctrl+C dans chaque terminal
- Ou taper `quit` dans chaque client


