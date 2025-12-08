"""
Système de notifications desktop
"""

import sys
import os

# Essayer d'importer plyer pour les notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("[!] Module 'plyer' non disponible. Notifications désactivées.")


class NotificationManager:
    """Gestionnaire de notifications desktop"""
    
    def __init__(self, enabled: bool = True):
        """
        Initialiser le gestionnaire
        
        Args:
            enabled: Activer/désactiver les notifications
        """
        self.enabled = enabled and NOTIFICATIONS_AVAILABLE
        self.app_name = "Réseau P2P"
    
    def notify_file_received(self, filename: str, sender: str, is_folder: bool = False):
        """
        Notification de fichier/dossier reçu
        
        Args:
            filename: Nom du fichier/dossier
            sender: Nom de l'expéditeur
            is_folder: True si c'est un dossier
        """
        if not self.enabled:
            return
        
        try:
            item_type = "Dossier" if is_folder else "Fichier"
            title = f"{item_type} recu"
            message = f"{filename}\nDe: {sender}"
            
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=5  # 5 secondes
            )
        except Exception as e:
            # Silencieux en cas d'erreur
            pass
    
    def notify_transfer_complete(self, filename: str, recipient: str, is_folder: bool = False, success: bool = True):
        """
        Notification de transfert terminé
        
        Args:
            filename: Nom du fichier/dossier
            recipient: Nom du destinataire
            is_folder: True si c'est un dossier
            success: True si succès, False si échec
        """
        if not self.enabled:
            return
        
        try:
            item_type = "Dossier" if is_folder else "Fichier"
            
            if success:
                title = f"{item_type} envoye"
                message = f"{filename}\nA: {recipient}"
            else:
                title = f"Echec d'envoi"
                message = f"{filename}\nA: {recipient}"
            
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=5
            )
        except Exception as e:
            pass
    
    def notify_peer_connected(self, peer_name: str):
        """
        Notification de nouveau PC connecté
        
        Args:
            peer_name: Nom du PC
        """
        if not self.enabled:
            return
        
        try:
            notification.notify(
                title="PC connecte",
                message=f"{peer_name} est maintenant en ligne",
                app_name=self.app_name,
                timeout=3
            )
        except Exception as e:
            pass
    
    def notify_error(self, error_message: str):
        """
        Notification d'erreur
        
        Args:
            error_message: Message d'erreur
        """
        if not self.enabled:
            return
        
        try:
            notification.notify(
                title="Erreur",
                message=error_message,
                app_name=self.app_name,
                timeout=5
            )
        except Exception as e:
            pass
    
    def enable(self):
        """Activer les notifications"""
        if NOTIFICATIONS_AVAILABLE:
            self.enabled = True
    
    def disable(self):
        """Désactiver les notifications"""
        self.enabled = False
    
    def toggle(self):
        """Basculer l'état des notifications"""
        self.enabled = not self.enabled
        return self.enabled
