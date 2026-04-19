
#!/usr/bin/env python3
"""
FAKE NEWS DETECTOR - TERMINAL VERSION
"""

import os
import sys
import re
import joblib

# Try to import optional image processing
try:
    import pytesseract
    from PIL import Image
    import cv2
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

# ============== CONFIG ==============
MODEL_PATH = 'fake_news_model.pkl'
TESSERACT_CMD = '/usr/bin/tesseract'

# ============== STOP WORDS ==============
STOP_WORDS = set(['i','me','my','myself','we','our','ours','ourselves','you','your','yours',
'yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its',
'itself','they','them','their','theirs','themselves','what','which','who','whom','this',
'that','these','those','am','is','are','was','were','be','been','being','have','has','had',
'having','do','does','did','doing','a','an','the','and','but','if','or','because','as',
'until','while','of','at','by','for','with','about','against','between','into','through',
'during','before','after','above','below','up','down','in','out','on','off','over','under',
'again','further','then','once','here','there','when','where','why','how','all','any',
'both','each','few','more','most','other','some','such','no','nor','not','only','own',
'same','so','than','too','very','s','t','can','will','just','don','should','now'])

def clean_text(text):
    """Clean text"""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return ' '.join(words)

def load_model():
    """Load model"""
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found: {MODEL_PATH}")
        print("Copy fake_news_model.pkl from Jupyter to this folder")
        sys.exit(1)
    
    print("⏳ Loading model...")
    package = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded! Accuracy: {package.get('accuracy', 'Unknown')}")
    return package

def preprocess_image(image_path):
    """Prepare image"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    h, w = binary.shape
    if h < 1000:
        binary = cv2.resize(binary, None, fx=1000/h, fy=1000/h)
    return binary

def extract_text_from_image(image_path):
    """OCR"""
    if not IMAGE_SUPPORT:
        return None, "Image libs not installed"
    
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    
    try:
        processed = preprocess_image(image_path)
        if processed is None:
            return None, "Could not load image"
        
        text = pytesseract.image_to_string(processed, config=r'--oem 3 --psm 6 -l eng')
        text = ' '.join(text.strip().split())
        return text, None
    except Exception as e:
        return None, str(e)

def predict_text(model_data, title, text):
    """Predict from text"""
    combined = str(title) + ' ' + str(text)
    cleaned = clean_text(combined)
    
    if len(cleaned) < 10:
        return {'error': 'Text too short'}
    
    vectorized = model_data['vectorizer'].transform([cleaned])
    prediction = model_data['model'].predict(vectorized)[0]
    prob = model_data['model'].predict_proba(vectorized)[0]
    
    return {
        'is_fake': bool(prediction == 1),
        'prediction': 'FAKE' if prediction == 1 else 'REAL',
        'confidence': max(prob) * 100,
        'fake_prob': prob[1] * 100,
        'real_prob': prob[0] * 100
    }

def predict_image(model_data, image_path):
    """Predict from image"""
    print("🔍 Extracting text...")
    extracted, error = extract_text_from_image(image_path)
    
    if error:
        return {'error': error}
    
    if not extracted or len(extracted) < 20:
        return {'error': 'Not enough text in image'}
    
    print(f"   ✓ {len(extracted)} chars extracted")
    return predict_text(model_data, extracted[:100], extracted)

def show_result(result, input_type):
    """Display result"""
    if 'error' in result:
        print(f"\n❌ {result['error']}")
        return
    
    print("\n" + "="*50)
    print(f"📊 RESULT ({input_type})")
    print("="*50)
    
    if result['is_fake']:
        print("\n🔴🔴🔴  FAKE NEWS DETECTED  🔴🔴🔴")
    else:
        print("\n🟢🟢🟢  REAL NEWS DETECTED  🟢🟢🟢")
    
    print(f"\nConfidence: {result['confidence']:.2f}%")
    print(f"  FAKE: {result['fake_prob']:.2f}% | REAL: {result['real_prob']:.2f}%")
    print("="*50)

def main():
    """Main"""
    print("="*50)
    print("🕵️  FAKE NEWS DETECTOR")
    print("="*50)
    
    model_data = load_model()
    print(f"Image support: {'✅' if IMAGE_SUPPORT else '❌'}\n")
    
    while True:
        print("-"*50)
        print("1. Text input  |  2. Image input  |  q. Quit")
        print("-"*50)
        
        choice = input("Choice: ").strip().lower()
        
        if choice == '1':
            print("\n📝 TEXT INPUT")
            title = input("Title: ").strip()
            print("Text (Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            text = '\n'.join(lines).strip()
            
            if title and text:
                result = predict_text(model_data, title, text)
                show_result(result, "TEXT")
            else:
                print("❌ Need both title and text")
        
        elif choice == '2':
            if not IMAGE_SUPPORT:
                print("❌ Install: pip install pytesseract pillow opencv-python-headless")
                continue
            
            print("\n🖼️  IMAGE INPUT")
            path = input("Image path: ").strip().strip('"').strip("'")
            
            if not os.path.exists(path):
                print(f"❌ Not found: {path}")
                continue
            
            result = predict_image(model_data, path)
            show_result(result, "IMAGE")
        
        elif choice == 'q':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
