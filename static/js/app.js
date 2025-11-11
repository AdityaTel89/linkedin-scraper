// ==================== STATE MANAGEMENT ====================
let statusInterval = null;
let startTime = null;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Setup URL counter
    const urlsTextarea = document.getElementById('urls');
    if (urlsTextarea) {
        urlsTextarea.addEventListener('input', updateURLCount);
    }
    
    // Check server connection
    checkServerConnection();
    
    console.log('LinkedIn Scraper initialized');
}

// ==================== URL COUNTING ====================
function updateURLCount() {
    const urlsText = document.getElementById('urls').value;
    const lines = urlsText.split('\n');
    const totalUrls = lines.filter(line => line.trim().length > 0).length;
    const validUrls = lines.filter(line => line.trim().startsWith('http')).length;
    
    document.getElementById('urlCount').textContent = totalUrls;
    document.getElementById('validUrlCount').textContent = validUrls;
}

// ==================== PASSWORD TOGGLE ====================
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.innerHTML = `
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
        `;
    } else {
        passwordInput.type = 'password';
        eyeIcon.innerHTML = `
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
        `;
    }
}

// ==================== SERVER CONNECTION ====================
async function checkServerConnection() {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(isConnected) {
    const statusIndicator = document.getElementById('connectionStatus');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    if (isConnected) {
        statusIndicator.style.background = 'var(--success-light)';
        statusDot.style.background = 'var(--success)';
        statusText.style.color = 'var(--success)';
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.style.background = 'var(--danger-light)';
        statusDot.style.background = 'var(--danger)';
        statusText.style.color = 'var(--danger)';
        statusText.textContent = 'Disconnected';
    }
}

// ==================== SCRAPING CONTROL ====================
async function startScraping() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const urlsText = document.getElementById('urls').value;
    const urls = urlsText.split('\n')
        .map(u => u.trim())
        .filter(u => u.startsWith('http'));
    
    // Validation
    if (!email || !password) {
        showNotification('Please enter your LinkedIn credentials', 'error');
        return;
    }
    
    if (urls.length === 0) {
        showNotification('Please enter at least one LinkedIn profile URL', 'error');
        return;
    }
    
    // UI Updates
    document.getElementById('startBtn').classList.add('hidden');
    document.getElementById('stopBtn').classList.remove('hidden');
    document.getElementById('statusCard').classList.remove('hidden');
    document.getElementById('downloadBtn').classList.add('hidden');
    
    // Reset status card
    resetStatusCard();
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password, urls})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Scraping started successfully!', 'success');
            startTime = new Date();
            statusInterval = setInterval(checkStatus, 1000);
        } else {
            showNotification(data.error || 'Failed to start scraping', 'error');
            resetUI();
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
        resetUI();
    }
}

async function stopScraping() {
    if (!confirm('Are you sure you want to stop scraping?')) {
        return;
    }
    
    try {
        await fetch('/api/stop', {method: 'POST'});
        clearInterval(statusInterval);
        showNotification('Scraping stopped', 'info');
        resetUI();
    } catch (error) {
        showNotification('Error stopping scraper', 'error');
    }
}

// ==================== STATUS CHECKING ====================
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        updateDashboard(status);
        
        if (!status.is_running && status.completed > 0) {
            clearInterval(statusInterval);
            onScrapingComplete(status);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

function updateDashboard(status) {
    // Update stats
    document.getElementById('totalStat').textContent = status.total || 0;
    document.getElementById('completedStat').textContent = status.completed || 0;
    document.getElementById('failedStat').textContent = status.failed || 0;
    
    // Update time
    if (startTime) {
        const elapsed = Math.floor((new Date() - startTime) / 1000);
        document.getElementById('timeStat').textContent = formatTime(elapsed);
    }
    
    // Update progress bar
    const percentage = status.total > 0 ? (status.completed / status.total) * 100 : 0;
    document.getElementById('progressBar').style.width = percentage + '%';
    document.getElementById('progressPercentage').textContent = Math.round(percentage) + '%';
    
    // Update status badge
    const statusBadge = document.getElementById('statusBadge');
    if (status.is_running) {
        statusBadge.textContent = 'Running';
        statusBadge.className = 'status-badge status-running';
    }
    
    // Update profiles grid
    if (status.profiles_data && status.profiles_data.length > 0) {
        updateProfilesGrid(status.profiles_data);
    }
    
    // Update log
    if (status.progress && status.progress.length > 0) {
        updateLog(status.progress);
    }
}

function updateProfilesGrid(profiles) {
    const grid = document.getElementById('profilesGrid');
    const section = document.getElementById('profilesSection');
    
    if (profiles.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    section.classList.remove('hidden');
    
    grid.innerHTML = profiles.map((profile, idx) => `
        <div class="profile-card ${profile.status} fade-in">
            <div class="profile-index">#${profile.index || idx + 1}</div>
            <div class="profile-name">${escapeHtml(profile.name)}</div>
            <div class="profile-headline">${escapeHtml(profile.headline)}</div>
            <div class="profile-location">📍 ${escapeHtml(profile.location)}</div>
            <div class="profile-status ${profile.status}">
                ${profile.status === 'success' ? '✅ Success' : '❌ Failed'}
            </div>
        </div>
    `).join('');
}

function updateLog(progress) {
    const logContainer = document.getElementById('logContainer');
    
    if (progress.length === 0) {
        logContainer.innerHTML = '<div class="log-empty">No activity yet...</div>';
        return;
    }
    
    logContainer.innerHTML = progress.map(item => {
        const message = typeof item === 'string' ? item : item.message;
        return `<div class="log-item">${escapeHtml(message)}</div>`;
    }).join('');
    
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLog() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '<div class="log-empty">Log cleared</div>';
}

// ==================== COMPLETION HANDLING ====================
function onScrapingComplete(status) {
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.textContent = 'Completed';
    statusBadge.className = 'status-badge status-completed';
    
    document.getElementById('stopBtn').classList.add('hidden');
    document.getElementById('downloadBtn').classList.remove('hidden');
    document.getElementById('startBtn').classList.remove('hidden');
    
    showNotification(
        `Scraping completed! ${status.completed} profiles scraped successfully.`,
        'success'
    );
}

function resetUI() {
    document.getElementById('startBtn').classList.remove('hidden');
    document.getElementById('stopBtn').classList.add('hidden');
    
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.textContent = 'Stopped';
    statusBadge.className = 'status-badge status-stopped';
}

function resetStatusCard() {
    document.getElementById('totalStat').textContent = '0';
    document.getElementById('completedStat').textContent = '0';
    document.getElementById('failedStat').textContent = '0';
    document.getElementById('timeStat').textContent = '0s';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressPercentage').textContent = '0%';
    document.getElementById('profilesGrid').innerHTML = '';
    document.getElementById('logContainer').innerHTML = '<div class="log-empty">Initializing...</div>';
}

// ==================== FILE DOWNLOAD ====================
function downloadCSV() {
    window.location.href = '/api/download';
    showNotification('Downloading CSV file...', 'success');
}

// ==================== NOTIFICATIONS ====================
function showNotification(message, type = 'info') {
    // Simple alert for now - you can implement a toast notification system
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    alert(`${icons[type] || ''} ${message}`);
}

// ==================== UTILITIES ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}
