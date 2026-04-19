// Global variables
let selectedImage = null;

// Switch tabs
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tab + '-section').classList.add('active');
    
    hideResults();
}

// Handle image selection
function handleImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        selectedImage = e.target.result;
        document.getElementById('preview-img').src = selectedImage;
        document.getElementById('preview').classList.remove('hidden');
        document.querySelector('.upload-box').classList.add('hidden');
        document.getElementById('analyze-img-btn').disabled = false;
        hideResults();
    };
    reader.readAsDataURL(file);
}

// Remove image
function removeImage() {
    selectedImage = null;
    document.getElementById('file-input').value = '';
    document.getElementById('preview').classList.add('hidden');
    document.querySelector('.upload-box').classList.remove('hidden');
    document.getElementById('analyze-img-btn').disabled = true;
    hideResults();
}

// Hide all results
function hideResults() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
}

// Show loading
function showLoading() {
    hideResults();
    document.getElementById('loading').classList.remove('hidden');
}

// Show error
function showError(msg) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error').textContent = msg;
    document.getElementById('error').classList.remove('hidden');
}

// Display result
function showResult(data, isImage) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('result').classList.remove('hidden');
    
    // Verdict
    const verdictDiv = document.getElementById('verdict');
    verdictDiv.className = 'verdict ' + (data.is_fake ? 'fake' : 'real');
    verdictDiv.innerHTML = (data.is_fake ? '🚨 FAKE NEWS' : '✅ REAL NEWS');
    
    // Confidence
    document.getElementById('conf-value').textContent = data.confidence + '%';
    document.getElementById('conf-bar').style.width = data.confidence + '%';
    
    // Probabilities
    document.getElementById('fake-p').textContent = data.fake_prob + '%';
    document.getElementById('real-p').textContent = data.real_prob + '%';
    
    // Extracted text (for images)
    const extractedDiv = document.getElementById('extracted');
    if (isImage && data.extracted_text) {
        document.getElementById('extracted-text').textContent = data.extracted_text;
        extractedDiv.classList.remove('hidden');
    } else {
        extractedDiv.classList.add('hidden');
    }
}

// Analyze text
async function analyzeText() {
    const title = document.getElementById('title').value.trim();
    const content = document.getElementById('content').value.trim();
    
    if (!title && !content) {
        showError('Please enter title or content');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/predict/text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: title + ' ' + content})
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            showResult(data, false);
        }
    } catch (err) {
        showError('Failed to analyze. Is server running?');
    }
}

// Analyze image
async function analyzeImage() {
    if (!selectedImage) {
        showError('Please select an image first');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/predict/image', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({image: selectedImage})
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            showResult(data, true);
        }
    } catch (err) {
        showError('Failed to analyze. Is server running?');
    }
}

// Drag and drop support
document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.querySelector('.upload-box');
    
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#667eea';
    });
    
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.style.borderColor = '#ccc';
    });
    
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#ccc';
        const files = e.dataTransfer.files;
        if (files.length) {
            document.getElementById('file-input').files = files;
            handleImage({target: {files: files}});
        }
    });
});