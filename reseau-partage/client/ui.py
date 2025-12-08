"""
Interface utilisateur en ligne de commande
"""

from typing import List
import os


class CLI:
    """Interface en ligne de commande"""
    
    def __init__(self, peer_name: str):
        """
        Initialiser l'interface
        
        Args:
            peer_name: Nom de ce PC
        """
        self.peer_name = peer_name
    
    def show_banner(self):
        """Afficher la bannière"""
        print("\n" + "=" * 60)
        print(f"RESEAU DE PARTAGE P2P - {self.peer_name}")
        print("=" * 60)
    
    def show_help(self):
        """Afficher l'aide"""
        print("\nCOMMANDES DISPONIBLES:\n")
        print("  list                    - Voir les PC connectés")
        print("  send <chemin> <dest>    - Envoyer un fichier ou dossier")
        print("                            dest = PC1, PC2, ... ou * (tous)")
        print("  received                - Voir les fichiers/dossiers reçus")
        print("  status                  - Statut du serveur")
        print("  help                    - Afficher cette aide")
        print("  quit                    - Quitter\n")
        print("EXEMPLES:\n")
        print("  send document.pdf PC2        -> Envoyer fichier à PC2")
        print("  send /home/user/photos PC3   -> Envoyer dossier à PC3")
        print("  send image.png PC2 PC3       -> Envoyer à PC2 et PC3")
        print("  send projet/ *               -> Envoyer dossier à tous")
        print()
    
    def show_peers(self, peers: List[dict]):
        """
        Afficher la liste des PC
        
        Args:
            peers: Liste des PC
        """
        if not peers:
            print("\n[!] Aucun autre PC connecté")
            return
        
        print(f"\nPC CONNECTES ({len(peers)}):\n")
        print(f"{'Nom':<15} {'Adresse IP':<20} {'Port':<10} {'Statut':<10}")
        print("-" * 55)
        
        for peer in peers:
            status = "En ligne" if peer['status'] == 'online' else "Hors ligne"
            print(f"{peer['name']:<15} {peer['ip_address']:<20} {peer['port']:<10} {status:<10}")
        
        print()
    
    def show_received_files(self, files: List[dict]):
        """
        Afficher les fichiers reçus
        
        Args:
            files: Liste des fichiers
        """
        if not files:
            print("\nAucun fichier reçu")
            return
        
        print(f"\nFICHIERS RECUS ({len(files)}):\n")
        print(f"{'Type':<10} {'Nom':<30} {'Taille':<15}")
        print("-" * 55)
        
        from shared.utils import format_size
        
        for file in files:
            file_type = file.get('type', 'file')
            type_str = "Dossier" if file_type == 'folder' else "Fichier"
            print(f"{type_str:<10} {file['name']:<30} {format_size(file['size']):<15}")
        
        print()
    
    def show_server_status(self, status: dict):
        """
        Afficher le statut du serveur
        
        Args:
            status: Statut du serveur
        """
        if not status:
            print("\n[!] Serveur inaccessible")
            return
        
        print("\nSTATUT DU SERVEUR:\n")
        print(f"  Statut: {status.get('status', 'inconnu')}")
        print(f"  Version: {status.get('version', '?')}")
        print(f"  PC totaux: {status.get('peers_total', 0)}")
        print(f"  PC en ligne: {status.get('peers_online', 0)}")
        print()
    
    def prompt(self) -> str:
        """
        Afficher le prompt et lire la commande
        
        Returns:
            Commande saisie
        """
        try:
            return input(f"{self.peer_name}> ").strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def parse_send_command(self, command: str) -> tuple:
        """
        Parser une commande send
        
        Args:
            command: Commande complète
            
        Returns:
            (filepath, recipients) ou (None, None) si erreur
        """
        parts = command.split()
        
        if len(parts) < 3:
            print("[X] Usage: send <fichier/dossier> <destinataire(s)>")
            print("   Exemples:")
            print("     send file.txt PC2")
            print("     send /home/user/photos PC3")
            print("     send file.txt PC2 PC3")
            print("     send projet/ *")
            return None, None
        
        filepath = parts[1]
        
        # Vérifier que le fichier/dossier existe
        if not os.path.exists(filepath):
            print(f"[X] Chemin non trouvé: {filepath}")
            return None, None
        
        # Récupérer les destinataires
        recipients = parts[2:]
        
        return filepath, recipients
    
    def confirm(self, message: str) -> bool:
        """
        Demander confirmation
        
        Args:
            message: Message de confirmation
            
        Returns:
            True si confirmé, False sinon
        """
        try:
            response = input(f"{message} (o/n): ").strip().lower()
            return response in ['o', 'oui', 'y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False
    
    def error(self, message: str):
        """Afficher un message d'erreur"""
        print(f"[X] {message}")
    
    def success(self, message: str):
        """Afficher un message de succès"""
        print(f"[OK] {message}")
    
    def info(self, message: str):
        """Afficher une information"""
        print(f"ℹ️  {message}")
