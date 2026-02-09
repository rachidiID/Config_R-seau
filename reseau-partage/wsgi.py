"""
WSGI Entry Point pour PythonAnywhere
"""
import sys
import os

# Ajouter le répertoire du projet au path
project_home = '/home/VOTRE_USERNAME/reseau-partage'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importer l'application Flask
from server.main import app as application

# Désactiver le mode debug en production
application.config['DEBUG'] = False

# Configuration pour PythonAnywhere
application.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB sur plan gratuit
