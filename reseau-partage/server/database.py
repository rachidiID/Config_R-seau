"""
Base de données SQLite
Gère l'annuaire des PC et les permissions
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class Database:
    """Gestionnaire de base de données"""
    
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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Résultats comme dictionnaires
        return conn
    
    def init_database(self):
        """Créer les tables si elles n'existent pas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des PC (peers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ip_address TEXT NOT NULL,
                port INTEGER NOT NULL,
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
        
        # Table des permissions (qui peut accéder à quel fichier)
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
        
        # Table de l'historique des transferts
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
        print(f"[OK] Base de donnees initialisee : {self.db_path}")
    
    # ========================================
    # GESTION DES PEERS
    # ========================================
    
    def register_peer(self, name: str, ip: str, port: int) -> bool:
        """
        Enregistrer un nouveau PC
        
        Args:
            name: Nom du PC
            ip: Adresse IP
            port: Port
            
        Returns:
            True si succès, False si existe déjà
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO peers (name, ip_address, port, status, last_seen, created_at)
                VALUES (?, ?, ?, 'online', ?, ?)
            """, (name, ip, port, now, now))
            conn.commit()
            print(f"✓ PC enregistré : {name} ({ip}:{port})")
            return True
        except sqlite3.IntegrityError:
            # Déjà existe, mettre à jour
            cursor.execute("""
                UPDATE peers
                SET ip_address = ?, port = ?, status = 'online', last_seen = ?
                WHERE name = ?
            """, (ip, port, now, name))
            conn.commit()
            print(f"✓ PC mis à jour : {name}")
            return True
        finally:
            conn.close()
    
    def unregister_peer(self, name: str):
        """
        Déconnecter un PC
        
        Args:
            name: Nom du PC
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE peers
            SET status = 'offline'
            WHERE name = ?
        """, (name,))
        
        conn.commit()
        conn.close()
        print(f"✓ PC déconnecté : {name}")
    
    def get_all_peers(self) -> List[Dict]:
        """
        Obtenir tous les PC
        
        Returns:
            Liste des PC avec leurs infos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, ip_address, port, status, last_seen
            FROM peers
            ORDER BY name
        """)
        
        peers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return peers
    
    def get_online_peers(self) -> List[Dict]:
        """
        Obtenir les PC en ligne
        
        Returns:
            Liste des PC en ligne
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, ip_address, port, status, last_seen
            FROM peers
            WHERE status = 'online'
            ORDER BY name
        """)
        
        peers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return peers
    
    def get_peer(self, name: str) -> Optional[Dict]:
        """
        Obtenir un PC par son nom
        
        Args:
            name: Nom du PC
            
        Returns:
            Infos du PC ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, ip_address, port, status, last_seen
            FROM peers
            WHERE name = ?
        """, (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ========================================
    # GESTION DES FICHIERS
    # ========================================
    
    def register_file(self, filename: str, filesize: int, checksum: str,
                     owner: str, permission_type: str, recipients: List[str] = None) -> int:
        """
        Enregistrer un fichier partagé
        
        Args:
            filename: Nom du fichier
            filesize: Taille en octets
            checksum: Checksum MD5
            owner: Propriétaire
            permission_type: Type de permission (private, shared, public)
            recipients: Liste des destinataires (pour private/shared)
            
        Returns:
            ID du fichier créé
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # Insérer le fichier
        cursor.execute("""
            INSERT INTO files (filename, filesize, checksum, owner, permission_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, filesize, checksum, owner, permission_type, now))
        
        file_id = cursor.lastrowid
        
        # Ajouter les permissions
        if permission_type == 'public':
            # Tout le monde peut accéder
            pass  # On vérifie juste le type plus tard
        elif recipients:
            # Ajouter chaque destinataire
            for recipient in recipients:
                cursor.execute("""
                    INSERT INTO permissions (file_id, peer_name, granted_at)
                    VALUES (?, ?, ?)
                """, (file_id, recipient, now))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Fichier enregistré : {filename} (ID: {file_id})")
        return file_id
    
    def check_permission(self, file_id: int, peer_name: str) -> bool:
        """
        Vérifier si un PC a accès à un fichier
        
        Args:
            file_id: ID du fichier
            peer_name: Nom du PC
            
        Returns:
            True si accès autorisé, False sinon
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer le fichier
        cursor.execute("""
            SELECT permission_type, owner
            FROM files
            WHERE id = ?
        """, (file_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        permission_type = row['permission_type']
        owner = row['owner']
        
        # Le propriétaire a toujours accès
        if peer_name == owner:
            conn.close()
            return True
        
        # Public = tout le monde
        if permission_type == 'public':
            conn.close()
            return True
        
        # Private/Shared = vérifier la table permissions
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM permissions
            WHERE file_id = ? AND peer_name = ?
        """, (file_id, peer_name))
        
        count = cursor.fetchone()['count']
        conn.close()
        
        return count > 0
    
    def log_transfer(self, file_id: int, from_peer: str, to_peer: str, status: str):
        """
        Enregistrer un transfert
        
        Args:
            file_id: ID du fichier
            from_peer: Expéditeur
            to_peer: Destinataire
            status: Statut (success, failed)
        """
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
        """
        Obtenir les fichiers envoyés par un PC
        
        Args:
            peer_name: Nom du PC
            
        Returns:
            Liste des fichiers envoyés avec infos de transfert
        """
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
        """
        Obtenir les fichiers reçus par un PC
        
        Args:
            peer_name: Nom du PC
            
        Returns:
            Liste des fichiers reçus avec infos d'expéditeur
        """
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
