"""
Gestion des transferts de fichiers P2P
"""

import socket
import os
import threading
import zipfile
import tempfile
from typing import Dict
import sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.utils import calculate_checksum, format_size
from shared.protocol import BUFFER_SIZE, CHUNK_SIZE


class FileTransfer:
    """Gestionnaire de transferts de fichiers"""
    
    def __init__(self, storage_dir: str, port: int = 5001, on_receive_callback=None):
        """
        Initialiser le gestionnaire
        
        Args:
            storage_dir: Dossier de stockage des fichiers reçus
            port: Port pour recevoir les fichiers
            on_receive_callback: Fonction à appeler lors de la réception (filename, sender_ip, is_folder)
        """
        self.storage_dir = storage_dir
        self.port = port
        self.server_socket = None
        self.running = False
        self.on_receive_callback = on_receive_callback
        
        # Créer le dossier de stockage
        os.makedirs(storage_dir, exist_ok=True)
    
    def start_receiver(self):
        """Démarrer le serveur de réception en arrière-plan"""
        self.running = True
        thread = threading.Thread(target=self._receive_loop, daemon=True)
        thread.start()
        print(f"[OK] Serveur de réception démarré sur le port {self.port}")
    
    def stop_receiver(self):
        """Arrêter le serveur de réception"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def _receive_loop(self):
        """Boucle de réception (thread séparé)"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Timeout pour vérifier self.running
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    # Traiter dans un thread séparé
                    thread = threading.Thread(
                        target=self._handle_receive,
                        args=(client_socket, address),
                        daemon=True
                    )
                    thread.start()
                except socket.timeout:
                    continue
                except:
                    break
                    
        except Exception as e:
            print(f"[X] Erreur serveur réception: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def _handle_receive(self, client_socket: socket.socket, address):
        """
        Gérer la réception d'un fichier ou dossier
        
        Args:
            client_socket: Socket du client
            address: Adresse du client
        """
        try:
            # Recevoir les métadonnées (première ligne)
            metadata = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            parts = metadata.split('|')
            filename = parts[0]
            filesize = int(parts[1])
            is_folder = parts[2] == 'folder' if len(parts) > 2 else False
            
            # Envoyer ACK
            client_socket.send(b'OK')
            
            # Recevoir le fichier
            filepath = os.path.join(self.storage_dir, filename)
            received = 0
            
            if is_folder:
                print(f"\nReception dossier: {filename.replace('.zip', '')} de {address[0]}")
            else:
                print(f"\nReception: {filename} de {address[0]}")
            
            # Barre de progression avec tqdm
            with open(filepath, 'wb') as f:
                with tqdm(total=filesize, unit='B', unit_scale=True, unit_divisor=1024, 
                         desc=filename[:30], ncols=80) as pbar:
                    while received < filesize:
                        chunk = client_socket.recv(min(CHUNK_SIZE, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                        pbar.update(len(chunk))
            
            # Si c'est un dossier, décompresser
            if is_folder:
                print(f"Decompression...")
                folder_name = filename.replace('.zip', '')
                extract_path = os.path.join(self.storage_dir, folder_name)
                
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                # Supprimer le zip
                os.remove(filepath)
                print(f"[OK] Dossier reçu: {extract_path}")
            else:
                print(f"[OK] Fichier reçu: {filepath}")
            
            # Vérifier le checksum
            if not is_folder:
                checksum = calculate_checksum(filepath)
                print(f"  Checksum: {checksum}")
            
            # Appeler le callback de notification
            if self.on_receive_callback:
                display_name = filename.replace('.zip', '') if is_folder else filename
                self.on_receive_callback(display_name, address[0], is_folder)
            
        except Exception as e:
            print(f"\n[X] Erreur réception: {e}")
        finally:
            client_socket.close()
    
    def send_file(self, filepath: str, peer_ip: str, peer_port: int) -> bool:
        """
        Envoyer un fichier à un PC
        
        Args:
            filepath: Chemin du fichier à envoyer
            peer_ip: IP du destinataire
            peer_port: Port du destinataire
            
        Returns:
            True si succès, False sinon
        """
        if not os.path.exists(filepath):
            print(f"[X] Fichier non trouvé: {filepath}")
            return False
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        try:
            # Connexion au destinataire
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            
            # Envoyer métadonnées
            metadata = f"{filename}|{filesize}".encode('utf-8')
            sock.send(metadata)
            
            # Attendre ACK
            ack = sock.recv(BUFFER_SIZE)
            if ack != b'OK':
                raise Exception("ACK non reçu")
            
            # Envoyer le fichier avec barre de progression
            sent = 0
            print(f"\nEnvoi: {filename} vers {peer_ip}:{peer_port}")
            
            with open(filepath, 'rb') as f:
                with tqdm(total=filesize, unit='B', unit_scale=True, unit_divisor=1024,
                         desc=filename[:30], ncols=80) as pbar:
                    while sent < filesize:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        sock.sendall(chunk)
                        sent += len(chunk)
                        pbar.update(len(chunk))
            
            print(f"[OK] Fichier envoyé avec succès")
            sock.close()
            return True
            
        except Exception as e:
            print(f"\n[X] Erreur envoi: {e}")
            return False
    
    def send_folder(self, folder_path: str, peer_ip: str, peer_port: int) -> bool:
        """
        Envoyer un dossier complet à un PC (compression automatique)
        
        Args:
            folder_path: Chemin du dossier à envoyer
            peer_ip: IP du destinataire
            peer_port: Port du destinataire
            
        Returns:
            True si succès, False sinon
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"[X] Dossier non trouvé: {folder_path}")
            return False
        
        folder_name = os.path.basename(folder_path)
        
        try:
            # Créer un fichier zip temporaire
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                zip_path = tmp_file.name
            
            print(f"\nCompression du dossier '{folder_name}'...")
            
            # Compresser le dossier
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                        zipf.write(file_path, arcname)
            
            zip_size = os.path.getsize(zip_path)
            print(f"[OK] Compression terminée: {format_size(zip_size)}")
            
            # Envoyer le zip
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((peer_ip, peer_port))
                
                # Envoyer métadonnées (inclure flag 'folder')
                metadata = f"{folder_name}.zip|{zip_size}|folder".encode('utf-8')
                sock.send(metadata)
                
                # Attendre ACK
                ack = sock.recv(BUFFER_SIZE)
                if ack != b'OK':
                    raise Exception("ACK non reçu")
                
                # Envoyer le fichier zip avec barre de progression
                sent = 0
                print(f"\nEnvoi dossier: {folder_name} vers {peer_ip}:{peer_port}")
                
                with open(zip_path, 'rb') as f:
                    with tqdm(total=zip_size, unit='B', unit_scale=True, unit_divisor=1024,
                             desc=folder_name[:30], ncols=80) as pbar:
                        while sent < zip_size:
                            chunk = f.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            sock.sendall(chunk)
                            sent += len(chunk)
                            pbar.update(len(chunk))
                
                print(f"[OK] Dossier envoyé avec succès")
                sock.close()
                return True
                
            finally:
                # Supprimer le fichier zip temporaire
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            
        except Exception as e:
            print(f"\n[X] Erreur envoi dossier: {e}")
            return False
    
    def list_received_files(self) -> list:
        """
        Lister les fichiers et dossiers reçus
        
        Returns:
            Liste des fichiers et dossiers
        """
        try:
            items = []
            for item_name in os.listdir(self.storage_dir):
                item_path = os.path.join(self.storage_dir, item_name)
                
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    items.append({
                        'name': item_name,
                        'size': size,
                        'path': item_path,
                        'type': 'file'
                    })
                elif os.path.isdir(item_path):
                    # Calculer la taille totale du dossier
                    total_size = 0
                    for root, dirs, files in os.walk(item_path):
                        for f in files:
                            fp = os.path.join(root, f)
                            total_size += os.path.getsize(fp)
                    
                    items.append({
                        'name': item_name,
                        'size': total_size,
                        'path': item_path,
                        'type': 'folder'
                    })
            return items
        except:
            return []
