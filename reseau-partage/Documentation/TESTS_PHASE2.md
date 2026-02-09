# 🎯 Tests Phase 2 - Guide de Test

## ✅ Tests à effectuer

### Test 1: Transfert de fichier simple (vérifier que ça marche toujours)

**Sur PC1 (serveur déjà lancé)**:
```bash
cd "/home/rachidi/Base_de_données/reseau-partage"
source .venv/bin/activate
python client/main.py --name PC1 --server http://localhost:5000 --port 5001
```

**Sur PC2 (dans un autre terminal)**:
```bash
cd "/home/rachidi/Base_de_données/reseau-partage"
source .venv/bin/activate
python client/main.py --name PC2 --server http://localhost:5000 --port 5002
```

**Commandes sur PC1**:
```bash
PC1> list
# Devrait voir PC2

PC1> send /home/rachidi/test_folder/file1.txt PC2
# Observer la barre de progression tqdm
```

**Résultat attendu**:
- ✅ Barre de progression tqdm s'affiche
- ✅ Transfert réussit
- ✅ PC2 reçoit le fichier avec notification desktop

---

### Test 2: Transfert de dossier complet

**Sur PC1**:
```bash
PC1> send /home/rachidi/test_folder PC2
```

**Résultat attendu**:
```
📦 Préparation de l'envoi:
  Dossier: test_folder
  Taille: XXX B
  Destinataires: PC2
  Permission: private

✅ Dossier enregistré (ID: X)

📦 Compression du dossier 'test_folder'...
✓ Compression terminée: XXX B

📤 Envoi vers PC2...
test_folder: 100%|████████████| XXX/XXX [00:00<00:00, XXX/s]
✓ Dossier envoyé avec succès

✅ Transfert terminé: 1/1 réussis
```

**Sur PC2**:
```
📦 Réception dossier: test_folder de 127.0.0.1
test_folder.zip: 100%|████████| XXX/XXX [00:00<00:00, XXX/s]
⚙️  Décompression...
✓ Dossier reçu: /home/rachidi/.../storage/PC2/test_folder

[Notification desktop apparaît]
📦 Dossier reçu
test_folder
De: PC1
```

**Vérification sur PC2**:
```bash
PC2> received
# Devrait voir:
📬 FICHIERS REÇUS (2):

Type      Nom                            Taille
-----------------------------------------------------
📄 Fichier  file1.txt                    15 B
📁 Dossier  test_folder                  XXX B
```

---

### Test 3: Transfert vers plusieurs PC

**Lancer PC3** (dans un 3ème terminal):
```bash
cd "/home/rachidi/Base_de_données/reseau-partage"
source .venv/bin/activate
python client/main.py --name PC3 --server http://localhost:5000 --port 5003
```

**Sur PC1**:
```bash
PC1> send /home/rachidi/test_folder/file2.txt PC2 PC3
```

**Résultat attendu**:
- ✅ Fichier envoyé à PC2 et PC3
- ✅ Barre de progression pour chaque transfert
- ✅ Notification d'envoi réussi pour chaque PC
- ✅ PC2 et PC3 reçoivent le fichier avec notification

---

### Test 4: Transfert public (à tous)

**Sur PC1**:
```bash
PC1> send /home/rachidi/test_folder/file1.txt *
```

**Résultat attendu**:
```
📢 Envoi public à 2 PC

📦 Préparation de l'envoi:
  Fichier: file1.txt
  Taille: 15 B
  Destinataires: PC2, PC3
  Permission: public

✅ Fichier enregistré (ID: X)

📤 Envoi vers PC2...
file1.txt: 100%|████████████| 15/15 [00:00<00:00, XXX/s]
✓ Fichier envoyé avec succès

📤 Envoi vers PC3...
file1.txt: 100%|████████████| 15/15 [00:00<00:00, XXX/s]
✓ Fichier envoyé avec succès

✅ Transfert terminé: 2/2 réussis
```

---

### Test 5: Vérifier les notifications

**Pendant les tests précédents, vérifier**:

1. **Réception de fichier**:
   - Une notification apparaît sur le bureau du destinataire
   - Titre: "📥 Fichier reçu"
   - Message: nom du fichier + expéditeur

2. **Réception de dossier**:
   - Notification: "📦 Dossier reçu"
   - Message: nom du dossier + expéditeur

3. **Envoi réussi**:
   - Notification sur l'expéditeur
   - Titre: "✅ Fichier envoyé" ou "✅ Dossier envoyé"

**Si les notifications ne fonctionnent pas sur Linux**:
```bash
# Vérifier notify-send
which notify-send

# Installer si nécessaire
sudo apt install libnotify-bin

# Test manuel
notify-send "Test" "Ceci est un test"
```

---

### Test 6: Barre de progression détaillée

**Créer un fichier plus gros pour mieux voir**:
```bash
# Créer un fichier de 10 MB
dd if=/dev/zero of=/tmp/bigfile.bin bs=1M count=10
```

**Sur PC1**:
```bash
PC1> send /tmp/bigfile.bin PC2
```

**Observer**:
- ✅ Pourcentage en temps réel
- ✅ Taille transférée / Taille totale
- ✅ Vitesse (MB/s)
- ✅ Temps écoulé et ETA
- ✅ Barre visuelle

**Exemple d'affichage attendu**:
```
📤 Envoi: bigfile.bin vers 127.0.0.1:5002
bigfile.bin: 67%|█████████▋  | 6.7M/10.0M [00:01<00:00, 4.5MB/s]
```

---

## 🐛 Problèmes possibles et solutions

### Erreur: "ModuleNotFoundError: No module named 'tqdm'"
```bash
source .venv/bin/activate
pip install tqdm
```

### Erreur: "ModuleNotFoundError: No module named 'plyer'"
```bash
source .venv/bin/activate
pip install plyer
```

### Les notifications ne s'affichent pas (Linux)
```bash
# Vérifier notify-send
which notify-send

# Installer
sudo apt install libnotify-bin
```

### Erreur lors de la compression du dossier
- Vérifier les permissions du dossier
- Vérifier l'espace disque disponible dans /tmp

### Le serveur ne démarre pas
```bash
# Vérifier qu'il n'y a pas déjà un serveur lancé
ps aux | grep python | grep server

# Tuer les processus si nécessaire
pkill -f "python.*server/main.py"
```

---

## 📊 Checklist complète

- [ ] Test 1: Transfert fichier simple ✓
- [ ] Test 2: Transfert dossier complet ✓
- [ ] Test 3: Transfert vers plusieurs PC ✓
- [ ] Test 4: Transfert public (*) ✓
- [ ] Test 5: Notifications desktop ✓
- [ ] Test 6: Barre de progression détaillée ✓
- [ ] Vérification: Aucune erreur dans les logs
- [ ] Vérification: Les fichiers/dossiers sont bien reçus
- [ ] Vérification: La commande `received` affiche correctement
- [ ] Vérification: Les types (fichier/dossier) sont distingués

---

## 🎉 Validation finale

**Si tous les tests passent**:
- ✅ Phase 2 complètement fonctionnelle
- ✅ Transfert de dossiers opérationnel
- ✅ Barres de progression améliorées
- ✅ Notifications système actives

**Prochaine étape**: Phase 3 - Sécurité avancée (chiffrement, authentification)

---

**Note**: Le serveur doit être lancé dans un terminal séparé et rester actif pendant tous les tests.
