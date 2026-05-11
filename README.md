## 📥 Step 1: Download This Project

### Option A: Download ZIP (Easiest)
1. Go to your GitHub repository page
2. Click the green **<> Code** button
3. Click **Download ZIP**
4. Extract the ZIP to your Desktop
5. Rename the folder to: `Fake News Detector`

### Option B: Using Git (If installed)
```powershell
cd Desktop
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)

```

## 🧹 Step 2: Clean Up — Remove These Files

These files were created on Linux and will NOT work on Windows. Delete them:

| File/Folder | Why Delete? |
| --- | --- |
| `venv/` | Linux Python environment — Windows needs its own |
| `__pycache__/` | Linux compiled Python cache |
| `start.sh` | Linux shell script — we will make `start.bat` |
| `scraper.sh` | Linux shell script — we will make `scraper.bat` |
| `.ipynb_checkpoints/` | Jupyter notebook cache |
| `live_news_dataset.csv` | Will be auto-created on first run |
| `history.csv` | Will be auto-created on first check |

**Files you MUST keep:**
`api.py`, `history.py`, `Scraper.py`, `fake_or_real_news.csv`, `fake_news_model.pkl`, `index.html`, `script.js`, `style.css`, `requirements.txt`

---

## 🐍 Step 3: Install Python on Windows

1. **Download:** Open browser → [python.org/downloads](https://www.python.org/downloads/)
2. Click **"Download Python 3.11.x"**
3. **Install:** Open the downloaded `.exe` file.
4. ⚠️ **VERY IMPORTANT:** Check the box **"Add python.exe to PATH"**.
5. Click **"Install Now"** and wait for it to finish.
6. **Verify:** Press `Win + R`, type `cmd`, press Enter. Type:
```cmd
python --version

```


If you see `Python 3.11.x`, you are good to go!

---

## 🔍 Step 4: Install Tesseract OCR (For Image Analysis)

*Required only for image-to-text analysis.*

1. Download the installer: [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the `.exe` file.
3. During installation, select **"Install for anyone using this computer"**.
4. Click Finish and **Restart your computer**.

---

## 📄 Step 5: Create requirements.txt

If missing, create a new text file named `requirements.txt` and paste:

```txt
flask==3.0.0
flask-cors==4.0.0
scikit-learn==1.3.2
joblib==1.3.2
numpy==1.26.0
pandas==2.1.0
Pillow==10.0.0
pytesseract==0.3.10
opencv-python-headless==4.8.1.78
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3

```

---

## 🚀 Step 6: Create start.bat (API Launcher)

1. Right-click in project folder → **New** → **Text Document**.
2. Name it `start.bat` (Ensure it's not `start.bat.txt`).
3. Right-click → **Edit** and paste:

```batch
@echo off
chcp 65001 >nul
title Fake News Detector - API Server
color 0A
echo ==========================================
echo    FAKE NEWS DETECTOR - WINDOWS
echo ==========================================
echo.
cd /d "%~dp0"
if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)
echo [2/3] Activating environment...
call venv\Scripts\activate.bat
echo [3/3] Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting API Server at http://localhost:5000
python api.py
pause

```

---

## 🌐 Step 7: Create scraper.bat (Optional)

1. Create `scraper.bat` in the same way.
2. Paste this:

```batch
@echo off
title Fake News Detector - News Scraper
color 0E
cd /d "%~dp0"
call venv\\Scripts\\activate.bat
echo Starting scraper (Updates every 5 mins)...
python Scraper.py
pause

```

---

## ▶️ Step 8: Run the Application

1. Double-click `start.bat`.
2. Wait for the message: `🚀 Starting API at http://localhost:5000`.
3. Open your browser and go to: `http://localhost:5000`.

---

## 📂 Final Folder Structure

```text
Fake News Detector/
├── api.py
├── Scraper.py
├── index.html
├── style.css
├── script.js
├── requirements.txt
├── start.bat
└── scraper.bat

```

---

## 🐛 Troubleshooting

| Problem | Solution |
| --- | --- |
| `python` not recognized | Reinstall Python and check "Add to PATH" |
| Port 5000 in use | Change port in `api.py`: `app.run(port=8080)` |
| Execution Policy Error | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell |

---

## 👥 Developed By

| Name | Roll Number |
| --- | --- |
| Ayesha Zubairi | 2022-GCUF-074424 |
| Maira Tariq | 2022-GCUF-074274 |
| Urba Tariq | 2022-GCUF-074277 |

**Institution:** Government College University, Faisalabad (GCUF)
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(readme_content)
