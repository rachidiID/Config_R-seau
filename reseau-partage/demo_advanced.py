#!/usr/bin/env python3
"""
Script de démonstration des fonctionnalités avancées
Teste la haute disponibilité et la fragmentation
"""

import os
import sys
import time
import tempfile
import shutil

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.fragmentation import FileFragmenter, get_chunk_distribution, FragmentedFileMetadata
from shared.high_availability import ServerDiscovery, ServerInfo


def print_header(title):
    """Afficher un en-tête formaté"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_fragmentation():
    """Démonstration de la fragmentation de fichiers"""
    print_header("DÉMONSTRATION : FRAGMENTATION DE FICHIERS")
    
    # Créer un fichier de test (100 MB)
    print("\n[1/5] Création d'un fichier de test (100 MB)...")
    test_file = tempfile.mktemp(suffix='.dat')
    
    with open(test_file, 'wb') as f:
        # Écrire 100 MB de données aléatoires
        chunk_size = 1024 * 1024  # 1 MB
        for i in range(100):
            f.write(os.urandom(chunk_size))
            if i % 20 == 0:
                print(f"   Écriture... {i + 1}/100 MB")
    
    filesize = os.path.getsize(test_file)
    print(f"[OK] Fichier créé : {test_file} ({filesize / (1024*1024):.1f} MB)")
    
    # Fragmenter le fichier
    print("\n[2/5] Fragmentation du fichier...")
    temp_dir = tempfile.mkdtemp()
    
    fragmenter = FileFragmenter(chunk_size=10 * 1024 * 1024)  # 10 MB par chunk
    metadata = fragmenter.fragment_file(test_file, temp_dir)
    
    print(f"[OK] Fragmentation terminée :")
    print(f"     - Chunks créés : {metadata.total_chunks}")
    print(f"     - Taille chunk : {metadata.chunk_size / (1024*1024):.1f} MB")
    print(f"     - Hash original : {metadata.original_hash[:16]}...")
    
    # Lister les chunks
    print("\n[3/5] Chunks créés :")
    chunks = sorted([f for f in os.listdir(temp_dir) if f.endswith('.chunk0000') or 'chunk' in f])
    for i, chunk in enumerate(chunks[:5]):  # Afficher les 5 premiers
        size = os.path.getsize(os.path.join(temp_dir, chunk))
        print(f"     {i+1}. {chunk} ({size / (1024*1024):.1f} MB)")
    if len(chunks) > 5:
        print(f"     ... et {len(chunks) - 5} autres chunks")
    
    # Calculer la distribution
    print("\n[4/5] Distribution optimale des chunks sur 3 PCs...")
    distribution = get_chunk_distribution(
        chunks_count=metadata.total_chunks,
        available_peers=["PC1", "PC2", "PC3"],
        redundancy=2
    )
    
    for chunk_id, peers in list(distribution.items())[:5]:
        print(f"     Chunk {chunk_id:2d} → {', '.join(peers)}")
    if len(distribution) > 5:
        print(f"     ... {len(distribution) - 5} autres chunks")
    
    # Reconstruire le fichier
    print("\n[5/5] Reconstruction du fichier...")
    reconstructed_file = tempfile.mktemp(suffix='_reconstructed.dat')
    
    success = fragmenter.reconstruct_file(temp_dir, metadata, reconstructed_file)
    
    if success:
        original_size = os.path.getsize(test_file)
        reconstructed_size = os.path.getsize(reconstructed_file)
        
        print(f"[OK] Reconstruction réussie !")
        print(f"     - Taille originale : {original_size / (1024*1024):.1f} MB")
        print(f"     - Taille reconstruite : {reconstructed_size / (1024*1024):.1f} MB")
        print(f"     - Intégrité : {'✓ Vérifiée' if original_size == reconstructed_size else '✗ ERREUR'}")
    else:
        print("[X] Erreur lors de la reconstruction")
    
    # Nettoyage
    print("\n[NETTOYAGE] Suppression des fichiers temporaires...")
    os.remove(test_file)
    os.remove(reconstructed_file)
    shutil.rmtree(temp_dir)
    print("[OK] Nettoyage terminé")


def demo_high_availability():
    """Démonstration de la haute disponibilité"""
    print_header("DÉMONSTRATION : HAUTE DISPONIBILITÉ")
    
    print("\n[1/4] Création de 3 serveurs virtuels...")
    
    # Créer 3 instances de découverte
    server1 = ServerDiscovery("192.168.1.10", 5000, "Server1", priority=3)
    server2 = ServerDiscovery("192.168.1.11", 5001, "Server2", priority=2)
    server3 = ServerDiscovery("192.168.1.12", 5002, "Server3", priority=1)
    
    print(f"[OK] Server1 créé : {server1.my_info.host}:{server1.my_info.port} (priorité {server1.my_info.priority})")
    print(f"[OK] Server2 créé : {server2.my_info.host}:{server2.my_info.port} (priorité {server2.my_info.priority})")
    print(f"[OK] Server3 créé : {server3.my_info.host}:{server3.my_info.port} (priorité {server3.my_info.priority})")
    
    print("\n[2/4] Démarrage du système de découverte...")
    print("     (En production, les heartbeats se feraient via UDP broadcast)")
    
    # Simuler la découverte mutuelle
    server1.known_servers["Server2"] = server2.my_info
    server1.known_servers["Server3"] = server3.my_info
    
    server2.known_servers["Server1"] = server1.my_info
    server2.known_servers["Server3"] = server3.my_info
    
    server3.known_servers["Server1"] = server1.my_info
    server3.known_servers["Server2"] = server2.my_info
    
    print("[OK] Tous les serveurs se sont découverts")
    
    print("\n[3/4] Élection du serveur primaire...")
    
    # Simuler l'élection
    all_servers = [server1.my_info, server2.my_info, server3.my_info]
    all_servers.sort(key=lambda s: (-s.priority, s.name))
    primary = all_servers[0]
    
    print(f"[OK] Serveur primaire élu : {primary.name}")
    print(f"     Raison : Priorité la plus élevée ({primary.priority})")
    
    print("\n[4/4] Simulation d'une panne du serveur primaire...")
    print(f"     Serveur {primary.name} tombe en panne...")
    
    # Retirer le primaire
    remaining_servers = [s for s in all_servers if s.name != primary.name]
    remaining_servers.sort(key=lambda s: (-s.priority, s.name))
    new_primary = remaining_servers[0]
    
    print(f"[OK] Basculement automatique vers {new_primary.name}")
    print(f"     Nouveau primaire : {new_primary.name} (priorité {new_primary.priority})")
    print(f"     Temps de basculement : < 15 secondes (détection timeout)")
    
    print("\n[RÉSUMÉ] Haute disponibilité :")
    print(f"     - Serveurs actifs : {len(remaining_servers)}/{len(all_servers)}")
    print(f"     - Primaire actuel : {new_primary.name}")
    print(f"     - Secondaires : {', '.join([s.name for s in remaining_servers if s.name != new_primary.name])}")


def demo_integration():
    """Démonstration de l'intégration des deux systèmes"""
    print_header("DÉMONSTRATION : INTÉGRATION HA + FRAGMENTATION")
    
    print("\n[SCÉNARIO]")
    print("  Un utilisateur envoie un fichier de 2 GB depuis PC1 vers PC2")
    print("  Le réseau a 3 serveurs et 5 PCs clients")
    print()
    
    print("[ÉTAPE 1] PC1 se connecte au réseau")
    print("  → Découverte automatique des serveurs")
    print("  → Connexion au serveur primaire (Server1)")
    print("  [OK] PC1 connecté à Server1")
    
    print("\n[ÉTAPE 2] PC1 initie le transfert")
    print("  → Fichier détecté : 2 GB")
    print("  → Seuil de fragmentation dépassé (>1 GB)")
    print("  → Fragmentation activée : 8 chunks de 256 MB")
    print("  [OK] Fragmentation terminée")
    
    print("\n[ÉTAPE 3] Calcul de la distribution")
    print("  → PCs disponibles : PC1, PC2, PC3, PC4, PC5")
    print("  → Redondance : 2 copies par chunk")
    print("  → Distribution calculée :")
    
    peers = ["PC1", "PC2", "PC3", "PC4", "PC5"]
    distribution = get_chunk_distribution(8, peers, 2)
    for chunk_id, chunk_peers in distribution.items():
        print(f"      Chunk {chunk_id} → {', '.join(chunk_peers)}")
    
    print("\n[ÉTAPE 4] Transfert des chunks")
    print("  → Envoi parallèle des chunks...")
    print("  [OK] 8/8 chunks transférés avec succès")
    
    print("\n[ÉTAPE 5] Panne du serveur primaire")
    print("  → Server1 tombe en panne")
    print("  → Détection après 15 secondes")
    print("  → Basculement automatique vers Server2")
    print("  [OK] Nouveau primaire : Server2")
    
    print("\n[ÉTAPE 6] PC2 reconstruit le fichier")
    print("  → PC2 se connecte à Server2 (nouveau primaire)")
    print("  → Récupération des métadonnées")
    print("  → Téléchargement des 8 chunks depuis les PCs sources")
    print("  → Reconstruction du fichier")
    print("  → Vérification d'intégrité (SHA-256)")
    print("  [OK] Fichier reconstruit avec succès")
    
    print("\n[RÉSULTAT]")
    print("  ✓ Transfert réussi malgré la panne du serveur")
    print("  ✓ Fichier distribué sur 5 PCs")
    print("  ✓ Redondance assurée (2 copies par chunk)")
    print("  ✓ Zéro temps d'arrêt pour les utilisateurs")


def main():
    """Point d'entrée principal"""
    print("\n" + "=" * 70)
    print("  DÉMONSTRATION DES FONCTIONNALITÉS AVANCÉES")
    print("  Réseau de Partage P2P - Version 2.0")
    print("=" * 70)
    
    print("\nChoisissez une démonstration :")
    print("  1. Fragmentation de fichiers")
    print("  2. Haute disponibilité (HA)")
    print("  3. Intégration (HA + Fragmentation)")
    print("  4. Toutes les démonstrations")
    print("  0. Quitter")
    
    choice = input("\nVotre choix : ").strip()
    
    if choice == "1":
        demo_fragmentation()
    elif choice == "2":
        demo_high_availability()
    elif choice == "3":
        demo_integration()
    elif choice == "4":
        demo_fragmentation()
        time.sleep(2)
        demo_high_availability()
        time.sleep(2)
        demo_integration()
    elif choice == "0":
        print("\nAu revoir !")
        return
    else:
        print("\n[X] Choix invalide")
        return
    
    print("\n" + "=" * 70)
    print("  DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    print("\nPour plus d'informations, consultez :")
    print("  - ADVANCED_FEATURES.md (documentation complète)")
    print("  - shared/fragmentation.py (code source)")
    print("  - shared/high_availability.py (code source)")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n[X] Erreur : {e}")
        import traceback
        traceback.print_exc()
