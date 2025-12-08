"""
Utilitaires partagés
"""

import hashlib
import os
from datetime import datetime
from typing import Optional


def calculate_checksum(filepath: str) -> str:
    """
    Calculer le checksum MD5 d'un fichier
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        Checksum MD5 en hexadécimal
    """
    hash_md5 = hashlib.md5()
    
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def format_size(size_bytes: int) -> str:
    """
    Formater une taille en octets
    
    Args:
        size_bytes: Taille en octets
        
    Returns:
        Chaîne formatée (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_timestamp() -> str:
    """
    Obtenir le timestamp actuel au format ISO
    
    Returns:
        Timestamp ISO 8601
    """
    return datetime.utcnow().isoformat()


def validate_filename(filename: str) -> bool:
    """
    Valider un nom de fichier
    
    Args:
        filename: Nom du fichier
        
    Returns:
        True si valide, False sinon
    """
    # Caractères interdits
    forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    if not filename or len(filename) > 255:
        return False
    
    for char in forbidden:
        if char in filename:
            return False
    
    return True


def get_local_ip() -> Optional[str]:
    """
    Obtenir l'adresse IP locale
    
    Returns:
        Adresse IP ou None
    """
    import socket
    
    try:
        # Créer une socket UDP (pas besoin d'être connecté)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def create_directory(path: str) -> bool:
    """
    Créer un répertoire s'il n'existe pas
    
    Args:
        path: Chemin du répertoire
        
    Returns:
        True si créé ou existe, False en cas d'erreur
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erreur création répertoire {path}: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Nettoyer un nom de fichier
    
    Args:
        filename: Nom du fichier
        
    Returns:
        Nom nettoyé
    """
    # Remplacer les caractères interdits par _
    forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    for char in forbidden:
        filename = filename.replace(char, '_')
    
    return filename.strip()
