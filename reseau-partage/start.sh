#!/bin/bash

# Script de test - Démarrage automatique du projet

echo "🚀 Démarrage du projet Réseau de Partage P2P"
echo "=============================================="
echo ""

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "   Exécutez d'abord: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activer l'environnement
source venv/bin/activate

echo "✅ Environnement virtuel activé"
echo ""
echo "📋 Pour tester le projet:"
echo ""
echo "Terminal 1 - Serveur:"
echo "  python server/main.py"
echo ""
echo "Terminal 2 - PC1:"
echo "  python client/main.py --name PC1 --port 5001"
echo ""
echo "Terminal 3 - PC2:"
echo "  python client/main.py --name PC2 --port 5002"
echo ""
echo "Terminal 4 - PC3:"
echo "  python client/main.py --name PC3 --port 5003"
echo ""
echo "=============================================="
