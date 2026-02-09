"""
Système de fragmentation de fichiers pour les gros fichiers (>1GB)
Divise les fichiers en chunks et les distribue sur plusieurs PCs
"""

import os
import json
import hashlib
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict


# Configuration
CHUNK_SIZE = 256 * 1024 * 1024  # 256 MB par chunk
FRAGMENTATION_THRESHOLD = 1024 * 1024 * 1024  # 1 GB - seuil pour fragmenter
REDUNDANCY_FACTOR = 2  # Chaque chunk sur 2 PCs minimum


@dataclass
class ChunkInfo:
    """Information sur un fragment de fichier"""
    chunk_id: int
    chunk_hash: str
    chunk_size: int
    stored_on: List[str]  # Liste des PCs qui ont ce chunk
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return ChunkInfo(**data)


@dataclass
class FragmentedFileMetadata:
    """Métadonnées d'un fichier fragmenté"""
    original_filename: str
    original_size: int
    original_hash: str
    total_chunks: int
    chunk_size: int
    chunks: List[ChunkInfo]
    
    def to_dict(self):
        return {
            'original_filename': self.original_filename,
            'original_size': self.original_size,
            'original_hash': self.original_hash,
            'total_chunks': self.total_chunks,
            'chunk_size': self.chunk_size,
            'chunks': [c.to_dict() for c in self.chunks]
        }
    
    @staticmethod
    def from_dict(data):
        chunks = [ChunkInfo.from_dict(c) for c in data['chunks']]
        return FragmentedFileMetadata(
            original_filename=data['original_filename'],
            original_size=data['original_size'],
            original_hash=data['original_hash'],
            total_chunks=data['total_chunks'],
            chunk_size=data['chunk_size'],
            chunks=chunks
        )
    
    def save_to_file(self, filepath: str):
        """Sauvegarder les métadonnées dans un fichier JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load_from_file(filepath: str):
        """Charger les métadonnées depuis un fichier JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return FragmentedFileMetadata.from_dict(data)


class FileFragmenter:
    """Gestionnaire de fragmentation de fichiers"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE):
        """
        Initialiser le fragmenteur
        
        Args:
            chunk_size: Taille de chaque chunk en octets
        """
        self.chunk_size = chunk_size
    
    def should_fragment(self, filesize: int) -> bool:
        """
        Déterminer si un fichier doit être fragmenté
        
        Args:
            filesize: Taille du fichier en octets
            
        Returns:
            True si le fichier doit être fragmenté
        """
        return filesize > FRAGMENTATION_THRESHOLD
    
    def fragment_file(self, filepath: str, output_dir: str) -> FragmentedFileMetadata:
        """
        Fragmenter un fichier en chunks
        
        Args:
            filepath: Chemin du fichier à fragmenter
            output_dir: Dossier où sauvegarder les chunks
            
        Returns:
            Métadonnées du fichier fragmenté
        """
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Informations du fichier original
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        # Calculer le hash du fichier complet
        print(f"[...] Calcul du hash du fichier complet...")
        original_hash = self._calculate_file_hash(filepath)
        
        # Calculer le nombre de chunks
        total_chunks = (filesize + self.chunk_size - 1) // self.chunk_size
        
        print(f"[OK] Fragmentation de {filename} ({filesize} octets) en {total_chunks} chunks")
        
        # Fragmenter le fichier
        chunks_info = []
        
        with open(filepath, 'rb') as f:
            for chunk_id in range(total_chunks):
                # Lire le chunk
                chunk_data = f.read(self.chunk_size)
                chunk_size = len(chunk_data)
                
                # Calculer le hash du chunk
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                
                # Sauvegarder le chunk
                chunk_filename = f"{filename}.chunk{chunk_id:04d}"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                # Enregistrer les infos
                chunk_info = ChunkInfo(
                    chunk_id=chunk_id,
                    chunk_hash=chunk_hash,
                    chunk_size=chunk_size,
                    stored_on=[]  # Sera rempli lors de la distribution
                )
                chunks_info.append(chunk_info)
                
                print(f"  [OK] Chunk {chunk_id + 1}/{total_chunks} créé ({chunk_size} octets)")
        
        # Créer les métadonnées
        metadata = FragmentedFileMetadata(
            original_filename=filename,
            original_size=filesize,
            original_hash=original_hash,
            total_chunks=total_chunks,
            chunk_size=self.chunk_size,
            chunks=chunks_info
        )
        
        # Sauvegarder les métadonnées
        metadata_path = os.path.join(output_dir, f"{filename}.metadata.json")
        metadata.save_to_file(metadata_path)
        
        print(f"[OK] Fragmentation terminée : {total_chunks} chunks créés")
        
        return metadata
    
    def reconstruct_file(self, chunks_dir: str, metadata: FragmentedFileMetadata, 
                        output_path: str) -> bool:
        """
        Reconstruire un fichier à partir de ses chunks
        
        Args:
            chunks_dir: Dossier contenant les chunks
            metadata: Métadonnées du fichier fragmenté
            output_path: Chemin où reconstruire le fichier
            
        Returns:
            True si la reconstruction a réussi
        """
        print(f"[...] Reconstruction de {metadata.original_filename}...")
        
        # Vérifier que tous les chunks sont disponibles
        missing_chunks = []
        for chunk_info in metadata.chunks:
            chunk_filename = f"{metadata.original_filename}.chunk{chunk_info.chunk_id:04d}"
            chunk_path = os.path.join(chunks_dir, chunk_filename)
            
            if not os.path.exists(chunk_path):
                missing_chunks.append(chunk_info.chunk_id)
        
        if missing_chunks:
            print(f"[X] Chunks manquants : {missing_chunks}")
            return False
        
        # Reconstruire le fichier
        with open(output_path, 'wb') as output_file:
            for chunk_info in metadata.chunks:
                chunk_filename = f"{metadata.original_filename}.chunk{chunk_info.chunk_id:04d}"
                chunk_path = os.path.join(chunks_dir, chunk_filename)
                
                # Lire et vérifier le chunk
                with open(chunk_path, 'rb') as chunk_file:
                    chunk_data = chunk_file.read()
                
                # Vérifier le hash
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                if chunk_hash != chunk_info.chunk_hash:
                    print(f"[X] Erreur : Hash invalide pour le chunk {chunk_info.chunk_id}")
                    return False
                
                # Écrire dans le fichier final
                output_file.write(chunk_data)
                
                print(f"  [OK] Chunk {chunk_info.chunk_id + 1}/{metadata.total_chunks} ajouté")
        
        # Vérifier le hash du fichier complet
        print(f"[...] Vérification du hash du fichier reconstruit...")
        reconstructed_hash = self._calculate_file_hash(output_path)
        
        if reconstructed_hash != metadata.original_hash:
            print(f"[X] Erreur : Hash du fichier reconstruit invalide")
            os.remove(output_path)
            return False
        
        print(f"[OK] Fichier reconstruit avec succès : {output_path}")
        return True
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """
        Calculer le hash SHA-256 d'un fichier
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            Hash SHA-256 en hexadécimal
        """
        sha256_hash = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096 * 1024), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()


def get_chunk_distribution(chunks_count: int, available_peers: List[str], 
                          redundancy: int = REDUNDANCY_FACTOR) -> Dict[int, List[str]]:
    """
    Déterminer la distribution optimale des chunks sur les PCs disponibles
    
    Args:
        chunks_count: Nombre total de chunks
        available_peers: Liste des PCs disponibles
        redundancy: Nombre de copies de chaque chunk
        
    Returns:
        Dictionnaire {chunk_id: [peer1, peer2, ...]}
    """
    if len(available_peers) == 0:
        return {}
    
    distribution = {}
    
    for chunk_id in range(chunks_count):
        # Sélectionner les PCs pour ce chunk (rotation circulaire avec redondance)
        selected_peers = []
        for r in range(min(redundancy, len(available_peers))):
            peer_index = (chunk_id + r) % len(available_peers)
            selected_peers.append(available_peers[peer_index])
        
        distribution[chunk_id] = selected_peers
    
    return distribution
