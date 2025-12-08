"""
Communication réseau avec le serveur
"""

import requests
from typing import List, Dict, Optional
import sys
import os

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.utils import get_local_ip


class NetworkClient:
    """Client pour communiquer avec le serveur central"""
    
    def __init__(self, server_url: str, peer_name: str, peer_port: int = 5001):
        """
        Initialiser le client réseau
        
        Args:
            server_url: URL du serveur (ex: http://localhost:5000)
            peer_name: Nom de ce PC
            peer_port: Port pour recevoir les fichiers
        """
        self.server_url = server_url.rstrip('/')
        self.peer_name = peer_name
        self.peer_port = peer_port
        self.peer_ip = get_local_ip()
    
    def register(self) -> bool:
        """
        S'enregistrer sur le serveur
        
        Returns:
            True si succès, False sinon
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/register",
                json={
                    'name': self.peer_name,
                    'ip': self.peer_ip,
                    'port': self.peer_port
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ Enregistré sur le serveur en tant que: {self.peer_name}")
                print(f"  IP: {self.peer_ip}:{self.peer_port}")
                return True
            else:
                print(f"✗ Erreur d'enregistrement: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Impossible de contacter le serveur: {e}")
            return False
    
    def unregister(self):
        """Se déconnecter du serveur"""
        try:
            requests.post(
                f"{self.server_url}/api/unregister",
                json={'name': self.peer_name},
                timeout=5
            )
            print(f"✓ Déconnecté du serveur")
        except:
            pass
    
    def get_peers(self) -> List[Dict]:
        """
        Obtenir la liste des PC connectés
        
        Returns:
            Liste des PC avec leurs infos
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/peers/online",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Filtrer pour ne pas s'inclure soi-même
                peers = [p for p in data['peers'] if p['name'] != self.peer_name]
                return peers
            else:
                return []
                
        except requests.exceptions.RequestException:
            return []
    
    def get_peer_info(self, peer_name: str) -> Optional[Dict]:
        """
        Obtenir les infos d'un PC spécifique
        
        Args:
            peer_name: Nom du PC
            
        Returns:
            Infos du PC ou None
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/peer/{peer_name}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def register_file(self, filename: str, filesize: int, checksum: str,
                     permission: str, recipients: List[str]) -> Optional[int]:
        """
        Enregistrer un fichier sur le serveur
        
        Args:
            filename: Nom du fichier
            filesize: Taille en octets
            checksum: Checksum MD5
            permission: Type de permission (private, shared, public)
            recipients: Liste des destinataires
            
        Returns:
            ID du fichier ou None
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/file/register",
                json={
                    'filename': filename,
                    'filesize': filesize,
                    'checksum': checksum,
                    'owner': self.peer_name,
                    'permission': permission,
                    'recipients': recipients
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('file_id')
            else:
                print(f"✗ Erreur d'enregistrement du fichier: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur réseau: {e}")
            return None
    
    def check_permission(self, file_id: int, peer_name: str) -> bool:
        """
        Vérifier si un PC peut accéder à un fichier
        
        Args:
            file_id: ID du fichier
            peer_name: Nom du PC
            
        Returns:
            True si autorisé, False sinon
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/file/{file_id}/check",
                json={'peer_name': peer_name},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('allowed', False)
            else:
                return False
                
        except requests.exceptions.RequestException:
            return False
    
    def log_transfer(self, file_id: int, to_peer: str, status: str):
        """
        Enregistrer un transfert
        
        Args:
            file_id: ID du fichier
            to_peer: Destinataire
            status: Statut (success, failed)
        """
        try:
            requests.post(
                f"{self.server_url}/api/transfer/log",
                json={
                    'file_id': file_id,
                    'from_peer': self.peer_name,
                    'to_peer': to_peer,
                    'status': status
                },
                timeout=5
            )
        except:
            pass
    
    def server_status(self) -> Optional[Dict]:
        """
        Obtenir le statut du serveur
        
        Returns:
            Statut ou None
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/status",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
