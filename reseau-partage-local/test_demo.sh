#!/bin/bash

# Script de démonstration - Lance 3 terminaux avec serveurs/client

echo "================================================"
echo "DÉMONSTRATION RÉSEAU P2P LOCAL AVEC HAUTE DISPO"
echo "================================================"
echo ""
echo "Ce script va ouvrir 3 terminaux :"
echo "  - Terminal 1 : Serveur PC1 (deviendra PRIMAIRE)"
echo "  - Terminal 2 : Serveur PC2 (deviendra SECONDAIRE)"
echo "  - Terminal 3 : Client PC3"
echo ""
echo "Pour tester le failover :"
echo "  1. Arrêtez PC1 avec Ctrl+C dans son terminal"
echo "  2. Observez PC2 devenir PRIMAIRE en ~15s"
echo ""
read -p "Appuyez sur ENTRÉE pour démarrer..."

# Fonction pour détecter le terminal disponible
launch_terminal() {
    local title="$1"
    local cmd="$2"
    
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$cmd; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e bash -c "$cmd; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole --title "$title" -e bash -c "$cmd; exec bash" &
    else
        echo "Aucun terminal graphique trouvé. Lancez manuellement :"
        echo "$cmd"
    fi
}

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Vérifier les dépendances
echo "Vérification des dépendances..."
python -c "import flask; import netifaces; import apscheduler" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installation des dépendances..."
    pip install -r requirements.txt
fi

echo ""
echo "✓ Dépendances OK"
echo ""

# Lancer les 3 nœuds
echo "Lancement de PC1 (Serveur)..."
sleep 1
launch_terminal "PC1 - Serveur Principal" "cd '$SCRIPT_DIR' && source venv/bin/activate && python launcher.py --mode server --name PC1"

echo "Attente de 3 secondes pour que PC1 démarre..."
sleep 3

echo "Lancement de PC2 (Serveur)..."
sleep 1
launch_terminal "PC2 - Serveur Secondaire" "cd '$SCRIPT_DIR' && source venv/bin/activate && python launcher.py --mode server --name PC2"

echo "Attente de 3 secondes pour que PC2 se synchronise..."
sleep 3

echo "Lancement de PC3 (Client)..."
sleep 1
launch_terminal "PC3 - Client" "cd '$SCRIPT_DIR' && source venv/bin/activate && python launcher.py --mode client --name PC3"

echo ""
echo "================================================"
echo "✓ Tous les nœuds sont lancés !"
echo "================================================"
echo ""
echo "Test suggérés :"
echo "  1. Connectez-vous via l'interface web (PC3)"
echo "  2. Uploadez un fichier"
echo "  3. Arrêtez PC1 → PC2 devient primaire"
echo "  4. Vérifiez que le fichier est toujours accessible"
echo ""
echo "API utiles :"
echo "  curl http://localhost:5000/api/ha/status"
echo "  curl http://localhost:5000/api/peers"
echo "  curl http://localhost:5000/api/health"
echo ""
