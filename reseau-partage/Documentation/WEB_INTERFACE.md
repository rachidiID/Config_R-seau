# Interface Web P2P

## Accès à l'interface

1. **Démarrer le serveur:**
```bash
cd ~/Base_de_données/reseau-partage
source venv/bin/activate
python server/main.py
```

2. **Ouvrir l'interface web:**
   - Dans votre navigateur: http://localhost:5000/web
   - Avec paramètres: http://localhost:5000/web?name=PC1&port=5001

## Fonctionnalités

### Envoyer des fichiers
- Glisser-déposer ou cliquer pour sélectionner
- Choisir le destinataire (un PC ou tous)
- Barre de progression en temps réel

### Voir les PC connectés
- Liste en temps réel
- Statut (en ligne/hors ligne)
- Adresse IP et port

### Fichiers reçus
- Liste des fichiers/dossiers reçus
- Taille et type

## Design

- **Interface moderne** avec dégradés et ombres
- **Responsive** - fonctionne sur mobile et desktop  
- **Notifications** visuelles pour chaque action
- **Thème coloré** violet/bleu professionnel
- **Auto-refresh** toutes les 5 secondes

## Utilisation multi-PC

**PC 1:**
```
http://localhost:5000/web?name=PC1&port=5001
```

**PC 2:**
```
http://localhost:5000/web?name=PC2&port=5002
```

**PC 3:**
```
http://localhost:5000/web?name=PC3&port=5003
```

## Compatibilité

- Chrome, Firefox, Safari, Edge
- Desktop et mobile
- Fonctionne avec le CLI en même temps
