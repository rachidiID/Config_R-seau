"""
Système de haute disponibilité avec plusieurs serveurs
Permet au réseau de fonctionner sans dépendre d'un seul PC
"""

import socket
import threading
import time
import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


# Configuration
HEARTBEAT_INTERVAL = 5  # Secondes entre chaque heartbeat
SERVER_TIMEOUT = 15  # Secondes avant de considérer un serveur mort
DISCOVERY_PORT = 5555  # Port UDP pour la découverte de serveurs
SYNC_INTERVAL = 30  # Intervalle de synchronisation DB (secondes)


@dataclass
class ServerInfo:
    """Information sur un serveur"""
    host: str
    port: int
    name: str
    is_primary: bool
    last_seen: float
    priority: int  # Plus élevé = prioritaire pour devenir primary
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return ServerInfo(**data)
    
    def is_alive(self) -> bool:
        """Vérifier si le serveur est toujours vivant"""
        return (time.time() - self.last_seen) < SERVER_TIMEOUT


class ServerDiscovery:
    """Gestionnaire de découverte et monitoring de serveurs"""
    
    def __init__(self, my_host: str, my_port: int, my_name: str, priority: int = 1):
        """
        Initialiser le système de découverte
        
        Args:
            my_host: Mon adresse IP
            my_port: Mon port HTTP
            my_name: Mon nom
            priority: Ma priorité (plus élevé = prioritaire)
        """
        self.my_info = ServerInfo(
            host=my_host,
            port=my_port,
            name=my_name,
            is_primary=False,
            last_seen=time.time(),
            priority=priority
        )
        
        self.known_servers: Dict[str, ServerInfo] = {}
        self.running = False
        self.discovery_socket = None
        self.primary_server: Optional[ServerInfo] = None
        
        # Lock pour thread-safety
        self.lock = threading.Lock()
    
    def start(self):
        """Démarrer le système de découverte"""
        self.running = True
        
        # Thread d'écoute (broadcast UDP)
        threading.Thread(target=self._listen_broadcasts, daemon=True).start()
        
        # Thread d'envoi heartbeat
        threading.Thread(target=self._send_heartbeats, daemon=True).start()
        
        # Thread de nettoyage des serveurs morts
        threading.Thread(target=self._cleanup_dead_servers, daemon=True).start()
        
        # Thread d'élection du serveur primaire
        threading.Thread(target=self._primary_election, daemon=True).start()
        
        print(f"[OK] Système de haute disponibilité démarré")
        print(f"     Serveur: {self.my_info.name} ({self.my_info.host}:{self.my_info.port})")
        print(f"     Priorité: {self.my_info.priority}")
    
    def stop(self):
        """Arrêter le système de découverte"""
        self.running = False
        if self.discovery_socket:
            self.discovery_socket.close()
    
    def _listen_broadcasts(self):
        """Écouter les broadcasts UDP des autres serveurs"""
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.discovery_socket.bind(('', DISCOVERY_PORT))
            self.discovery_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.discovery_socket.recvfrom(1024)
                    message = json.loads(data.decode('utf-8'))
                    
                    if message.get('type') == 'heartbeat':
                        server_data = message.get('server')
                        server_info = ServerInfo.from_dict(server_data)
                        server_info.last_seen = time.time()
                        
                        # Ne pas s'ajouter soi-même
                        if server_info.name != self.my_info.name:
                            with self.lock:
                                self.known_servers[server_info.name] = server_info
                                # print(f"[INFO] Serveur découvert: {server_info.name}")
                
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[!] Erreur écoute broadcast: {e}")
        
        except Exception as e:
            print(f"[X] Erreur initialisation écoute: {e}")
    
    def _send_heartbeats(self):
        """Envoyer des heartbeats périodiques en broadcast"""
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running:
            try:
                # Mettre à jour notre timestamp
                self.my_info.last_seen = time.time()
                
                # Créer le message
                message = {
                    'type': 'heartbeat',
                    'server': self.my_info.to_dict()
                }
                
                # Envoyer en broadcast
                data = json.dumps(message).encode('utf-8')
                broadcast_socket.sendto(data, ('<broadcast>', DISCOVERY_PORT))
                
            except Exception as e:
                if self.running:
                    print(f"[!] Erreur envoi heartbeat: {e}")
            
            time.sleep(HEARTBEAT_INTERVAL)
    
    def _cleanup_dead_servers(self):
        """Nettoyer les serveurs qui ne répondent plus"""
        while self.running:
            time.sleep(10)
            
            with self.lock:
                dead_servers = [
                    name for name, info in self.known_servers.items()
                    if not info.is_alive()
                ]
                
                for name in dead_servers:
                    print(f"[!] Serveur {name} est hors ligne")
                    del self.known_servers[name]
    
    def _primary_election(self):
        """Élire le serveur primaire (celui avec la plus haute priorité)"""
        while self.running:
            time.sleep(5)
            
            with self.lock:
                # Inclure notre propre serveur dans la liste
                all_servers = list(self.known_servers.values()) + [self.my_info]
                
                # Filtrer les serveurs vivants
                alive_servers = [s for s in all_servers if s.is_alive()]
                
                if not alive_servers:
                    continue
                
                # Trier par priorité (puis par nom pour déterminisme)
                alive_servers.sort(key=lambda s: (-s.priority, s.name))
                
                # Le premier est le primaire
                new_primary = alive_servers[0]
                
                # Si le primaire a changé
                if self.primary_server is None or self.primary_server.name != new_primary.name:
                    old_primary = self.primary_server.name if self.primary_server else "Aucun"
                    self.primary_server = new_primary
                    
                    # Mettre à jour notre statut
                    self.my_info.is_primary = (new_primary.name == self.my_info.name)
                    
                    print(f"[HA] Serveur primaire : {new_primary.name} (ancien: {old_primary})")
                    
                    if self.my_info.is_primary:
                        print(f"[HA] Je suis maintenant le serveur PRIMAIRE")
    
    def get_primary_server(self) -> Optional[ServerInfo]:
        """Obtenir le serveur primaire actuel"""
        with self.lock:
            return self.primary_server
    
    def get_all_servers(self) -> List[ServerInfo]:
        """Obtenir tous les serveurs connus (vivants)"""
        with self.lock:
            all_servers = list(self.known_servers.values()) + [self.my_info]
            return [s for s in all_servers if s.is_alive()]
    
    def am_i_primary(self) -> bool:
        """Vérifier si je suis le serveur primaire"""
        return self.my_info.is_primary
    
    def get_server_url(self, server: Optional[ServerInfo] = None) -> str:
        """
        Obtenir l'URL d'un serveur
        
        Args:
            server: Serveur cible (None = primaire)
            
        Returns:
            URL du serveur
        """
        if server is None:
            server = self.get_primary_server()
            if server is None:
                # Fallback sur nous-même
                server = self.my_info
        
        return f"http://{server.host}:{server.port}"


class DatabaseReplicator:
    """Gestionnaire de réplication de base de données entre serveurs"""
    
    def __init__(self, discovery: ServerDiscovery, db_path: str):
        """
        Initialiser le réplicateur
        
        Args:
            discovery: Instance de ServerDiscovery
            db_path: Chemin de la base de données locale
        """
        self.discovery = discovery
        self.db_path = db_path
        self.running = False
    
    def start(self):
        """Démarrer la réplication"""
        self.running = True
        threading.Thread(target=self._sync_loop, daemon=True).start()
        print(f"[OK] Réplication de base de données démarrée")
    
    def stop(self):
        """Arrêter la réplication"""
        self.running = False
    
    def _sync_loop(self):
        """Boucle de synchronisation périodique"""
        while self.running:
            time.sleep(SYNC_INTERVAL)
            
            # Si on n'est pas le primaire, synchroniser avec le primaire
            if not self.discovery.am_i_primary():
                self._pull_from_primary()
            else:
                # Si on est le primaire, pousser vers les autres
                self._push_to_replicas()
    
    def _pull_from_primary(self):
        """Récupérer les données depuis le serveur primaire"""
        primary = self.discovery.get_primary_server()
        if primary is None or primary.name == self.discovery.my_info.name:
            return
        
        try:
            url = f"{self.discovery.get_server_url(primary)}/api/db/export"
            response = requests.get(url, timeout=5)
            
            if response.ok:
                # Sauvegarder les données
                db_data = response.json()
                # TODO: Implémenter l'import dans la DB
                # print(f"[SYNC] Données synchronisées depuis {primary.name}")
        
        except Exception as e:
            # print(f"[!] Erreur sync depuis primaire: {e}")
            pass
    
    def _push_to_replicas(self):
        """Pousser les données vers les serveurs secondaires"""
        replicas = [s for s in self.discovery.get_all_servers() 
                   if s.name != self.discovery.my_info.name]
        
        for replica in replicas:
            try:
                # TODO: Implémenter l'export et l'envoi
                pass
            except Exception as e:
                # print(f"[!] Erreur sync vers {replica.name}: {e}")
                pass
