"""
Base de données SQLite pour version locale
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class Database:
    """Gestionnaire de base de données locale"""
    
    def __init__(self, db_path: str):
        """
        Initialiser la base de données
        
        Args:
            db_path: Chemin du fichier SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Obtenir une connexion à la base"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Créer les tables si elles n'existent pas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des peers (PC connectés)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ip_address TEXT NOT NULL,
                port INTEGER NOT NULL,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'online',
                last_seen TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Table des fichiers partagés
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filesize INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                owner TEXT NOT NULL,
                permission_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (owner) REFERENCES peers(name)
            )
        """)
        
        # Table des permissions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                peer_name TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (peer_name) REFERENCES peers(name)
            )
        """)
        
        # Table des transferts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                from_peer TEXT NOT NULL,
                to_peer TEXT NOT NULL,
                status TEXT NOT NULL,
                transferred_at TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Base de données initialisée : {self.db_path}")
    
    def register_peer(self, name: str, ip: str, port: int, role: str) -> bool:
        """
        Enregistrer un peer
        
        Args:
            name: Nom du PC
            ip: Adresse IP
            port: Port
            role: 'server' ou 'client'
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO peers (name, ip_address, port, role, status, last_seen, created_at)
                VALUES (?, ?, ?, ?, 'online', ?, ?)
            """, (name, ip, port, role, now, now))
            conn.commit()
            print(f"✓ Peer enregistré : {name} ({role}) - {ip}:{port}")
            return True
        except sqlite3.IntegrityError:
            # Déjà existe, mettre à jour
            cursor.execute("""
                UPDATE peers
                SET ip_address = ?, port = ?, role = ?, status = 'online', last_seen = ?
                WHERE name = ?
            """, (ip, port, role, now, name))
            conn.commit()
            print(f"✓ Peer mis à jour : {name}")
            return True
        finally:
            conn.close()
    
    def unregister_peer(self, name: str):
        """Déconnecter un peer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE peers
            SET status = 'offline'
            WHERE name = ?
        """, (name,))
        
        conn.commit()
        conn.close()
        print(f"✓ Peer déconnecté : {name}")
    
    def get_all_peers(self) -> List[Dict]:
        """Obtenir tous les peers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, ip_address, port, role, status, last_seen
            FROM peers
            ORDER BY name
        """)
        
        peers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return peers
    
    def get_online_peers(self) -> List[Dict]:
        """Obtenir les peers en ligne"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, ip_address, port, role, status, last_seen
            FROM peers
            WHERE status = 'online'
            ORDER BY name
        """)
        
        peers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return peers
    
    def update_peer_last_seen(self, name: str):
        """Mettre à jour last_seen (heartbeat)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            UPDATE peers
            SET last_seen = ?, status = 'online'
            WHERE name = ?
        """, (now, name))
        
        conn.commit()
        conn.close()
    
    def update_peers_status(self):
        """Marquer offline les peers inactifs >5 min"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE peers
            SET status = 'offline'
            WHERE status = 'online'
            AND datetime(last_seen) < datetime('now', '-5 minutes')
        """)
        
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        return updated
    
    def cleanup_inactive_peers(self):
        """Supprimer les peers inactifs >10h"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM peers
            WHERE datetime(last_seen) < datetime('now', '-10 hours')
        """)
        
        peers_to_delete = [row['name'] for row in cursor.fetchall()]
        
        cursor.execute("""
            DELETE FROM peers
            WHERE datetime(last_seen) < datetime('now', '-10 hours')
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            print(f"✓ Nettoyage : {deleted} peer(s) supprimé(s): {', '.join(peers_to_delete)}")
        
        return deleted
    
    def register_file(self, filename: str, filesize: int, checksum: str, 
                     owner: str, permission_type: str, recipients: List[str]) -> int:
        """Enregistrer un fichier partagé"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO files (filename, filesize, checksum, owner, permission_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, filesize, checksum, owner, permission_type, now))
        
        file_id = cursor.lastrowid
        
        # Ajouter permissions
        for recipient in recipients:
            cursor.execute("""
                INSERT INTO permissions (file_id, peer_name, granted_at)
                VALUES (?, ?, ?)
            """, (file_id, recipient, now))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Fichier enregistré : {filename} (ID: {file_id})")
        return file_id
    
    def log_transfer(self, file_id: int, from_peer: str, to_peer: str, status: str):
        """Enregistrer un transfert"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO transfers (file_id, from_peer, to_peer, status, transferred_at)
            VALUES (?, ?, ?, ?, ?)
        """, (file_id, from_peer, to_peer, status, now))
        
        conn.commit()
        conn.close()
    
    def get_sent_files(self, peer_name: str) -> List[Dict]:
        """Obtenir les fichiers envoyés par un peer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT 
                f.id, f.filename, f.filesize, f.checksum, 
                f.created_at,
                GROUP_CONCAT(t.to_peer) as recipients,
                COUNT(DISTINCT t.to_peer) as recipient_count
            FROM files f
            LEFT JOIN transfers t ON f.id = t.file_id AND t.status = 'success'
            WHERE f.owner = ?
            GROUP BY f.id
            ORDER BY f.created_at DESC
        """, (peer_name,))
        
        files = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return files
    
    def get_received_files(self, peer_name: str) -> List[Dict]:
        """Obtenir les fichiers reçus par un peer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                f.id, f.filename, f.filesize, f.checksum,
                f.owner as sender,
                t.transferred_at,
                t.status
            FROM files f
            JOIN transfers t ON f.id = t.file_id
            WHERE t.to_peer = ? AND t.status = 'success'
            ORDER BY t.transferred_at DESC
        """, (peer_name,))
        
        files = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return files
    
    def export_db(self) -> bytes:
        """Exporter la base de données (pour synchronisation)"""
        with open(self.db_path, 'rb') as f:
            return f.read()
    
    def import_db(self, data: bytes):
        """Importer une base de données (synchronisation)"""
        backup_path = self.db_path + '.backup'
        
        # Backup de l'ancienne DB
        if os.path.exists(self.db_path):
            with open(self.db_path, 'rb') as f:
                with open(backup_path, 'wb') as bf:
                    bf.write(f.read())
        
        # Écrire la nouvelle DB
        with open(self.db_path, 'wb') as f:
            f.write(data)
        
        print("✓ Base de données synchronisée")
