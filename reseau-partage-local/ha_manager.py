"""
Gestionnaire de Haute Disponibilité
Gère l'élection primaire/secondaire et la synchronisation
"""

import time
import threading
import requests
from typing import Optional, Dict

from config_local import SYNC_INTERVAL, SERVER_TIMEOUT


class HAManager:
    """Gestion de la Haute Disponibilité"""
    
    def __init__(self, discovery, database, is_server: bool):
        """
        Args:
            discovery: Instance de NetworkDiscovery
            database: Instance de Database
            is_server: True si ce nœud est un serveur
        """
        self.discovery = discovery
        self.database = database
        self.is_server = is_server
        
        self.role = None  # 'primary', 'secondary', ou None (client)
        self.sync_thread = None
        self.monitor_thread = None
        self.running = False
    
    def start(self):
        """Démarrer le gestionnaire HA"""
        if not self.is_server:
            return
        
        self.running = True
        
        # Déterminer rôle initial
        self._update_role()
        
        # Thread de synchronisation (si secondaire)
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        # Thread de monitoring (vérifier si primaire tombe)
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"✅ Gestionnaire HA démarré (rôle: {self.role})")
    
    def stop(self):
        """Arrêter le gestionnaire HA"""
        self.running = False
        print("🛑 Gestionnaire HA arrêté")
    
    def _update_role(self):
        """Mettre à jour le rôle (primaire/secondaire)"""
        old_role = self.role
        
        if self.discovery.am_i_primary():
            self.role = 'primary'
        else:
            self.role = 'secondary'
        
        if old_role != self.role:
            print(f"🔄 Changement de rôle : {old_role} → {self.role}")
            
            if self.role == 'primary':
                print("👑 Je suis maintenant le serveur PRIMAIRE")
            else:
                print("🔄 Je suis en mode SECONDAIRE (backup)")
    
    def _sync_loop(self):
        """Synchroniser avec le serveur primaire (secondaires uniquement)"""
        while self.running:
            try:
                self._update_role()
                
                # Si secondaire, synchroniser avec primaire
                if self.role == 'secondary':
                    primary = self.discovery.get_primary_server()
                    if primary and primary['name'] != self.discovery.node_name:
                        self._sync_with_primary(primary)
                
                time.sleep(SYNC_INTERVAL)
            except Exception as e:
                print(f"❌ Erreur sync : {e}")
                time.sleep(10)
    
    def _sync_with_primary(self, primary: Dict):
        """Synchroniser la DB avec le serveur primaire"""
        try:
            url = f"http://{primary['ip']}:{primary['port']}/api/sync/export"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                db_data = response.content
                self.database.import_db(db_data)
                print(f"✓ Synchronisé avec {primary['name']}")
        except requests.RequestException as e:
            print(f"⚠️  Échec sync avec {primary['name']}: {e}")
    
    def _monitor_loop(self):
        """Surveiller la disponibilité du primaire"""
        while self.running:
            try:
                primary = self.discovery.get_primary_server()
                
                if primary and primary['name'] != self.discovery.node_name:
                    # Vérifier si primaire répond
                    if not self._check_primary_alive(primary):
                        print(f"⚠️  Serveur primaire {primary['name']} injoignable")
                        # La découverte réseau le marquera comme offline
                        # et je deviendrai primaire automatiquement
                
                time.sleep(5)
            except Exception as e:
                print(f"❌ Erreur monitor : {e}")
    
    def _check_primary_alive(self, primary: Dict) -> bool:
        """Vérifier si le serveur primaire répond"""
        try:
            url = f"http://{primary['ip']}:{primary['port']}/api/health"
            response = requests.get(url, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self) -> Dict:
        """Obtenir le statut HA"""
        servers = self.discovery.get_servers()
        primary = self.discovery.get_primary_server()
        
        return {
            'ha_enabled': True,
            'role': self.role,
            'servers_count': len(servers),
            'primary_server': primary['name'] if primary else None,
            'servers': [
                {
                    'name': s['name'],
                    'ip': s['ip'],
                    'port': s['port'],
                    'is_primary': s['name'] == (primary['name'] if primary else None)
                }
                for s in servers
            ]
        }
