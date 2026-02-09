"""
Serveur Flask Local avec Haute Disponibilité
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sys
import shutil
import secrets
import hashlib
import json

from config_local import *
from database import Database
from discovery import NetworkDiscovery
from ha_manager import HAManager


# Initialiser Flask
app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)
app.config['DEBUG'] = DEBUG
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Base de données
db = Database(DATABASE_PATH)

# Découverte réseau et HA (initialisés dans main)
discovery = None
ha_manager = None

# Authentification
AUTH_FILE = os.path.join(os.path.dirname(__file__), 'network_auth.json')
PORTS_IN_USE = set()


# ========================================
# FONCTIONS D'AUTHENTIFICATION
# ========================================

def load_auth_data():
    """Charger les données d'authentification"""
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return {'network_password_hash': None, 'users': {}, 'next_port': 5001}

def save_auth_data(data):
    """Sauvegarder les données d'authentification"""
    with open(AUTH_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    """Hasher un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Générer un token de session"""
    return secrets.token_urlsafe(32)

def get_available_port():
    """Trouver un port disponible"""
    auth_data = load_auth_data()
    port = auth_data.get('next_port', 5001)
    
    while port in PORTS_IN_USE:
        port += 1
    
    PORTS_IN_USE.add(port)
    auth_data['next_port'] = port + 1
    save_auth_data(auth_data)
    
    return port


# ========================================
# ROUTES - SANTÉ DU SERVEUR
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier que le serveur est vivant (pour monitoring HA)"""
    return jsonify({'status': 'ok', 'role': ha_manager.role if ha_manager else 'unknown'}), 200


@app.route('/api/ha/status', methods=['GET'])
def ha_status():
    """État de la Haute Disponibilité"""
    if ha_manager:
        return jsonify(ha_manager.get_status()), 200
    return jsonify({'ha_enabled': False}), 200


# ========================================
# ROUTES - SYNCHRONISATION (HA)
# ========================================

@app.route('/api/sync/export', methods=['GET'])
def sync_export():
    """Exporter la DB pour synchronisation (primaire seulement)"""
    if ha_manager and ha_manager.role == 'primary':
        db_data = db.export_db()
        return db_data, 200, {'Content-Type': 'application/octet-stream'}
    return jsonify({'error': 'Non autorisé'}), 403


# ========================================
# ROUTES - GESTION DES PEERS
# ========================================

@app.route('/api/register', methods=['POST'])
def register_peer():
    """Enregistrer un nouveau peer"""
    data = request.json
    
    name = data.get('name')
    ip = data.get('ip')
    port = data.get('port', 5000)
    role = data.get('role', 'client')
    
    if not name or not ip:
        return jsonify({'error': 'Nom et IP requis'}), 400
    
    success = db.register_peer(name, ip, port, role)
    
    return jsonify({
        'status': 'registered',
        'peer': {'name': name, 'ip': ip, 'port': port, 'role': role}
    }), 200


@app.route('/api/unregister', methods=['POST'])
def unregister_peer():
    """Déconnecter un peer"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Nom requis'}), 400
    
    db.unregister_peer(name)
    return jsonify({'status': 'unregistered'}), 200


@app.route('/api/peers', methods=['GET'])
def list_peers():
    """Liste de tous les peers"""
    peers = db.get_all_peers()
    return jsonify({'peers': peers, 'count': len(peers)}), 200


@app.route('/api/peers/online', methods=['GET'])
def list_online_peers():
    """Liste des peers en ligne"""
    peers = db.get_online_peers()
    return jsonify({'peers': peers, 'count': len(peers)}), 200


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Signal de vie d'un peer"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'name requis'}), 400
    
    db.update_peer_last_seen(name)
    return jsonify({'status': 'ok'}), 200


# ========================================
# ROUTES - GESTION DES FICHIERS
# ========================================

@app.route('/api/file/upload', methods=['POST'])
def upload_file():
    """Upload d'un fichier"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    owner = request.form.get('owner')
    recipients = request.form.get('recipients', '').split(',')
    recipients = [r.strip() for r in recipients if r.strip()]
    
    if not owner:
        return jsonify({'error': 'Propriétaire requis'}), 400
    
    # Sauvegarder le fichier
    filename = secure_filename(file.filename)
    owner_dir = os.path.join(STORAGE_PATH, owner)
    os.makedirs(owner_dir, exist_ok=True)
    filepath = os.path.join(owner_dir, filename)
    file.save(filepath)
    
    # Calculer checksum
    import hashlib
    with open(filepath, 'rb') as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    
    filesize = os.path.getsize(filepath)
    
    # Enregistrer dans DB
    permission_type = 'shared' if len(recipients) > 1 else 'private'
    file_id = db.register_file(filename, filesize, checksum, owner, permission_type, recipients)
    
    # Copier vers les destinataires
    for recipient in recipients:
        recipient_dir = os.path.join(STORAGE_PATH, recipient)
        os.makedirs(recipient_dir, exist_ok=True)
        recipient_path = os.path.join(recipient_dir, filename)
        
        try:
            shutil.copy2(filepath, recipient_path)
            db.log_transfer(file_id, owner, recipient, 'success')
        except Exception as e:
            print(f"❌ Erreur copie vers {recipient}: {e}")
            db.log_transfer(file_id, owner, recipient, 'failed')
    
    return jsonify({
        'status': 'uploaded',
        'file_id': file_id,
        'filename': filename,
        'recipients': recipients
    }), 200


@app.route('/api/file/download/<peer_name>/<filename>', methods=['GET'])
def download_file(peer_name, filename):
    """Télécharger un fichier"""
    file_dir = os.path.join(STORAGE_PATH, peer_name)
    file_path = os.path.join(file_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Fichier introuvable'}), 404
    
    # Vérifier permissions
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count FROM transfers t
        JOIN files f ON t.file_id = f.id
        WHERE f.filename = ? AND t.to_peer = ? AND t.status = 'success'
    """, (filename, peer_name))
    
    result = dict(cursor.fetchone())
    conn.close()
    
    if result['count'] == 0:
        return jsonify({'error': 'Accès refusé : ce fichier ne vous est pas destiné'}), 403
    
    return send_from_directory(file_dir, filename, as_attachment=True)


@app.route('/api/files/sent/<peer_name>', methods=['GET'])
def get_sent_files(peer_name):
    """Fichiers envoyés par un peer"""
    files = db.get_sent_files(peer_name)
    return jsonify({'files': files, 'count': len(files)}), 200


@app.route('/api/files/received/<peer_name>', methods=['GET'])
def get_received_files(peer_name):
    """Fichiers reçus par un peer"""
    files = db.get_received_files(peer_name)
    return jsonify({'files': files, 'count': len(files)}), 200


# ========================================
# ROUTES - AUTHENTIFICATION
# ========================================

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Connexion au réseau"""
    data = request.json
    name = data.get('name')
    password = data.get('password')
    
    if not name or not password:
        return jsonify({'error': 'Nom et mot de passe requis'}), 400
    
    password_hash = hash_password(password)
    auth_data = load_auth_data()
    
    # Premier utilisateur : créer le réseau
    if not auth_data['network_password_hash']:
        auth_data['network_password_hash'] = password_hash
        print(f"🔐 Réseau créé avec mot de passe par {name}")
    else:
        # Vérifier mot de passe
        if password_hash != auth_data['network_password_hash']:
            return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    # Générer token
    token = generate_token()
    port = get_available_port()
    
    auth_data['users'][name] = {
        'token': token,
        'port': port,
        'created_at': datetime.utcnow().isoformat()
    }
    save_auth_data(auth_data)
    
    return jsonify({
        'status': 'connected',
        'token': token,
        'port': port,
        'message': 'Connexion réussie'
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Déconnexion"""
    data = request.json
    name = data.get('name')
    
    if name:
        auth_data = load_auth_data()
        if name in auth_data['users']:
            port = auth_data['users'][name].get('port')
            if port:
                PORTS_IN_USE.discard(port)
            
            del auth_data['users'][name]
            save_auth_data(auth_data)
    
    return jsonify({'status': 'disconnected'}), 200


# ========================================
# ROUTES - INTERFACE WEB
# ========================================

@app.route('/web')
def web_login():
    """Page de connexion"""
    return render_template('login.html')


@app.route('/web/app')
def web_app():
    """Interface principale"""
    return render_template('index.html')


# ========================================
# TÂCHES DE FOND
# ========================================

def scheduled_cleanup():
    """Tâche planifiée : nettoyer peers inactifs"""
    updated = db.update_peers_status()
    if updated > 0:
        print(f"Statuts mis à jour : {updated} peer(s) marqués offline")
    
    deleted = db.cleanup_inactive_peers()


# Initialiser le scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_cleanup, trigger="interval", minutes=5)


# ========================================
# POINT D'ENTRÉE
# ========================================

def start_server(node_name: str, is_server: bool = True):
    """
    Démarrer le serveur local
    
    Args:
        node_name: Nom du nœud
        is_server: True si ce nœud est un serveur, False si client
    """
    global discovery, ha_manager
    
    print("=" * 60)
    print("SERVEUR LOCAL P2P AVEC HAUTE DISPONIBILITÉ")
    print("=" * 60)
    print(f"Nom: {node_name}")
    print(f"Rôle: {'SERVEUR' if is_server else 'CLIENT'}")
    print(f"Port: {SERVER_PORT}")
    print(f"Base de données: {DATABASE_PATH}")
    print("=" * 60)
    
    # Initialiser découverte réseau
    discovery = NetworkDiscovery(node_name, 'server' if is_server else 'client', SERVER_PORT)
    discovery.start()
    
    # Attendre un peu pour découvrir d'autres serveurs
    import time
    time.sleep(2)
    
    # Initialiser HA
    ha_manager = HAManager(discovery, db, is_server)
    ha_manager.start()
    
    # Démarrer scheduler
    scheduler.start()
    
    # Afficher statut
    if is_server:
        print(f"\n🚀 Serveur démarré : http://{discovery.get_local_ip()}:{SERVER_PORT}")
        print(f"📊 Rôle HA : {ha_manager.role.upper()}")
        
        servers = discovery.get_servers()
        if len(servers) > 1:
            print(f"🔗 Serveurs dans le réseau : {len(servers)}")
            for s in servers:
                status = "👑 PRIMAIRE" if s['name'] == discovery.get_primary_server()['name'] else "🔄 SECONDAIRE"
                print(f"   - {s['name']} ({s['ip']}) {status}")
    
    print("\n✅ Utilisez Ctrl+C pour arrêter.\n")
    
    # Lancer Flask
    try:
        app.run(
            host=WEB_HOST,
            port=SERVER_PORT,
            debug=DEBUG,
            use_reloader=False  # Important : éviter double démarrage
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        scheduler.shutdown()
        if discovery:
            discovery.stop()
        if ha_manager:
            ha_manager.stop()
        print("✅ Serveur arrêté proprement")


# Point d'entrée WSGI pour production (optionnel)
application = app


if __name__ == '__main__':
    if len(sys.argv) > 1:
        node_name = sys.argv[1]
    else:
        node_name = input("Nom du nœud (ex: PC1): ")
    
    start_server(node_name, is_server=True)
