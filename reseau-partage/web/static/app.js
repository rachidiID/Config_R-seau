// Configuration
const API_BASE = 'http://localhost:5000/api';
let peerName = null;
let peerPort = null;
let refreshInterval = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initializePeer();
    setupEventListeners();
    startAutoRefresh();
});

// Initialiser le peer
function initializePeer() {
    // Récupérer les paramètres de l'URL ou demander
    const urlParams = new URLSearchParams(window.location.search);
    peerName = urlParams.get('name') || prompt('Nom de ce PC:', 'PC1');
    peerPort = parseInt(urlParams.get('port') || prompt('Port:', '5001'));
    
    if (!peerName || !peerPort) {
        alert('Nom et port requis');
        return;
    }
    
    // Mettre à jour l'interface
    document.getElementById('peerName').textContent = peerName;
    document.getElementById('peerPort').textContent = peerPort;
    
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
    
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.style.display = 'block';
    
    document.getElementById('sendBtn').disabled = false;
}

// Charger la liste des peers
async function loadPeers() {
    try {
        const response = await fetch(`${API_BASE}/peers/online`);
        const data = await response.json();
        
        const peersList = document.getElementById('peersList');
        const recipientSelect = document.getElementById('recipientSelect');
        
        // Filtrer le peer actuel
        const peers = data.peers.filter(p => p.name !== peerName);
        
        if (peers.length === 0) {
            peersList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <p>Aucun PC connecté</p>
                </div>
            `;
            recipientSelect.innerHTML = '<option value="">Aucun PC disponible</option>';
            return;
        }
        
        // Mettre à jour la liste
        peersList.innerHTML = peers.map(peer => `
            <div class="peer-item">
                <div class="peer-details">
                    <div class="peer-name">${peer.name}</div>
                    <div class="peer-ip">${peer.ip_address}:${peer.port}</div>
                </div>
                <span class="peer-status">En ligne</span>
            </div>
        `).join('');
        
        // Mettre à jour le select
        recipientSelect.innerHTML = `
            <option value="*">Tous les PC (${peers.length})</option>
            ${peers.map(p => `<option value="${p.name}">${p.name}</option>`).join('')}
        `;
        
        // Mettre à jour le badge
        document.getElementById('peersCount').textContent = peers.length;
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Charger la liste des fichiers reçus
async function loadFiles() {
    try {
        // Simuler des fichiers reçus (en réalité, cela viendrait du backend)
        const filesList = document.getElementById('filesList');
        
        // Pour l'instant, afficher un état vide
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📂</div>
                <p>Aucun fichier reçu</p>
            </div>
        `;
        
        document.getElementById('filesCount').textContent = '0';
        
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
        // 1. Calculer le checksum (simplifié)
        const checksum = await calculateChecksum(file);
        
        // 2. Enregistrer le fichier sur le serveur
        const recipients = recipient === '*' ? 
            Array.from(recipientSelect.options)
                .filter(opt => opt.value !== '*' && opt.value !== '')
                .map(opt => opt.value) :
            [recipient];
        
        const registerResponse = await fetch(`${API_BASE}/file/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: file.name,
                filesize: file.size,
                checksum: checksum,
                owner: peerName,
                permission: recipients.length > 1 ? 'public' : 'private',
                recipients: recipients
            })
        });
        
        if (!registerResponse.ok) {
            throw new Error('Erreur lors de l\'enregistrement du fichier');
        }
        
        const { file_id } = await registerResponse.json();
        
        // 3. Simuler l'envoi (en réalité, cela utiliserait WebSockets ou WebRTC)
        showProgress(true);
        await simulateUpload(file, recipients.length);
        
        // 4. Logger le transfert
        for (const rec of recipients) {
            await fetch(`${API_BASE}/transfer/log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_id: file_id,
                    from_peer: peerName,
                    to_peer: rec,
                    status: 'success'
                })
            });
        }
        
        showNotification(`Fichier envoyé à ${recipients.length} PC`, 'success');
        
        // Réinitialiser
        fileInput.value = '';
        document.getElementById('fileInfo').style.display = 'none';
        showProgress(false);
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur lors de l\'envoi du fichier', 'error');
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

// Afficher une notification
function showNotification(message, type = 'info') {
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
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
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
    }, 5000); // Toutes les 5 secondes
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
