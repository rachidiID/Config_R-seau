# 🎯 Guide Complet v2.1 - Avec Authentification

## 🆕 Nouveautés v2.1

### ✅ Améliorations Implémentées

1. **Notifications en Stack** 
   - Les notifications s'empilent (max 3)
   - Disparition progressive après 5s chacune
   - Bouton × pour fermer manuellement

2. **Page de Connexion Sécurisée**
   - Nom du PC + Mot de passe réseau
   - Plus besoin de taper l'URL avec paramètres

3. **Auto-Détection de Port**
   - Port attribué automatiquement
   - Plus de conflits de ports

4. **Authentification Simple**
   - Premier utilisateur crée le réseau
   - Autres utilisateurs rejoignent avec le mot de passe
   - Session sauvegardée (reconnexion auto)

5. **Déconnexion Propre**
   - Bouton "Déconnexion" dans l'interface
   - Libération automatique du port

---

## 🚀 Nouvelle Procédure de Connexion

### Étape 1 : Accéder au Réseau

Ouvrez simplement :
```
https://rachidi.pythonanywhere.com/web
```

### Étape 2 : Page de Connexion

Vous verrez :

```
┌──────────────────────────────┐
│   🌐 Réseau P2P v2.0         │
│                              │
│   Nom du PC: [_______]       │
│   Mot de passe: [_____]      │
│                              │
│   [ Se connecter ]           │
│                              │
│   ✓ Port détecté auto        │
└──────────────────────────────┘
```

### Étape 3 : Première Connexion (Créer le Réseau)

**Si vous êtes le premier utilisateur :**

1. **Nom du PC** : `PC1` (ou votre nom)
2. **Mot de passe** : `monmotdepasse` (choisissez-en un)
3. Cliquez **"Se connecter"**
4. ✅ **Réseau créé !**

**💡 Notez bien le mot de passe** - les autres devront l'utiliser.

---

### Étape 4 : Rejoindre le Réseau (Utilisateurs Suivants)

**Si le réseau existe déjà :**

1. **Nom du PC** : `PC2` (votre nom unique)
2. **Mot de passe** : `monmotdepasse` (le même que le premier utilisateur)
3. Cliquez **"Se connecter"**
4. ✅ **Connecté !**

**⚠️ Si le mot de passe est incorrect :**
```
❌ Erreur: Mot de passe incorrect
```

---

## 🎮 Utilisation

### Partager un Fichier

1. **Glisser-déposer** un fichier dans la zone d'upload
2. **Choisir** le destinataire
3. **Cliquer** "Envoyer"
4. ✅ **Notifications empilées :**
   ```
   ✓ Fichier sélectionné
   ✓ Envoi en cours...
   ✓ Fichier envoyé avec succès
   ```

### Recevoir un Fichier

- **Automatique** : Le fichier apparaît dans "Fichiers reçus"
- **Notification** : "Nouveau fichier reçu de PC1"

### Déconnexion

Cliquez sur **"🚪 Déconnexion"** en haut à droite.

---

## 🔒 Sécurité

### Mot de Passe Réseau

- **Stocké** : Haché en SHA-256 (non visible)
- **Validation** : Chaque connexion vérifie le hash
- **Tokens** : Session sécurisée par token unique

### Sessions

- **Durée** : 24 heures
- **Stockage** : localStorage du navigateur
- **Reconnexion** : Automatique si session valide

### Ports

- **Attribution** : Automatique et séquentielle
- **Plage** : 5001 → 5100 (extensible)
- **Libération** : Automatique à la déconnexion

---

## 📊 Comparaison v2.0 vs v2.1

| Fonctionnalité | v2.0 | v2.1 |
|----------------|------|------|
| **Connexion** | URL avec paramètres | Page de connexion |
| **Port** | Manuel (dans URL) | Auto-détecté ✨ |
| **Sécurité** | Aucune | Mot de passe réseau ✨ |
| **Notifications** | 1 à la fois | Stack de 3 ✨ |
| **Session** | Non persistante | Sauvegardée 24h ✨ |
| **Déconnexion** | Fermer la page | Bouton dédié ✨ |

---

## 🎯 Exemples de Scénarios

### Scénario 1 : Créer un Réseau Familial

**Utilisateur 1 (Papa - PC Bureau) :**
```
1. Ouvrir : https://rachidi.pythonanywhere.com/web
2. Nom : "Papa"
3. Mot de passe : "famille2026"
4. ✅ Réseau créé !
```

**Utilisateur 2 (Maman - PC Salon) :**
```
1. Ouvrir : https://rachidi.pythonanywhere.com/web
2. Nom : "Maman"
3. Mot de passe : "famille2026"
4. ✅ Connecté !
```

**Utilisateur 3 (Enfant - Laptop) :**
```
1. Ouvrir : https://rachidi.pythonanywhere.com/web
2. Nom : "Enfant"
3. Mot de passe : "famille2026"
4. ✅ Connecté !
```

**Papa envoie photo.jpg à tout le monde :**
```
Destinataire : "Tous les PC (2)"
```

✅ Maman et Enfant reçoivent la photo !

---

### Scénario 2 : Réseau d'Entreprise

**Admin (Premier) :**
```
Nom : "Serveur-Principal"
Mot de passe : "EntrepriseXYZ#2026"
```

**Employés :**
```
Nom : "Employé-1", "Employé-2", etc.
Mot de passe : "EntrepriseXYZ#2026"
```

**Sécurité** : Le mot de passe est partagé uniquement aux employés autorisés.

---

## 🛠️ Résolution de Problèmes

### Erreur "Mot de passe incorrect"

**Cause** : Le mot de passe ne correspond pas au réseau existant

**Solutions** :
1. Vérifier auprès du créateur du réseau
2. Si vous êtes seul, supprimer le fichier `network_auth.json` et recréer

---

### Erreur "Impossible de trouver un port disponible"

**Cause** : Plus de 100 utilisateurs connectés

**Solutions** :
1. Augmenter la limite de ports dans le code
2. Déconnecter des utilisateurs inactifs
3. Utiliser un VPS avec plus de ressources

---

### Session expirée

**Après 24h, reconnexion automatique échoue**

**Solution** : Simplement se reconnecter (nom + mot de passe)

---

### Notifications ne s'empilent pas

**Vérifier** :
1. Navigateur à jour (Chrome, Firefox, Edge)
2. JavaScript activé
3. Vider le cache : Ctrl+Shift+R

---

## 🔄 Mise à Jour depuis v2.0

### Sur PythonAnywhere

```bash
# Console Bash
cd ~/Config_R-seau/reseau-partage
git pull origin main

# Puis cliquer "Reload" sur l'onglet Web
```

### En Local

```bash
cd ~/Base_de_données/Config_R-seau/reseau-partage
git pull origin main

# Redémarrer le serveur
python server/main.py
```

---

## 📱 Accès Mobile

L'interface est **responsive** :

- **Sur mobile** : Interface adaptée
- **Connexion** : Même procédure (nom + mot de passe)
- **Notifications** : Empilées verticalement

---

## 🎉 Résumé des Avantages v2.1

✅ **Plus simple** : Pas d'URL complexe  
✅ **Plus sécurisé** : Authentification par mot de passe  
✅ **Plus intelligent** : Port auto-détecté  
✅ **Plus confortable** : Notifications empilées  
✅ **Plus rapide** : Reconnexion automatique  

**Fini les erreurs de port, fini les connexions non autorisées !** 🎯

---

## 📞 Aide

Pour toute question :
1. Vérifier les logs PythonAnywhere (Error log)
2. Consulter ce guide
3. Vérifier le fichier `network_auth.json` (stocke les infos)

**Le réseau est maintenant prêt pour une utilisation professionnelle !** 🚀
