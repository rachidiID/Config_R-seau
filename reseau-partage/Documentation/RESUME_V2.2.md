# Résumé des Modifications v2.2

## Ce qui a été fait

### ✅ 1. Statut Online/Offline

**Avant :** Tous les utilisateurs apparaissaient toujours comme "En ligne"

**Maintenant :**
- Les utilisateurs connectés sont **verts** avec "• En ligne"
- Les utilisateurs déconnectés sont **gris** avec "● Hors ligne" (transparents)
- Mise à jour automatique toutes les 5 minutes

**Comment ça marche :**
- Chaque client envoie un "heartbeat" toutes les 2 minutes
- Si pas de heartbeat pendant >5 min → marqué offline
- Si pas de heartbeat pendant >10h → supprimé automatiquement

---

### ✅ 2. Interface nettoyée (sans emojis)

**Supprimé :**
- 🌐 🔄 📁 ⚠️ 👥 📂 📥 📤 ✓ 💡

**Remplacé par du texte clair :**
- Titre : "Réseau de Partage P2P" (au lieu de "🌐 ... v2.0")
- Icônes : [Fichier], [PCs], [REÇU], [ENVOYÉ]
- Boutons : "Télécharger" (au lieu de "📥 Télécharger")

---

### ✅ 3. Architecture expliquée

**Document créé :** [ARCHITECTURE_SERVEUR_CLIENT.md](Documentation/ARCHITECTURE_SERVEUR_CLIENT.md)

**Réponse à votre question :**

#### Qui est serveur ?
- **1 seul serveur** : PythonAnywhere (https://rachidi.pythonanywhere.com)
- Rôle : annuaire, base de données, interface web
- Ne transfère PAS directement les fichiers entre clients

#### Qui est client ?
- **Tous les utilisateurs** qui se connectent via navigateur
- PC1, PC2, PC3, Rachidi, etc.
- N'importe quel ordinateur peut être client

#### Architecture

```
        SERVEUR CENTRAL
      (PythonAnywhere)
              │
    ┌─────────┼─────────┐
    │         │         │
   PC1       PC2       PC3
 (client)  (client)  (client)
```

---

## Déploiement

### 1. Installer la nouvelle dépendance

```bash
cd /home/rachidi/Base_de_données/Config_R-seau/reseau-partage
pip install APScheduler==3.10.4
```

### 2. Commit et push

```bash
git add -A
git commit -m "v2.2: Statut online/offline + nettoyage interface + documentation"
git push
```

### 3. Mise à jour PythonAnywhere

**Console PythonAnywhere :**
```bash
cd ~/Config_R-seau/reseau-partage
git pull origin main
pip install --user APScheduler==3.10.4
```

**Web tab :**
- Cliquer sur le bouton vert "Reload"

---

## Test

### Tester le statut online/offline

1. Connecter PC1 et PC2
2. Fermer l'onglet de PC1
3. Attendre 6 minutes
4. Sur PC2, cliquer "Rafraîchir" (ou attendre auto-refresh)
5. **Résultat attendu :** PC1 apparaît en gris "Hors ligne"

### Tester la suppression automatique

1. Laisser un PC déconnecté pendant >10h
2. Le PC sera automatiquement supprimé de la liste

---

## Fichiers modifiés

```
server/database.py          ← +3 fonctions (heartbeat, cleanup)
server/main.py              ← +1 route /api/heartbeat, +scheduler
web/static/app.js           ← +heartbeat auto, +affichage statut
web/static/style.css        ← +styles online/offline
web/templates/index.html    ← -emojis, -v2.0
web/templates/login.html    ← -emojis, -v2.0
requirements.txt            ← +APScheduler

Documentation/
  ARCHITECTURE_SERVEUR_CLIENT.md    [NOUVEAU]
  MODIFICATIONS_V2.2.md             [NOUVEAU]
  RESUME_V2.2.md                    [CE FICHIER]
```

---

## Documentation

- **Architecture :** [ARCHITECTURE_SERVEUR_CLIENT.md](Documentation/ARCHITECTURE_SERVEUR_CLIENT.md)
- **Modifications :** [MODIFICATIONS_V2.2.md](Documentation/MODIFICATIONS_V2.2.md)
- **Sécurité :** [SECURITE.md](Documentation/SECURITE.md)

---

## Questions fréquentes

### Le scheduler fonctionne-t-il sur PythonAnywhere Free ?

**Peut-être pas.** PythonAnywhere Free limite les background processes.

**Si ça ne fonctionne pas :**
- Les heartbeats fonctionneront quand même
- Le statut sera mis à jour uniquement quand le serveur traite des requêtes
- Solution : upgrade vers paid account ($5/mois)

### Les fichiers des peers supprimés sont-ils perdus ?

**Non !** Les fichiers restent dans `storage/<peer_name>/`. Seul l'enregistrement dans la table `peers` est supprimé.

Si le peer se reconnecte, il sera re-créé avec le même nom.

### Comment voir qui est connecté ?

Interface web → Section "PC Connectés" → Les peers verts sont online, les gris sont offline.

---

## Prochaines étapes

Vous pouvez maintenant :
1. Déployer sur PythonAnywhere
2. Tester avec plusieurs utilisateurs
3. Vérifier que les statuts s'affichent correctement

**Bon déploiement ! 🚀**
