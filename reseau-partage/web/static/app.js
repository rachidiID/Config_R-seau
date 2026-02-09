// Configuration - Utilise l'URL courante pour s'adapter automatiquement
const API_BASE = `${window.location.protocol}//${window.location.host}/api`;
let peerName = null;
let peerPort = null;
let refreshInterval = null;
let haEnabled = false;
let currentServer = null;

// Configuration fragmentation
const FRAGMENT_THRESHOLD = 1024 * 1024 * 1024; // 1 GB
const CHUNK_SIZE = 256 * 1024 * 1024; // 256 MB

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initializePeer();
    setupEventListeners();
    startAutoRefresh();
    checkHAStatus();
    startHeartbeat();
});

// Initialiser le peer
function initializePeer() {
    // Récupérer les paramètres de l'URL
    const urlParams = new URLSearchParams(window.location.search);
    peerName = urlParams.get('name');
    peerPort = parseInt(urlParams.get('port'));
    const token = urlParams.get('token');
    
    // Vérifier l'authentification
    if (!peerName || !peerPort || !token) {
        // Pas de session valide, retour à la page de connexion
        window.location.href = '/web';
        return;
    }
    
    // Vérifier la session stockée
    const session = localStorage.getItem('p2p_session');
    if (session) {
        try {
            const data = JSON.parse(session);
            if (data.name !== peerName || data.token !== token) {
                // Session invalide
                localStorage.removeItem('p2p_session');
                window.location.href = '/web';
                return;
            }
        } catch (e) {
            localStorage.removeItem('p2p_session');
            window.location.href = '/web';
            return;
        }
    }
    
    // Mettre à jour l'interface
    document.getElementById('peerName').textContent = peerName;
    document.getElementById('peerPort').textContent = peerPort;
    
    // Ajouter bouton déconnexion
    addLogoutButton();
    
    // S'enregistrer sur le serveur
    registerPeer();
}

// S'enregistrer sur le serveur
async function registerPeer() {
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: peerName,
                ip: window.location.hostname || 'localhost',
                port: peerPort
            })
        });
        
        if (response.ok) {
            showNotification('Connecté au serveur', 'success');
            loadPeers();
            loadFiles();
        } else {
            showNotification('Erreur de connexion au serveur', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Impossible de se connecter au serveur', 'error');
    }
}

// Envoyer un signal de vie (heartbeat)
async function sendHeartbeat() {
    try {
        await fetch(`${API_BASE}/heartbeat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name: peerName })
        });
    } catch (error) {
        console.error('Heartbeat erreur:', error);
    }
}

// Démarrer heartbeat automatique (toutes les 2 minutes)
function startHeartbeat() {
    // Premier heartbeat immédiat
    sendHeartbeat();
    
    // Puis toutes les 2 minutes (120000 ms)
    setInterval(sendHeartbeat, 120000);
}

// Configuration des événements
function setupEventListeners() {
    // Upload de fichier
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    });
    
    // Bouton d'envoi
    document.getElementById('sendBtn').addEventListener('click', sendFile);
    
    // Rafraîchir
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadPeers();
        loadFiles();
    });
}

// Gérer la sélection de fichier
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fragmentInfo = document.getElementById('fragmentInfo');
    const fragmentDetails = document.getElementById('fragmentDetails');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.style.display = 'block';
    
    // Vérifier si fragmentation nécessaire
    if (file.size > FRAGMENT_THRESHOLD) {
        const chunkCount = Math.ceil(file.size / CHUNK_SIZE);
        fragmentInfo.style.display = 'block';
        fragmentDetails.textContent = `Le fichier sera découpé en ${chunkCount} fragments de 256 MB max`;
    } else {
        fragmentInfo.style.display = 'none';
    }
    
    document.getElementById('sendBtn').disabled = false;
}

// Charger la liste des peers
async function loadPeers() {
    try {
        const response = await fetch(`${API_BASE}/peers`);
        const data = await response.json();
        
        const peersList = document.getElementById('peersList');
        const recipientSelect = document.getElementById('recipientSelect');
        
        // Filtrer le peer actuel
        const allPeers = data.peers.filter(p => p.name !== peerName);
        const onlinePeers = allPeers.filter(p => p.status === 'online');
        
        if (allPeers.length === 0) {
            peersList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">PC Isolé</div>
                    <p>Aucun PC connecté</p>
                </div>
            `;
            recipientSelect.innerHTML = '<option value="">Aucun PC disponible</option>';
            return;
        }
        
        // Mettre à jour la liste avec statut visuel
        peersList.innerHTML = allPeers.map(peer => {
            const isOnline = peer.status === 'online';
            const statusClass = isOnline ? 'peer-status-online' : 'peer-status-offline';
            const statusText = isOnline ? 'En ligne' : 'Hors ligne';
            const statusDot = isOnline ? '•' : '●';
            
            return `
                <div class="peer-item ${isOnline ? '' : 'peer-offline'}">
                    <div class="peer-details">
                        <div class="peer-name">${peer.name}</div>
                        <div class="peer-ip">${peer.ip_address}:${peer.port}</div>
                    </div>
                    <span class="peer-status ${statusClass}">${statusDot} ${statusText}</span>
                </div>
            `;
        }).join('');
        
        // Mettre à jour le select (seulement peers online)
        if (onlinePeers.length === 0) {
            recipientSelect.innerHTML = '<option value="">Aucun PC en ligne</option>';
        } else {
            recipientSelect.innerHTML = `
                <option value="*">Tous les PC (${onlinePeers.length})</option>
                ${onlinePeers.map(p => `<option value="${p.name}">${p.name}</option>`).join('')}
            `;
        }
        
        // Mettre à jour le badge
        document.getElementById('peersCount').textContent = onlinePeers.length;
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Charger la liste des fichiers reçus
async function loadFiles() {
    try {
        // Charger les fichiers reçus
        const receivedResponse = await fetch(`${API_BASE}/files/received/${peerName}`);
        const receivedData = await receivedResponse.json();
        
        // Charger les fichiers envoyés
        const sentResponse = await fetch(`${API_BASE}/files/sent/${peerName}`);
        const sentData = await sentResponse.json();
        
        const filesList = document.getElementById('filesList');
        
        const allFiles = [
            ...receivedData.files.map(f => ({...f, type: 'received'})),
            ...sentData.files.map(f => ({...f, type: 'sent'}))
        ];
        
        if (allFiles.length === 0) {
            filesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">[Fichiers]</div>
                    <p>Aucun fichier</p>
                </div>
            `;
            document.getElementById('filesCount').textContent = '0';
            return;
        }
        
        // Afficher les fichiers (FILTRÉ: seuls les fichiers reçus pour cet utilisateur)
        filesList.innerHTML = allFiles.map(file => {
            const isReceived = file.type === 'received';
            const icon = isReceived ? '[REÇU]' : '[ENVOYÉ]';
            const label = isReceived ? `De: ${file.sender}` : `À: ${file.recipients || 'Plusieurs'}`;
            const badgeClass = isReceived ? 'badge-received' : 'badge-sent';
            
            return `
                <div class="file-item">
                    <div class="file-icon">${icon}</div>
                    <div class="file-details">
                        <div class="file-name">${file.filename}</div>
                        <div class="file-meta">
                            ${formatSize(file.filesize)} • ${label}
                            ${file.recipient_count ? ` (${file.recipient_count} PC)` : ''}
                        </div>
                    </div>
                    <div class="file-actions">
                        <span class="badge ${badgeClass}">${isReceived ? 'Reçu' : 'Envoyé'}</span>
                        ${isReceived ? `
                            <button class="btn-download" onclick="downloadFile('${peerName}', '${file.filename}')" title="Télécharger">
                                Télécharger
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('filesCount').textContent = allFiles.length;
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Envoyer un fichier
async function sendFile() {
    const fileInput = document.getElementById('fileInput');
    const recipientSelect = document.getElementById('recipientSelect');
    const sendBtn = document.getElementById('sendBtn');
    
    const file = fileInput.files[0];
    const recipient = recipientSelect.value;
    
    if (!file || !recipient) {
        showNotification('Veuillez sélectionner un fichier et un destinataire', 'error');
        return;
    }
    
    // Désactiver le bouton
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="spinner"></span>Envoi en cours...';
    
    try {
        // Préparer les destinataires
        const recipients = recipient === '*' ? 
            Array.from(recipientSelect.options)
                .filter(opt => opt.value !== '*' && opt.value !== '')
                .map(opt => opt.value) :
            [recipient];
        
        // Créer FormData pour l'upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('owner', peerName);
        formData.append('recipients', recipients.join(','));
        formData.append('permission', recipients.length > 1 ? 'public' : 'private');
        
        // Afficher la progression
        showProgress(true);
        
        // Envoyer le fichier au serveur
        const uploadResponse = await fetch(`${API_BASE}/file/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            throw new Error(error.error || 'Erreur lors de l\'upload du fichier');
        }
        
        const result = await uploadResponse.json();
        
        // Simuler la progression jusqu'à 100%
        await simulateUpload(file, recipients.length);
        
        showNotification(`Fichier envoyé à ${recipients.length} PC avec succès`, 'success');
        
        // Réinitialiser
        fileInput.value = '';
        document.getElementById('fileInfo').style.display = 'none';
        showProgress(false);
        
        // Rafraîchir la liste des fichiers
        loadFiles();
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification(error.message || 'Erreur lors de l\'envoi du fichier', 'error');
        showProgress(false);
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Envoyer le fichier';
    }
}

// Calculer le checksum (MD5 simplifié)
async function calculateChecksum(file) {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Simuler l'upload avec progression
function simulateUpload(file, recipientCount) {
    return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            updateProgress(progress);
            
            if (progress >= 100) {
                clearInterval(interval);
                resolve();
            }
        }, 200);
    });
}

// Afficher/masquer la barre de progression
function showProgress(show) {
    const container = document.getElementById('progressContainer');
    if (show) {
        container.classList.add('active');
        updateProgress(0);
    } else {
        container.classList.remove('active');
    }
}

// Mettre à jour la barre de progression
function updateProgress(percent) {
    document.getElementById('progressFill').style.width = `${percent}%`;
    document.getElementById('progressText').textContent = `${percent}% - Transfert en cours...`;
}

// Afficher une notification en stack (empilées, max 3 visibles)
function showNotification(message, type = 'info') {
    // Vérifier le nombre de notifications actuelles
    const existingNotifications = document.querySelectorAll('.notification');
    const MAX_NOTIFICATIONS = 3;
    
    // Si on dépasse le max, supprimer la plus ancienne
    if (existingNotifications.length >= MAX_NOTIFICATIONS) {
        const oldest = existingNotifications[0];
        oldest.classList.remove('show');
        setTimeout(() => oldest.remove(), 3000);
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: '✓',
        error: '✗',
        info: 'i'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">${icons[type]}</div>
        <div class="notification-content">
            <div class="notification-title">${type === 'success' ? 'Succès' : type === 'error' ? 'Erreur' : 'Info'}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Formater la taille
function formatSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
}

// Auto-rafraîchir
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadPeers();
        loadFiles();
        checkHAStatus();
    }, 5000); // Toutes les 5 secondes
}

// Vérifier l'état HA
async function checkHAStatus() {
    try {
        const response = await fetch(`${API_BASE}/ha/status`);
        if (response.ok) {
            const data = await response.json();
            haEnabled = data.ha_enabled || false;
            
            if (haEnabled && data.servers) {
                displayHAStatus(data);
            }
        }
    } catch (error) {
        // HA non disponible, mode normal
        haEnabled = false;
    }
}

// Afficher l'état HA
function displayHAStatus(data) {
    const haStatus = document.getElementById('haStatus');
    const serversList = document.getElementById('serversList');
    const serverBadge = document.getElementById('serverBadge');
    const serverName = document.getElementById('serverName');
    
    if (!haStatus || !data.servers || data.servers.length === 0) return;
    
    haStatus.style.display = 'block';
    
    // Trouver le serveur primaire
    const primary = data.servers.find(s => s.is_primary);
    if (primary) {
        serverName.textContent = `${primary.name} (Primaire)`;
        serverName.style.color = '#10b981';
    }
    
    // Afficher tous les serveurs
    serversList.innerHTML = data.servers.map(server => {
        const isPrimary = server.is_primary;
        const statusClass = isPrimary ? 'server-primary' : 'server-secondary';
        const statusText = isPrimary ? 'Primaire' : 'Secondaire';
        const priorityStars = '⭐'.repeat(server.priority);
        
        return `
            <div class="server-card ${statusClass}">
                <div class="server-header">
                    <strong>${server.name}</strong>
                    <span class="badge ${isPrimary ? 'badge-success' : 'badge-secondary'}">${statusText}</span>
                </div>
                <div class="server-info">
                    <div>📍 ${server.host}:${server.port}</div>
                    <div>🎯 Priorité: ${priorityStars} (${server.priority})</div>
                    <div>⏱️ Vu il y a ${Math.floor((Date.now() / 1000) - server.last_seen)}s</div>
                </div>
            </div>
        `;
    }).join('');
}

// Déconnexion propre
window.addEventListener('beforeunload', async () => {
    if (peerName) {
        await fetch(`${API_BASE}/unregister`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: peerName })
        });
    }
});

// Ajouter bouton de déconnexion
function addLogoutButton() {
    const peerInfo = document.querySelector('.peer-info');
    if (peerInfo) {
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'btn-logout';
        logoutBtn.innerHTML = '🚪 Déconnexion';
        logoutBtn.onclick = logout;
        peerInfo.appendChild(logoutBtn);
    }
}

// Déconnexion
async function logout() {
    if (confirm('Voulez-vous vraiment vous déconnecter ?')) {
        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: peerName })
            });
            
            await fetch(`${API_BASE}/unregister`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: peerName })
            });
            
            localStorage.removeItem('p2p_session');
            window.location.href = '/web';
        } catch (error) {
            console.error('Erreur lors de la déconnexion:', error);
            window.location.href = '/web';
        }
    }
}

// Télécharger un fichier
function downloadFile(peerName, filename) {
    const downloadUrl = `${API_BASE}/file/download/${encodeURIComponent(peerName)}/${encodeURIComponent(filename)}`;
    
    // Créer un lien temporaire pour déclencher le téléchargement
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification(`Téléchargement de ${filename}...`, 'info');
}
