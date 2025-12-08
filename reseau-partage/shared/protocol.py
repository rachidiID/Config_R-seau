"""
Protocole de communication
Définit les messages échangés entre client et serveur
"""

from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json


class MessageType(Enum):
    """Types de messages"""
    # Connexion
    REGISTER = "register"           # Client s'enregistre
    UNREGISTER = "unregister"       # Client se déconnecte
    
    # Découverte
    LIST_PEERS = "list_peers"       # Demander liste des PC
    PEER_STATUS = "peer_status"     # Statut d'un PC
    
    # Transfert
    REQUEST_SEND = "request_send"   # Demander autorisation d'envoyer
    APPROVE_SEND = "approve_send"   # Serveur approuve l'envoi
    NOTIFY_RECEIVE = "notify_receive"  # Notifier réception
    
    # Permissions
    CHECK_PERMISSION = "check_permission"  # Vérifier droit d'accès
    
    # Réponses
    SUCCESS = "success"
    ERROR = "error"


class PermissionType(Enum):
    """Types de permissions"""
    PRIVATE = "private"    # 1 seul destinataire
    SHARED = "shared"      # Liste spécifique
    PUBLIC = "public"      # Tout le monde


@dataclass
class Message:
    """Message de base"""
    type: str
    data: Dict[str, Any]
    
    def to_json(self) -> str:
        """Convertir en JSON"""
        return json.dumps({
            'type': self.type,
            'data': self.data
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'Message':
        """Créer depuis JSON"""
        obj = json.loads(json_str)
        return Message(
            type=obj['type'],
            data=obj['data']
        )


@dataclass
class RegisterMessage:
    """Message d'enregistrement d'un client"""
    peer_name: str
    ip_address: str
    port: int
    
    def to_message(self) -> Message:
        return Message(
            type=MessageType.REGISTER.value,
            data=asdict(self)
        )


@dataclass
class FileTransferRequest:
    """Demande de transfert de fichier"""
    filename: str
    filesize: int
    checksum: str
    from_peer: str
    to_peers: List[str]
    permission: str  # private, shared, public
    
    def to_message(self) -> Message:
        return Message(
            type=MessageType.REQUEST_SEND.value,
            data=asdict(self)
        )


@dataclass
class PeerInfo:
    """Informations sur un PC"""
    name: str
    ip_address: str
    port: int
    status: str  # online, offline
    last_seen: str  # ISO timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Response:
    """Réponse du serveur"""
    
    @staticmethod
    def success(data: Dict[str, Any] = None) -> Message:
        """Réponse de succès"""
        return Message(
            type=MessageType.SUCCESS.value,
            data=data or {}
        )
    
    @staticmethod
    def error(message: str, code: int = 400) -> Message:
        """Réponse d'erreur"""
        return Message(
            type=MessageType.ERROR.value,
            data={
                'error': message,
                'code': code
            }
        )


# Constantes de configuration
DEFAULT_SERVER_PORT = 5000
DEFAULT_CLIENT_PORT = 5001
BUFFER_SIZE = 4096  # Taille du buffer pour transfert
CHUNK_SIZE = 1024 * 1024  # 1 MB par chunk
