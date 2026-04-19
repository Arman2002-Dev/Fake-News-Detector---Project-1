#!/usr/bin/env python3
"""
FAKE NEWS DETECTOR API - With Image Support
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import re
import os
import base64
from PIL import Image
import io
import pytesseract
import cv2
import numpy as np

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# ============== LOAD MODEL ==============
print("⏳ Loading model...")
try:
    package = joblib.load('fake_news_model.pkl')
    model = package['model']
    vectorizer = package['vectorizer']
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    vectorizer = None

# ============== STOP WORDS ==============
STOP_WORDS = set(['i','me','my','myself','we','our','ours','ourselves','you','your','yours',
'yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its',
'itself','they','them','their','theirs','themselves','what','which','who','whom','this',
'that','these','those','am','is','are','was','were','be','been','being','have','has','had',
'having','do','does','did','doing','a','an','the','and','but','if','or','because','as',
'until','while','of','at','by','for','with','through','during','before','after','above',
'below','up','down','in','out','on','off','over','under','again','further','then','once',
'here','there','when','where','why','how','all','any','both','each','few','more','most',
'other','some','such','no','nor','not','only','own','same','so','than','too','very','s',
't','can','will','just','don','should','now'])

# ============== TEXT CLEANING ==============
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return ' '.join(words)

# ============== IMAGE PROCESSING ==============
def preprocess_image(img_array):
    """Prepare image for OCR"""
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    h, w = binary.shape
    if h < 1000:
        binary = cv2.resize(binary, None, fx=1000/h, fy=1000/h)
    
    return binary

def extract_text_from_image(image_data):
    """Extract text from base64 image"""
    try:
        # Decode base64
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        
        # Convert to RGB if needed
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        # Process and OCR
        processed = preprocess_image(img_array)
        text = pytesseract.image_to_string(processed, config=r'--oem 3 --psm 6 -l eng')
        text = ' '.join(text.strip().split())
        
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

# ============== PREDICTION ==============
def predict_news(text):
    """Make prediction"""
    if model is None or vectorizer is None:
        return {'error': 'Model not loaded'}
    
    cleaned = clean_text(text)
    
    if len(cleaned) < 10:
        return {'error': 'Text too short after cleaning. Found: ' + cleaned[:50]}
    
    vectorized = vectorizer.transform([cleaned])
    prediction = model.predict(vectorized)[0]
    prob = model.predict_proba(vectorized)[0]
    
    return {
        'is_fake': bool(prediction == 1),
        'prediction': 'FAKE' if prediction == 1 else 'REAL',
        'confidence': round(max(prob) * 100, 2),
        'fake_prob': round(prob[1] * 100, 2),
        'real_prob': round(prob[0] * 100, 2),
        'cleaned_text': cleaned[:200] + '...' if len(cleaned) > 200 else cleaned
    }

# ============== ROUTES ==============
@app.route('/')
def index():
    """Serve your index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/predict/text', methods=['POST'])
def predict_text():
    """Predict from text input"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400
    
    result = predict_news(data['text'])
    return jsonify(result)

@app.route('/api/predict/image', methods=['POST'])
def predict_image():
    """Predict from image"""
    data = request.json
    
    if not data or 'image' not in data:
        return jsonify({'error': 'Missing image'}), 400
    
    # Extract text from image
    print("🔍 Extracting text from image...")
    extracted_text = extract_text_from_image(data['image'])
    
    if not extracted_text:
        return jsonify({'error': 'Could not extract text from image. Try clearer image.'}), 400
    
    if len(extracted_text) < 20:
        return jsonify({'error': f'Not enough text found. Only got: {extracted_text[:50]}'}), 400
    
    print(f"✓ Extracted {len(extracted_text)} characters")
    
    # Predict
    result = predict_news(extracted_text)
    result['extracted_text'] = extracted_text[:300] + '...' if len(extracted_text) > 300 else extracted_text
    
    return jsonify(result)

@app.route('/api/health')
def health():
    """Check status"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'ocr_available': True
    })

if __name__ == '__main__':
    print("🚀 Starting Fake News Detector API")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)