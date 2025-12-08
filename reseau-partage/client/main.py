"""
Client Principal - Application P2P
Projet: Réseau de partage de fichiers
"""

import argparse
import os
import sys
import signal

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from client.network import NetworkClient
from client.transfer import FileTransfer
from client.ui import CLI
from client.notifications import NotificationManager
from shared.utils import calculate_checksum, format_size


class P2PClient:
    """Client P2P principal"""
    
    def __init__(self, peer_name: str, server_url: str = "http://localhost:5000", port: int = 5001):
        """
        Initialiser le client
        
        Args:
            peer_name: Nom de ce PC
            server_url: URL du serveur central
            port: Port pour recevoir les fichiers
        """
        self.peer_name = peer_name
        self.server_url = server_url
        self.port = port
        
        # Composants
        self.network = NetworkClient(server_url, peer_name, port)
        self.notifications = NotificationManager(enabled=True)
        
        # Dossier de stockage
        storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', peer_name)
        self.transfer = FileTransfer(storage_dir, port, on_receive_callback=self._on_file_received)
        
        self.ui = CLI(peer_name)
        
        # État
        self.running = False
    
    def _on_file_received(self, filename: str, sender_ip: str, is_folder: bool):
        """
        Callback appelé lors de la réception d'un fichier/dossier
        
        Args:
            filename: Nom du fichier/dossier
            sender_ip: IP de l'expéditeur
            is_folder: True si c'est un dossier
        """
        # Essayer de trouver le nom du PC expéditeur
        peers = self.network.get_peers()
        sender_name = sender_ip
        for peer in peers:
            if peer['ip_address'] == sender_ip:
                sender_name = peer['name']
                break
        
        # Envoyer la notification
        self.notifications.notify_file_received(filename, sender_name, is_folder)
    
    def start(self) -> bool:
        """
        Démarrer le client
        
        Returns:
            True si démarré avec succès
        """
        self.ui.show_banner()
        
        # S'enregistrer sur le serveur
        if not self.network.register():
            print("\n[!] Impossible de se connecter au serveur.")
            print("   Vérifiez que le serveur est démarré:")
            print(f"   python server/main.py\n")
            return False
        
        # Démarrer le serveur de réception
        self.transfer.start_receiver()
        
        print(f"\n[OK] Client prêt ! Tapez 'help' pour voir les commandes.\n")
        
        self.running = True
        return True
    
    def stop(self):
        """Arrêter le client"""
        self.running = False
        print("\n\nArret du client...")
        
        # Se déconnecter
        self.network.unregister()
        
        # Arrêter le serveur de réception
        self.transfer.stop_receiver()
        
        print("[OK] Client arrêté proprement.\n")
    
    def run(self):
        """Boucle principale"""
        while self.running:
            try:
                command = self.ui.prompt()
                
                if not command:
                    continue
                
                self.handle_command(command)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Erreur: {e}\n")
        
        self.stop()
    
    def handle_command(self, command: str):
        """
        Traiter une commande
        
        Args:
            command: Commande saisie
        """
        parts = command.split()
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        # Commandes
        if cmd == 'help':
            self.ui.show_help()
        
        elif cmd == 'list':
            self.cmd_list_peers()
        
        elif cmd == 'send':
            self.cmd_send_file(command)
        
        elif cmd == 'received':
            self.cmd_list_received()
        
        elif cmd == 'status':
            self.cmd_server_status()
        
        elif cmd in ['quit', 'exit', 'q']:
            self.running = False
        
        else:
            print(f"❌ Commande inconnue: {cmd}")
            print("   Tapez 'help' pour voir les commandes disponibles")
    
    def cmd_list_peers(self):
        """Lister les PC connectés"""
        peers = self.network.get_peers()
        self.ui.show_peers(peers)
    
    def cmd_send_file(self, command: str):
        """
        Envoyer un fichier ou dossier
        
        Args:
            command: Commande complète
        """
        # Parser la commande
        filepath, recipients = self.ui.parse_send_command(command)
        
        if not filepath or not recipients:
            return
        
        # Vérifier que le chemin existe
        if not os.path.exists(filepath):
            print(f"[X] Chemin non trouvé: {filepath}")
            return
        
        # Déterminer si c'est un fichier ou un dossier
        is_folder = os.path.isdir(filepath)
        item_type = "dossier" if is_folder else "fichier"
        
        # Déterminer le type de permission
        if '*' in recipients:
            permission = 'public'
            # Récupérer tous les PC en ligne
            peers = self.network.get_peers()
            recipients = [p['name'] for p in peers]
            
            if not recipients:
                print(f"[X] Aucun PC en ligne pour recevoir le {item_type}")
                return
            
            print(f"[INFO] Envoi public à {len(recipients)} PC")
        elif len(recipients) == 1:
            permission = 'private'
        else:
            permission = 'shared'
        
        # Vérifier que les PC existent
        valid_recipients = []
        for recipient in recipients:
            peer_info = self.network.get_peer_info(recipient)
            if peer_info:
                valid_recipients.append(peer_info)
            else:
                print(f"[!] PC non trouvé ou hors ligne: {recipient}")
        
        if not valid_recipients:
            print("[X] Aucun destinataire valide")
            return
        
        # Calculer les infos
        filename = os.path.basename(filepath)
        
        if is_folder:
            # Calculer la taille totale du dossier
            total_size = 0
            for root, dirs, files in os.walk(filepath):
                for f in files:
                    fp = os.path.join(root, f)
                    total_size += os.path.getsize(fp)
            filesize = total_size
            checksum = "folder"  # Pas de checksum pour les dossiers
        else:
            filesize = os.path.getsize(filepath)
            checksum = calculate_checksum(filepath)
        
        print(f"\nPreparation de l'envoi:")
        print(f"  {'Dossier' if is_folder else 'Fichier'}: {filename}")
        print(f"  Taille: {format_size(filesize)}")
        print(f"  Destinataires: {', '.join([r['name'] for r in valid_recipients])}")
        print(f"  Permission: {permission}")
        
        # Enregistrer sur le serveur
        file_id = self.network.register_file(
            filename=filename,
            filesize=filesize,
            checksum=checksum,
            permission=permission,
            recipients=[r['name'] for r in valid_recipients]
        )
        
        if not file_id:
            print(f"[X] Impossible d'enregistrer le {item_type} sur le serveur")
            return
        
        print(f"[OK] {item_type.capitalize()} enregistré (ID: {file_id})")
        
        # Envoyer à chaque destinataire
        success_count = 0
        for recipient in valid_recipients:
            print(f"\nEnvoi vers {recipient['name']}...")
            
            if is_folder:
                success = self.transfer.send_folder(
                    folder_path=filepath,
                    peer_ip=recipient['ip_address'],
                    peer_port=recipient['port']
                )
            else:
                success = self.transfer.send_file(
                    filepath=filepath,
                    peer_ip=recipient['ip_address'],
                    peer_port=recipient['port']
                )
            
            # Logger le transfert
            status = 'success' if success else 'failed'
            self.network.log_transfer(file_id, recipient['name'], status)
            
            # Notification de transfert
            self.notifications.notify_transfer_complete(
                filename=filename,
                recipient=recipient['name'],
                is_folder=is_folder,
                success=success
            )
            
            if success:
                success_count += 1
        
        print(f"\n[OK] Transfert terminé: {success_count}/{len(valid_recipients)} réussis")
    
    def cmd_list_received(self):
        """Lister les fichiers reçus"""
        files = self.transfer.list_received_files()
        self.ui.show_received_files(files)
    
    def cmd_server_status(self):
        """Afficher le statut du serveur"""
        status = self.network.server_status()
        self.ui.show_server_status(status)


def signal_handler(sig, frame):
    """Gérer Ctrl+C proprement"""
    print("\n\n[!] Interruption détectée...")
    sys.exit(0)


def main():
    """Point d'entrée"""
    # Parser les arguments
    parser = argparse.ArgumentParser(description='Client P2P de partage de fichiers')
    parser.add_argument('--name', required=True, help='Nom de ce PC (ex: PC1)')
    parser.add_argument('--server', default='http://localhost:5000', help='URL du serveur')
    parser.add_argument('--port', type=int, default=5001, help='Port de réception')
    
    args = parser.parse_args()
    
    # Gérer Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Créer et démarrer le client
    client = P2PClient(
        peer_name=args.name,
        server_url=args.server,
        port=args.port
    )
    
    if client.start():
        client.run()


if __name__ == '__main__':
    main()
