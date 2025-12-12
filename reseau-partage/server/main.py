"""
Serveur Central - Annuaire et Permissions
Projet: Réseau de partage de fichiers
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
import os
import shutil

# Ajouter le dossier parent au path pour importer shared
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from server.database import Database
from server.config import *
from shared.protocol import MessageType, PermissionType
from shared.utils import get_timestamp, calculate_checksum

# Initialiser Flask
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
app = Flask(__name__, 
            template_folder=os.path.join(web_dir, 'templates'),
            static_folder=os.path.join(web_dir, 'static'))
CORS(app)
app.config['DEBUG'] = DEBUG
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max

# Dossier de stockage pour les uploads web
WEB_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
os.makedirs(WEB_UPLOAD_DIR, exist_ok=True)

# Initialiser la base de données
db = Database(DATABASE_PATH)


# ========================================
# ROUTES - GESTION DES PEERS
# ========================================

@app.route('/api/register', methods=['POST'])
def register_peer():
    """Enregistrer un nouveau PC"""
    data = request.json
    
    name = data.get('name')
    ip = data.get('ip')
    port = data.get('port', DEFAULT_CLIENT_PORT)
    
    if not name or not ip:
        return jsonify({'error': 'Nom et IP requis'}), 400
    
    success = db.register_peer(name, ip, port)
    
    return jsonify({
        'status': 'registered',
        'peer': {
            'name': name,
            'ip': ip,
            'port': port
        }
    }), 200


@app.route('/api/unregister', methods=['POST'])
def unregister_peer():
    """Déconnecter un PC"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Nom requis'}), 400
    
    db.unregister_peer(name)
    
    return jsonify({'status': 'unregistered'}), 200


@app.route('/api/peers', methods=['GET'])
def list_peers():
    """Liste de tous les PC"""
    peers = db.get_all_peers()
    
    return jsonify({
        'peers': peers,
        'count': len(peers)
    }), 200


@app.route('/api/peers/online', methods=['GET'])
def list_online_peers():
    """Liste des PC en ligne"""
    peers = db.get_online_peers()
    
    return jsonify({
        'peers': peers,
        'count': len(peers)
    }), 200


@app.route('/api/peer/<name>', methods=['GET'])
def get_peer(name):
    """Obtenir les infos d'un PC"""
    peer = db.get_peer(name)
    
    if not peer:
        return jsonify({'error': 'PC non trouvé'}), 404
    
    return jsonify(peer), 200


# ========================================
# ROUTES - GESTION DES FICHIERS
# ========================================

@app.route('/api/file/register', methods=['POST'])
def register_file():
    """
    Enregistrer un fichier partagé
    
    Body:
        {
            "filename": "document.pdf",
            "filesize": 1024000,
            "checksum": "abc123...",
            "owner": "PC1",
            "permission": "private",  // private, shared, public
            "recipients": ["PC2", "PC3"]  // optionnel
        }
    """
    data = request.json
    
    filename = data.get('filename')
    filesize = data.get('filesize')
    checksum = data.get('checksum')
    owner = data.get('owner')
    permission = data.get('permission', 'private')
    recipients = data.get('recipients', [])
    
    # Validation
    if not all([filename, filesize, checksum, owner]):
        return jsonify({'error': 'Données incomplètes'}), 400
    
    # Vérifier que le propriétaire existe
    if not db.get_peer(owner):
        return jsonify({'error': f'PC {owner} non enregistré'}), 404
    
    # Vérifier que les destinataires existent
    if permission != 'public':
        for recipient in recipients:
            if not db.get_peer(recipient):
                return jsonify({'error': f'PC {recipient} non trouvé'}), 404
    
    # Enregistrer le fichier
    file_id = db.register_file(
        filename=filename,
        filesize=filesize,
        checksum=checksum,
        owner=owner,
        permission_type=permission,
        recipients=recipients
    )
    
    return jsonify({
        'status': 'registered',
        'file_id': file_id,
        'filename': filename,
        'permission': permission,
        'recipients': recipients if permission != 'public' else 'all'
    }), 200


@app.route('/api/file/<int:file_id>/check', methods=['POST'])
def check_permission(file_id):
    """
    Vérifier si un PC peut accéder à un fichier
    
    Body:
        {
            "peer_name": "PC2"
        }
    """
    data = request.json
    peer_name = data.get('peer_name')
    
    if not peer_name:
        return jsonify({'error': 'peer_name requis'}), 400
    
    allowed = db.check_permission(file_id, peer_name)
    
    return jsonify({
        'allowed': allowed,
        'file_id': file_id,
        'peer_name': peer_name
    }), 200


@app.route('/api/transfer/log', methods=['POST'])
def log_transfer():
    """
    Enregistrer un transfert
    
    Body:
        {
            "file_id": 1,
            "from_peer": "PC1",
            "to_peer": "PC2",
            "status": "success"  // success, failed
        }
    """
    data = request.json
    
    file_id = data.get('file_id')
    from_peer = data.get('from_peer')
    to_peer = data.get('to_peer')
    status = data.get('status', 'success')
    
    if not all([file_id, from_peer, to_peer]):
        return jsonify({'error': 'Données incomplètes'}), 400
    
    db.log_transfer(file_id, from_peer, to_peer, status)
    
    return jsonify({'status': 'logged'}), 200


@app.route('/api/files/sent/<peer_name>', methods=['GET'])
def get_sent_files(peer_name):
    """
    Obtenir les fichiers envoyés par un PC
    
    Args:
        peer_name: Nom du PC
    """
    files = db.get_sent_files(peer_name)
    return jsonify({'files': files, 'count': len(files)}), 200


@app.route('/api/files/received/<peer_name>', methods=['GET'])
def get_received_files(peer_name):
    """
    Obtenir les fichiers reçus par un PC
    
    Args:
        peer_name: Nom du PC
    """
    files = db.get_received_files(peer_name)
    return jsonify({'files': files, 'count': len(files)}), 200


@app.route('/api/file/upload', methods=['POST'])
def upload_file():
    """
    Upload réel d'un fichier depuis le navigateur
    Le fichier est stocké sur le serveur et les métadonnées enregistrées
    """
    # Vérifier qu'un fichier est présent
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    # Récupérer les métadonnées
    owner = request.form.get('owner')
    recipients_str = request.form.get('recipients', '')
    permission = request.form.get('permission', 'private')
    
    if not owner:
        return jsonify({'error': 'Propriétaire requis'}), 400
    
    # Parser les destinataires
    recipients = [r.strip() for r in recipients_str.split(',') if r.strip()] if recipients_str else []
    
    # Sécuriser le nom de fichier
    filename = secure_filename(file.filename)
    
    # Créer le dossier du propriétaire
    owner_dir = os.path.join(WEB_UPLOAD_DIR, owner)
    os.makedirs(owner_dir, exist_ok=True)
    
    # Sauvegarder le fichier
    filepath = os.path.join(owner_dir, filename)
    file.save(filepath)
    
    # Calculer le checksum et la taille
    filesize = os.path.getsize(filepath)
    checksum = calculate_checksum(filepath)
    
    # Enregistrer dans la base de données
    file_id = db.register_file(
        filename=filename,
        filesize=filesize,
        checksum=checksum,
        owner=owner,
        permission_type=permission,
        recipients=recipients
    )
    
    # Copier le fichier vers chaque destinataire
    for recipient in recipients:
        recipient_dir = os.path.join(WEB_UPLOAD_DIR, recipient)
        os.makedirs(recipient_dir, exist_ok=True)
        recipient_filepath = os.path.join(recipient_dir, filename)
        
        # Copier le fichier
        shutil.copy2(filepath, recipient_filepath)
        
        # Logger le transfert
        db.log_transfer(file_id, owner, recipient, 'success')
    
    return jsonify({
        'status': 'success',
        'file_id': file_id,
        'filename': filename,
        'filesize': filesize,
        'checksum': checksum,
        'recipients': recipients
    }), 200


# ========================================
# ROUTES - INFORMATIONS
# ========================================

@app.route('/api/status', methods=['GET'])
def server_status():
    """Statut du serveur"""
    peers = db.get_all_peers()
    online = [p for p in peers if p['status'] == 'online']
    
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'peers_total': len(peers),
        'peers_online': len(online),
        'timestamp': get_timestamp()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Page d'accueil API"""
    return """
    <h1>Serveur de Partage P2P</h1>
    <p>Le serveur est en ligne et fonctionne.</p>
    <h2>Liens:</h2>
    <ul>
        <li><a href="/web">Interface Web</a></li>
        <li><a href="/api/status">Statut du serveur (API)</a></li>
    </ul>
    <h2>API Endpoints:</h2>
    <ul>
        <li><b>POST</b> /api/register - Enregistrer un PC</li>
        <li><b>POST</b> /api/unregister - Déconnecter un PC</li>
        <li><b>GET</b> /api/peers - Liste tous les PC</li>
        <li><b>GET</b> /api/peers/online - PC en ligne</li>
        <li><b>GET</b> /api/peer/&lt;name&gt; - Info d'un PC</li>
        <li><b>POST</b> /api/file/register - Enregistrer un fichier</li>
        <li><b>POST</b> /api/file/&lt;id&gt;/check - Vérifier permission</li>
        <li><b>POST</b> /api/transfer/log - Logger un transfert</li>
        <li><b>GET</b> /api/status - Statut du serveur</li>
    </ul>
    """, 200


@app.route('/web')
def web_interface():
    """Interface web"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir les fichiers statiques"""
    return send_from_directory(app.static_folder, filename)


# ========================================
# POINT D'ENTRÉE
# ========================================

def main():
    """Démarrer le serveur"""
    print("=" * 50)
    print("SERVEUR DE PARTAGE P2P")
    print("=" * 50)
    print(f"Host: {SERVER_HOST}")
    print(f"Port: {SERVER_PORT}")
    print(f"Base de données: {DATABASE_PATH}")
    print("=" * 50)
    print("\nServeur démarré ! Utilisez Ctrl+C pour arrêter.\n")
    
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG
    )


if __name__ == '__main__':
    main()
