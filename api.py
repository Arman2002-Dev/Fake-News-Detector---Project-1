#!/usr/bin/env python3
"""
FAKE NEWS DETECTOR API - With Live Data, Image Support & History
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import re
import os
import base64
import pandas as pd
from PIL import Image
import io
import pytesseract
import cv2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Import history manager
from history import (
    init_history, save_analysis, get_history, 
    get_history_stats, delete_history_item, clear_all_history
)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

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

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return ' '.join(words)

def load_and_train_model():
    print("⏳ Loading data...")
    
    df_orig = pd.read_csv('fake_or_real_news.csv')
    
    if os.path.exists('live_news_dataset.csv') and os.path.getsize('live_news_dataset.csv') > 0:
        df_live = pd.read_csv('live_news_dataset.csv')
        df_combined = pd.concat([df_orig, df_live], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['title'], keep='first')
        print(f"✅ Loaded: {len(df_orig)} original + {len(df_live)} live = {len(df_combined)} total")
    else:
        df_combined = df_orig
        print(f"✅ Loaded: {len(df_orig)} original (no live data yet)")
    
    X = df_combined['title'].fillna('') + ' ' + df_combined['text'].fillna('')
    y = df_combined['label'].apply(lambda x: 1 if str(x).upper() == 'FAKE' else 0)
    
    X_clean = [clean_text(t) for t in X]
    
    print("⏳ Training model...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_vec = vectorizer.fit_transform(X_clean)
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_vec, y)
    
    print("✅ Model ready!")
    return model, vectorizer

# Load model at startup
model, vectorizer = load_and_train_model()

# Init history
init_history()

def extract_text_from_image(image_data):
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        text = pytesseract.image_to_string(binary, config=r'--oem 3 --psm 6 -l eng')
        return ' '.join(text.strip().split())
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def predict_news(text):
    cleaned = clean_text(text)
    if len(cleaned) < 10:
        return {'error': 'Text too short'}
    
    vec = vectorizer.transform([cleaned])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0]
    
    return {
        'is_fake': bool(pred == 1),
        'prediction': 'FAKE' if pred == 1 else 'REAL',
        'confidence': round(max(prob) * 100, 2),
        'fake_prob': round(prob[1] * 100, 2),
        'real_prob': round(prob[0] * 100, 2)
    }

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

@app.route('/api/predict/text', methods=['POST'])
def predict_text():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400
    
    title = data.get('title', '')
    text = data['text']
    combined = (title + ' ' + text).strip()
    
    result = predict_news(combined)
    
    if 'error' not in result:
        # Save to history
        save_analysis(
            title=title or text[:100],
            content=text,
            source_type='text',
            prediction=result['prediction'],
            credibility_score=result['confidence'],
            fake_prob=result['fake_prob'],
            real_prob=result['real_prob'],
            red_flags=[]
        )
    
    return jsonify(result)

@app.route('/api/predict/image', methods=['POST'])
def predict_image():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'Missing image'}), 400
    
    extracted = extract_text_from_image(data['image'])
    if not extracted:
        return jsonify({'error': 'Could not extract text from image'}), 400
    
    result = predict_news(extracted)
    result['extracted_text'] = extracted[:300] + '...' if len(extracted) > 300 else extracted
    
    if 'error' not in result:
        # Save to history
        save_analysis(
            title=extracted[:100],
            content=extracted,
            source_type='image',
            prediction=result['prediction'],
            credibility_score=result['confidence'],
            fake_prob=result['fake_prob'],
            real_prob=result['real_prob'],
            red_flags=[]
        )
    
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def history_list():
    """Get history with optional filtering"""
    limit = request.args.get('limit', 50, type=int)
    filter_type = request.args.get('filter_type', 'all')
    
    records = get_history(limit=limit, filter_type=filter_type)
    stats = get_history_stats()
    
    return jsonify({
        'data': records,
        'stats': stats
    })

@app.route('/api/history/<item_id>', methods=['DELETE'])
def history_delete(item_id):
    """Delete a history item"""
    success = delete_history_item(item_id)
    if success:
        return jsonify({'status': 'success', 'message': 'Item deleted'})
    return jsonify({'status': 'error', 'message': 'Item not found'}), 404

@app.route('/api/history/clear/all', methods=['DELETE'])
def history_clear():
    """Clear all history"""
    clear_all_history()
    return jsonify({'status': 'success', 'message': 'History cleared'})

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'ocr_available': True
    })

if __name__ == '__main__':
    print("🚀 Starting API at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)