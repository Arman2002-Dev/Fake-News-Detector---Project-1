// ===== STATE =====
let selectedHomeImage = null;
let selectedFullImage = null;
let currentResult = null;
let currentFilter = 'all';

const API_BASE = 'http://localhost:5000';

// ===== PAGE SWITCHING =====
function switchPage(page) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + page)?.classList.add('active');
    
    if (page === 'history') loadHistory();
    if (page === 'home') loadRecentChecks();
}

// ===== INPUT MODE SWITCHING (Home) =====
function switchInputMode(mode) {
    document.querySelectorAll('.input-tab').forEach(tab => tab.classList.remove('active'));
    event.target.closest('.input-tab')?.classList.add('active');
    
    document.querySelectorAll('.input-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(mode + '-input-panel')?.classList.add('active');
    if (mode === 'url') document.getElementById('url-input')?.classList.add('active');
}

// ===== FULL MODE SWITCHING =====
function switchFullMode(mode) {
    document.querySelectorAll('.full-tab').forEach(tab => tab.classList.remove('active'));
    event.target.closest('.full-tab')?.classList.add('active');
    
    document.querySelectorAll('.full-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('full-' + mode + '-panel')?.classList.add('active');
}

// ===== HOME IMAGE =====
function handleHomeImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        selectedHomeImage = e.target.result;
        document.getElementById('home-preview-img').src = selectedHomeImage;
        document.getElementById('home-img-preview').classList.remove('hidden');
        document.getElementById('home-analyze-img').disabled = false;
    };
    reader.readAsDataURL(file);
}

function removeHomeImage() {
    selectedHomeImage = null;
    document.getElementById('home-file').value = '';
    document.getElementById('home-img-preview').classList.add('hidden');
    document.getElementById('home-analyze-img').disabled = true;
}

// ===== FULL IMAGE =====
function handleFullImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        selectedFullImage = e.target.result;
        document.getElementById('full-preview-img').src = selectedFullImage;
        document.getElementById('full-preview').classList.remove('hidden');
        document.getElementById('full-analyze-btn').disabled = false;
    };
    reader.readAsDataURL(file);
}

// ===== ANALYSIS FUNCTIONS =====
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showResult(result) {
    currentResult = result;
    const isFake = result.prediction === 'FAKE';
    
    document.getElementById('res-icon').textContent = isFake ? '🚨' : '✨';
    document.getElementById('res-title').textContent = 'Analysis Complete';
    document.getElementById('res-subtitle').textContent = isFake ? 'Fake news detected!' : 'This news appears credible';
    
    const verdictDiv = document.getElementById('res-verdict');
    verdictDiv.className = 'result-verdict ' + (isFake ? 'fake' : 'real');
    document.getElementById('res-badge').textContent = isFake ? 'FAKE NEWS' : 'REAL NEWS';
    document.getElementById('res-confidence').textContent = (result.confidence || 0) + '%';
    
    document.getElementById('res-fake-bar').style.width = (result.fake_prob || 0) + '%';
    document.getElementById('res-fake-p').textContent = (result.fake_prob || 0) + '%';
    document.getElementById('res-real-bar').style.width = (result.real_prob || 0) + '%';
    document.getElementById('res-real-p').textContent = (result.real_prob || 0) + '%';
    
    document.getElementById('result-overlay').classList.remove('hidden');
    hideLoading();
}

function closeResult() {
    document.getElementById('result-overlay').classList.add('hidden');
}

async function analyzeFromHome() {
    const url = document.getElementById('url-field').value.trim();
    if (!url) {
        switchInputMode('text');
        return;
    }
    // For URL, we'd need a scraper. For now, switch to text mode
    switchPage('detect');
}

async function analyzeTextFromHome() {
    const title = document.getElementById('home-title').value.trim();
    const content = document.getElementById('home-content').value.trim();
    if (!title && !content) return alert('Please enter some text');
    // FIX: Send title and content SEPARATELY so api.py can handle them correctly
    // Do NOT merge them here — merging changes how the model processes the input
    await analyzeText(content, title);
}

async function analyzeFullText() {
    const title = document.getElementById('detect-title').value.trim();
    const content = document.getElementById('detect-content').value.trim();
    if (!title && !content) return alert('Please enter some text');
    // FIX: Send title and content SEPARATELY so api.py can handle them correctly
    await analyzeText(content, title);
}

async function analyzeHomeImage() {
    if (!selectedHomeImage) return;
    await analyzeImage(selectedHomeImage);
}

async function analyzeFullImage() {
    if (!selectedFullImage) return;
    await analyzeImage(selectedFullImage);
}

async function analyzeText(text, title) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/api/predict/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, title })
        });
        const data = await res.json();
        if (data.error) { hideLoading(); return alert(data.error); }
        showResult(data);
        loadRecentChecks();
    } catch (e) {
        hideLoading();
        alert('Server error. Is it running?');
    }
}

async function analyzeImage(image) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/api/predict/image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image })
        });
        const data = await res.json();
        if (data.error) { hideLoading(); return alert(data.error); }
        showResult(data);
        loadRecentChecks();
    } catch (e) {
        hideLoading();
        alert('Server error. Is it running?');
    }
}

// ===== RECENT CHECKS =====
async function loadRecentChecks() {
    try {
        const res = await fetch(`${API_BASE}/api/history?limit=5`);
        const data = await res.json();
        renderRecentChecks(data.data || []);
    } catch (e) {
        console.log('Could not load recent checks');
    }
}

function renderRecentChecks(items) {
    const container = document.getElementById('recent-checks-list');
    if (!items.length) {
        container.innerHTML = '<div class="check-item empty"><p>No recent checks. Start analyzing news!</p></div>';
        return;
    }
    container.innerHTML = items.map(item => {
        const isFake = item.prediction === 'FAKE';
        return `
            <div class="check-item">
                <span class="check-title">${escapeHtml(item.title)}</span>
                <span class="check-badge ${isFake ? 'fake' : 'real'}">${isFake ? 'Fake News' : 'Real News'}</span>
                <span class="check-score">${item.credibility_score}%</span>
                <span class="check-time">${timeAgo(item.timestamp)}</span>
            </div>
        `;
    }).join('');
}

// ===== HISTORY =====
async function loadHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/history?filter_type=${currentFilter}`);
        const data = await res.json();
        updateHistoryStats(data.stats);
        renderHistoryTable(data.data || []);
    } catch (e) {
        document.getElementById('history-table').innerHTML = '<div class="history-empty-state"><i class="fa-regular fa-folder-open"></i><p>Could not load history</p></div>';
    }
}

function updateHistoryStats(stats) {
    document.getElementById('hist-total').textContent = stats.total_checks;
    document.getElementById('hist-fake').textContent = stats.fake_detected;
    document.getElementById('hist-real').textContent = stats.real_detected;
    document.getElementById('hist-today').textContent = stats.today_checks;
}

function renderHistoryTable(items) {
    const container = document.getElementById('history-table');
    if (!items.length) {
        container.innerHTML = '<div class="history-empty-state"><i class="fa-regular fa-folder-open"></i><p>No history yet. Start checking news!</p></div>';
        return;
    }
    container.innerHTML = items.map(item => {
        const isFake = item.prediction === 'FAKE';
        return `
            <div class="hist-item">
                <div class="hist-icon ${isFake ? 'fake' : 'real'}">
                    <i class="fa-solid ${isFake ? 'fa-triangle-exclamation' : 'fa-check'}"></i>
                </div>
                <div class="hist-details">
                    <div class="hist-title">${escapeHtml(item.title)}</div>
                    <div class="hist-meta">${item.source_type} • ${timeAgo(item.timestamp)}</div>
                </div>
                <span class="hist-badge ${isFake ? 'fake' : 'real'}">${isFake ? 'Fake' : 'Real'}</span>
                <span class="hist-score">${item.credibility_score}%</span>
                <button class="hist-delete" onclick="deleteHistoryItem('${item.id}')">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
    }).join('');
}

function filterHistory(type) {
    currentFilter = type;
    document.querySelectorAll('.h-filter').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadHistory();
}

async function deleteHistoryItem(id) {
    if (!confirm('Delete this item?')) return;
    try {
        await fetch(`${API_BASE}/api/history/${id}`, { method: 'DELETE' });
        loadHistory();
    } catch (e) {}
}

async function clearAllHistory() {
    if (!confirm('Clear all history?')) return;
    try {
        await fetch(`${API_BASE}/api/history/clear/all`, { method: 'DELETE' });
        loadHistory();
    } catch (e) {}
}

// ===== UTILITIES =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function timeAgo(timestamp) {
    if (!timestamp) return 'Unknown';
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return minutes + 'm ago';
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    const days = Math.floor(hours / 24);
    if (days < 30) return days + 'd ago';
    return date.toLocaleDateString();
}

function shareResult() {
    if (!currentResult) return;
    const text = currentResult.prediction === 'FAKE' 
        ? '🚨 Detected fake news with TruthCheck!' 
        : '✅ Verified real news with TruthCheck!';
    navigator.clipboard?.writeText(text);
    alert('Copied to clipboard!');
}

function showHowItWorks() { alert('How It Works:\n\n1. Paste news URL or text\n2. Our AI analyzes the content\n3. Get instant credibility score'); }
function showAbout() { alert('TruthCheck v1.0\nAI-powered fake news detection'); }
function showContact() { alert('Contact us at: support@truthcheck.ai'); }
function toggleTheme() { alert('Theme toggle coming soon!'); }

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadRecentChecks();
});