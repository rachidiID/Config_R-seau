#!/bin/bash

# Script de vérification - S'assure que tout est prêt avant de lancer

echo "=========================================="
echo "VÉRIFICATION PROJET RÉSEAU P2P LOCAL"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Compteurs
ERRORS=0
WARNINGS=0

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher OK
ok() {
    echo -e "${GREEN}✓${NC} $1"
}

# Fonction pour afficher erreur
error() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

# Fonction pour afficher warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

echo "1. Vérification des fichiers..."
echo "================================"

# Fichiers Python core
FILES=(
    "config_local.py"
    "discovery.py"
    "database.py"
    "ha_manager.py"
    "server_local.py"
    "launcher.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        ok "Fichier $file présent"
    else
        error "Fichier $file manquant"
    fi
done

# Fichiers de config
if [ -f "requirements.txt" ]; then
    ok "requirements.txt présent"
else
    error "requirements.txt manquant"
fi

if [ -f ".gitignore" ]; then
    ok ".gitignore présent"
else
    warning ".gitignore manquant (recommandé)"
fi

# Documentation
echo ""
echo "2. Vérification de la documentation..."
echo "======================================="

DOCS=(
    "README.md"
    "CHANGELOG.md"
    "RESUME.md"
    "Doc/QUICKSTART.md"
    "Doc/TESTS_COMPLETS.md"
    "Doc/COMPARAISON.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        ok "Documentation $doc présente"
    else
        warning "Documentation $doc manquante"
    fi
done

# Interface web
echo ""
echo "3. Vérification de l'interface web..."
echo "======================================"

if [ -d "web" ]; then
    ok "Dossier web/ présent"
    
    if [ -d "web/templates" ]; then
        ok "Dossier web/templates/ présent"
        
        if [ -f "web/templates/index.html" ]; then
            ok "  index.html présent"
        else
            error "  index.html manquant"
        fi
        
        if [ -f "web/templates/login.html" ]; then
            ok "  login.html présent"
        else
            error "  login.html manquant"
        fi
    else
        error "Dossier web/templates/ manquant"
    fi
    
    if [ -d "web/static" ]; then
        ok "Dossier web/static/ présent"
        
        if [ -f "web/static/app.js" ]; then
            ok "  app.js présent"
        else
            error "  app.js manquant"
        fi
        
        if [ -f "web/static/style.css" ]; then
            ok "  style.css présent"
        else
            error "  style.css manquant"
        fi
    else
        error "Dossier web/static/ manquant"
    fi
else
    error "Dossier web/ manquant - copier depuis reseau-partage/web"
fi

# Python
echo ""
echo "4. Vérification de l'environnement Python..."
echo "============================================="

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    ok "Python 3 installé (version $PYTHON_VERSION)"
    
    # Vérifier version >= 3.8
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        ok "Version Python >= 3.8"
    else
        error "Version Python < 3.8 (requis: 3.8+)"
    fi
else
    error "Python 3 non installé"
fi

# Environnement virtuel
if [ -d "venv" ]; then
    ok "Environnement virtuel créé"
    
    # Vérifier si activé
    if [[ "$VIRTUAL_ENV" == *"reseau-partage-local"* ]]; then
        ok "Environnement virtuel activé"
    else
        warning "Environnement virtuel non activé (lancez: source venv/bin/activate)"
    fi
else
    warning "Environnement virtuel non créé (recommandé: python3 -m venv venv)"
fi

# Dépendances
echo ""
echo "5. Vérification des dépendances..."
echo "==================================="

if [ -d "venv" ] && [[ "$VIRTUAL_ENV" == *"reseau-partage-local"* ]]; then
    # Vérifier Flask
    if python3 -c "import flask" 2>/dev/null; then
        FLASK_VERSION=$(python3 -c "import flask; print(flask.__version__)")
        ok "Flask installé (version $FLASK_VERSION)"
    else
        error "Flask non installé (pip install flask)"
    fi
    
    # Vérifier netifaces
    if python3 -c "import netifaces" 2>/dev/null; then
        ok "netifaces installé"
    else
        error "netifaces non installé (pip install netifaces)"
    fi
    
    # Vérifier APScheduler
    if python3 -c "import apscheduler" 2>/dev/null; then
        ok "APScheduler installé"
    else
        error "APScheduler non installé (pip install apscheduler)"
    fi
    
    # Vérifier Flask-CORS
    if python3 -c "import flask_cors" 2>/dev/null; then
        ok "Flask-CORS installé"
    else
        warning "Flask-CORS non installé (optionnel)"
    fi
else
    warning "Impossible de vérifier dépendances (venv non activé)"
fi

# Réseau
echo ""
echo "6. Vérification réseau..."
echo "========================="

# Vérifier interfaces réseau
if command -v ip &> /dev/null; then
    INTERFACES=$(ip -o link show | awk -F': ' '{print $2}' | grep -v "^lo$")
    ok "Interfaces réseau disponibles:"
    for iface in $INTERFACES; do
        echo "   - $iface"
    done
else
    warning "Commande 'ip' non disponible (impossible de lister interfaces)"
fi

# Vérifier ports
if command -v lsof &> /dev/null; then
    if lsof -i :5000 &> /dev/null; then
        warning "Port 5000 déjà utilisé (kill le processus avant de lancer)"
    else
        ok "Port 5000 disponible"
    fi
    
    if lsof -i :5555 &> /dev/null; then
        warning "Port 5555 (UDP) déjà utilisé"
    else
        ok "Port 5555 disponible"
    fi
else
    warning "Commande 'lsof' non disponible (impossible de vérifier ports)"
fi

# Syntaxe Python
echo ""
echo "7. Vérification syntaxe Python..."
echo "=================================="

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            ok "Syntaxe $file valide"
        else
            error "Erreur syntaxe dans $file"
        fi
    fi
done

# Scripts exécutables
echo ""
echo "8. Vérification permissions..."
echo "=============================="

if [ -x "test_demo.sh" ]; then
    ok "test_demo.sh exécutable"
else
    warning "test_demo.sh non exécutable (chmod +x test_demo.sh)"
fi

if [ -x "verify.sh" ]; then
    ok "verify.sh exécutable"
else
    warning "verify.sh non exécutable (chmod +x verify.sh)"
fi

# Résumé
echo ""
echo "=========================================="
echo "RÉSUMÉ"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Tout est prêt ! Aucun problème détecté.${NC}"
    echo ""
    echo "Pour lancer la démo :"
    echo "  ./test_demo.sh"
    echo ""
    echo "Pour lancer manuellement :"
    echo "  python launcher.py --mode server --name PC1"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings détectés${NC}"
    echo ""
    echo "Le projet devrait fonctionner malgré les warnings."
    echo ""
    exit 0
else
    echo -e "${RED}✗ $ERRORS erreurs détectées${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warnings détectés${NC}"
    fi
    echo ""
    echo "Corrigez les erreurs avant de lancer."
    echo ""
    
    # Suggestions
    echo "Suggestions :"
    if [ $ERRORS -gt 0 ]; then
        echo "  1. Installez les dépendances manquantes :"
        echo "     pip install -r requirements.txt"
        echo ""
        echo "  2. Si web/ manque, copiez depuis la version cloud :"
        echo "     cp -r ../reseau-partage/web ."
        echo ""
    fi
    
    exit 1
fi
