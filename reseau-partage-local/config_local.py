"""
Configuration pour la version locale
"""

import os

# Réseau Local
DISCOVERY_PORT = 5555        # Port UDP pour découverte réseau
SERVER_PORT = 5000           # Port HTTP du serveur Flask
BROADCAST_INTERVAL = 10      # Secondes entre chaque broadcast
HEARTBEAT_INTERVAL = 120     # 2 minutes

# Timeouts
SERVER_TIMEOUT = 15          # Secondes avant de considérer serveur offline
ELECTION_TIMEOUT = 5         # Temps d'attente pour élection

# Base de données
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'network.db')

# Stockage
STORAGE_PATH = os.path.join(os.path.dirname(__file__), 'storage')
os.makedirs(STORAGE_PATH, exist_ok=True)

# Haute Disponibilité
HA_ENABLED = True            # Toujours activé en local
SYNC_INTERVAL = 60           # Synchronisation DB toutes les 60s
MAX_SERVERS = 10             # Max serveurs simultanés

# Sécurité
DEBUG = False
SECRET_KEY = os.urandom(24)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

# Web Interface
WEB_HOST = '0.0.0.0'         # Écoute sur toutes les interfaces
WEB_PORT = 5000

# Logs
LOG_LEVEL = 'INFO'
LOG_FILE = 'reseau-local.log'
