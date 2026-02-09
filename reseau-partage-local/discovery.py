"""
Module de découverte réseau (UDP Broadcast)
Permet aux serveurs et clients de se trouver automatiquement sur le LAN
"""

import socket
import json
import threading
import time
import netifaces
from datetime import datetime
from typing import List, Dict, Optional

from config_local import DISCOVERY_PORT, BROADCAST_INTERVAL, SERVER_TIMEOUT


class NetworkDiscovery:
    """Gestion de la découverte réseau par broadcast UDP"""
    
    def __init__(self, node_name: str, node_type: str, server_port: int):
        """
        Args:
            node_name: Nom du nœud (PC1, PC2...)
            node_type: 'server' ou 'client'
            server_port: Port du serveur Flask
        """
        self.node_name = node_name
        self.node_type = node_type
        self.server_port = server_port
        
        # Serveurs découverts {ip: {name, port, last_seen, priority}}
        self.discovered_servers = {}
        self.lock = threading.Lock()
        
        # Sockets
        self.broadcast_socket = None
        self.listen_socket = None
        
        # Threads
        self.broadcast_thread = None
        self.listen_thread = None
        self.cleanup_thread = None
        self.running = False
    
    def get_local_ip(self) -> str:
        """Obtenir l'IP locale du PC"""
        try:
            # Essayer de trouver l'IP sur le réseau local
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr['addr']
                        # Ignorer localhost et IPs virtuelles
                        if not ip.startswith('127.') and not ip.startswith('169.254.'):
                            return ip
        except:
            pass
        
        # Fallback : connexion dummy pour trouver l'IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def start(self):
        """Démarrer la découverte réseau"""
        if self.running:
            return
        
        self.running = True
        
        # Socket pour envoyer des broadcasts
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Socket pour écouter les broadcasts
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', DISCOVERY_PORT))
        
        # Démarrer les threads
        if self.node_type == 'server':
            self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
            self.broadcast_thread.start()
        
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        print(f"✅ Découverte réseau démarrée (IP: {self.get_local_ip()})")
    
    def stop(self):
        """Arrêter la découverte"""
        self.running = False
        
        if self.broadcast_socket:
            self.broadcast_socket.close()
        if self.listen_socket:
            self.listen_socket.close()
        
        print("🛑 Découverte réseau arrêtée")
    
    def _broadcast_loop(self):
        """Envoyer périodiquement des annonces (serveurs seulement)"""
        while self.running:
            try:
                message = {
                    'type': 'SERVER_ANNOUNCE',
                    'name': self.node_name,
                    'ip': self.get_local_ip(),
                    'port': self.server_port,
                    'timestamp': datetime.utcnow().isoformat(),
                    'priority': self._calculate_priority()
                }
                
                data = json.dumps(message).encode('utf-8')
                self.broadcast_socket.sendto(data, ('<broadcast>', DISCOVERY_PORT))
                
                time.sleep(BROADCAST_INTERVAL)
            except Exception as e:
                if self.running:
                    print(f"❌ Erreur broadcast : {e}")
                time.sleep(1)
    
    def _listen_loop(self):
        """Écouter les annonces réseau"""
        self.listen_socket.settimeout(1.0)
        
        while self.running:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                
                # Ignorer ses propres messages
                if message.get('name') == self.node_name:
                    continue
                
                if message['type'] == 'SERVER_ANNOUNCE':
                    self._handle_server_announce(message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"❌ Erreur écoute : {e}")
    
    def _handle_server_announce(self, message: dict):
        """Traiter une annonce de serveur"""
        ip = message['ip']
        
        with self.lock:
            if ip not in self.discovered_servers:
                print(f"🔍 Serveur découvert : {message['name']} ({ip}:{message['port']})")
            
            self.discovered_servers[ip] = {
                'name': message['name'],
                'ip': ip,
                'port': message['port'],
                'priority': message.get('priority', 0),
                'last_seen': time.time()
            }
    
    def _cleanup_loop(self):
        """Nettoyer les serveurs inactifs"""
        while self.running:
            try:
                now = time.time()
                to_remove = []
                
                with self.lock:
                    for ip, info in self.discovered_servers.items():
                        if now - info['last_seen'] > SERVER_TIMEOUT:
                            to_remove.append(ip)
                    
                    for ip in to_remove:
                        print(f"⚠️  Serveur perdu : {self.discovered_servers[ip]['name']} ({ip})")
                        del self.discovered_servers[ip]
                
                time.sleep(5)
            except Exception as e:
                print(f"❌ Erreur cleanup : {e}")
    
    def _calculate_priority(self) -> int:
        """Calculer la priorité de ce serveur (pour élection primaire)"""
        # Basé sur le nom (ordre alphabétique inversé)
        # PC1 > PC2 > PC3...
        return -ord(self.node_name[-1]) if self.node_name else 0
    
    def get_servers(self) -> List[Dict]:
        """Obtenir la liste des serveurs découverts"""
        with self.lock:
            return sorted(
                self.discovered_servers.values(),
                key=lambda s: s['priority'],
                reverse=True
            )
    
    def get_primary_server(self) -> Optional[Dict]:
        """Obtenir le serveur primaire (plus haute priorité)"""
        servers = self.get_servers()
        return servers[0] if servers else None
    
    def am_i_primary(self) -> bool:
        """Vérifier si ce nœud est le serveur primaire"""
        if self.node_type != 'server':
            return False
        
        primary = self.get_primary_server()
        if not primary:
            return True  # Aucun autre serveur, je suis primaire
        
        return primary['name'] == self.node_name
