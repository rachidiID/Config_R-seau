#!/usr/bin/env python3
"""
Launcher - Point d'entrée unique pour la version locale
Usage:
    python launcher.py --mode server --name PC1
    python launcher.py --mode client --name PC3
"""

import argparse
import sys
import os

# Ajouter le dossier au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """Afficher la bannière"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║     RÉSEAU P2P LOCAL AVEC HAUTE DISPONIBILITÉ              ║
║     Version Locale - Multi-serveurs HA                     ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_dependencies():
    """Vérifier que les dépendances sont installées"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append('Flask')
    
    try:
        import flask_cors
    except ImportError:
        missing.append('Flask-CORS')
    
    try:
        import apscheduler
    except ImportError:
        missing.append('APScheduler')
    
    try:
        import netifaces
    except ImportError:
        missing.append('netifaces')
    
    if missing:
        print("❌ Dépendances manquantes :")
        for dep in missing:
            print(f"   - {dep}")
        print("\n💡 Installez-les avec :")
        print("   pip install -r requirements.txt")
        sys.exit(1)


def launch_server(name: str):
    """Lancer en mode serveur"""
    print(f"🚀 Lancement en mode SERVEUR : {name}")
    print("📡 Découverte réseau activée...")
    print("🔄 Haute Disponibilité activée...")
    print()
    
    from server_local import start_server
    start_server(name, is_server=True)


def launch_client(name: str):
    """Lancer en mode client"""
    print(f"🚀 Lancement en mode CLIENT : {name}")
    print("🔍 Recherche des serveurs disponibles...")
    print()
    
    import time
    from discovery import NetworkDiscovery
    from config_local import SERVER_PORT
    
    # Démarrer découverte
    discovery = NetworkDiscovery(name, 'client', SERVER_PORT)
    discovery.start()
    
    # Attendre découverte
    print("⏳ Scan du réseau local...")
    time.sleep(3)
    
    servers = discovery.get_servers()
    
    if not servers:
        print("❌ Aucun serveur trouvé sur le réseau")
        print("\n💡 Assurez-vous qu'au moins un serveur est démarré avec :")
        print("   python launcher.py --mode server --name PC1")
        discovery.stop()
        sys.exit(1)
    
    primary = discovery.get_primary_server()
    
    print(f"✅ {len(servers)} serveur(s) trouvé(s) :")
    for s in servers:
        status = "👑 PRIMAIRE" if s['name'] == primary['name'] else "🔄 BACKUP"
        print(f"   - {s['name']} ({s['ip']}:{s['port']}) {status}")
    
    print(f"\n🌐 Ouverture interface web : http://{primary['ip']}:{primary['port']}/web")
    print(f"📝 Utilisez le nom : {name}")
    
    # Ouvrir navigateur
    try:
        import webbrowser
        url = f"http://{primary['ip']}:{primary['port']}/web"
        webbrowser.open(url)
        print("\n✅ Navigateur ouvert !")
    except:
        print("\n💡 Ouvrez manuellement dans votre navigateur")
    
    print("\nℹ️  Appuyez sur Ctrl+C pour quitter")
    
    # Garder le processus vivant pour heartbeat
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du client...")
        discovery.stop()
        print("✅ Client arrêté")


def interactive_mode():
    """Mode interactif si pas d'arguments"""
    print_banner()
    
    print("Choisissez le mode de démarrage :")
    print("1. Serveur (héberge les fichiers + interface)")
    print("2. Client (utilise l'interface)")
    print()
    
    choice = input("Votre choix (1/2) : ").strip()
    
    if choice not in ['1', '2']:
        print("❌ Choix invalide")
        sys.exit(1)
    
    name = input("\nNom du PC (ex: PC1, Mon-Ordi...) : ").strip()
    
    if not name:
        print("❌ Nom requis")
        sys.exit(1)
    
    print()
    
    if choice == '1':
        launch_server(name)
    else:
        launch_client(name)


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Réseau P2P Local avec HA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  # Lancer un serveur primaire
  python launcher.py --mode server --name PC1
  
  # Lancer un serveur secondaire (backup)
  python launcher.py --mode server --name PC2
  
  # Lancer un client
  python launcher.py --mode client --name PC3
  
  # Mode interactif
  python launcher.py
        """
    )
    
    parser.add_argument('--mode', choices=['server', 'client'], 
                        help='Mode de démarrage')
    parser.add_argument('--name', help='Nom du PC')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Vérifier dépendances
    check_dependencies()
    
    # Mode interactif si pas d'arguments
    if not args.mode or not args.name:
        interactive_mode()
        return
    
    # Mode avec arguments
    if args.mode == 'server':
        launch_server(args.name)
    else:
        launch_client(args.name)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
