"""
Configuration du serveur
"""

import os

# Réseau
SERVER_HOST = '0.0.0.0'  # Écouter sur toutes les interfaces
SERVER_PORT = 5000
DEFAULT_CLIENT_PORT = 5001  # Port par défaut pour les clients

# Base de données
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'network.db')

# Timeouts
PEER_TIMEOUT = 60  # Secondes avant de considérer un peer hors ligne
CLEANUP_INTERVAL = 30  # Intervalle de nettoyage (secondes)

# Transfert
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1 GB max
ALLOWED_EXTENSIONS = None  # None = tous les fichiers autorisés

# Sécurité
ENABLE_AUTH = False  # Authentification simple (pour plus tard)
SECRET_KEY = 'dev-secret-key-change-in-production'

# Debug
DEBUG = True
