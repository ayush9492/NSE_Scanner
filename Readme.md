# 🔍 NSE Stock Scanner — RS New High + Buy Signal

A web-based stock scanner that scans 180+ NSE stocks for **Relative Strength New Highs** and multi-factor **Buy Signals**, then surfaces the intersection as final picks.

> ⚠️ **Disclaimer**: For educational purposes only. Not financial advice.

![Scanner Preview](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=flat&logo=react)

---

## 📋 What It Scans

| Filter | Criteria |
|--------|----------|
| **RS New High** | Relative Strength vs Nifty 50 making a new 123-day high |
| **DI+ Jump** | Plus DI increases by ≥ 10 in one day (5-period) |
| **EMA Stack** | EMA 10 > EMA 20 > EMA 50 |
| **Weekly RSI** | Weekly RSI ≥ 59 |
| **SMA Trend** | 50-day SMA rising for 5 consecutive days |
| **Volume** | Above 20-day average + ₹5Cr minimum trade value |

**Final Picks** = Stocks hitting BOTH RS New High AND all Buy Signal conditions.

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- TA-Lib C library (see below)

### 1. Install TA-Lib C Library

**macOS:**
```bash
brew install ta-lib
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib && ./configure --prefix=/usr && make && sudo make install
```

**Windows:**
Download the prebuilt wheel from https://github.com/cgohlke/talib-build/releases

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Server

```bash
cd backend
python app.py
```

### 4. Open the App

- **API**: http://localhost:8000
- **Frontend**: http://localhost:8000/app
- Or open `frontend/index.html` directly in your browser

---

## ☁️ Deploy to the Cloud (Free Options)

### Option A: Railway (Easiest — Free Tier)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app)
3. Click **"New Project" → "Deploy from GitHub"**
4. Select your repo
5. Set the start command:
   ```
   cd backend && pip install -r requirements.txt && uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
6. Railway gives you a public URL — share it with anyone!

### Option B: Render (Free Tier)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo
4. Settings:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Deploy — you'll get a `.onrender.com` URL

### Option C: Google Colab (Quick Demo)

```python
# In a Colab notebook:
!pip install fastapi uvicorn yfinance TA-Lib pyngrok

# Copy app.py content into a cell, then:
from pyngrok import ngrok
import uvicorn, threading

# Start server in background
thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host":"0.0.0.0", "port":8000})
thread.daemon = True
thread.start()

# Create public URL
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")
```

### Option D: VPS (DigitalOcean / AWS EC2)

```bash
# On your server:
git clone <your-repo>
cd stock-scanner/backend
pip install -r requirements.txt
# Run with auto-restart:
nohup uvicorn app:app --host 0.0.0.0 --port 8000 &
```

---

## 📁 Project Structure

```
stock-scanner/
├── backend/
│   ├── app.py              # FastAPI server + scanner logic
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # React SPA (single file, no build needed)
├── Dockerfile              # Container deployment
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/scan` | Start a background scan |
| `GET` | `/status` | Get scan progress (poll this) |
| `GET` | `/results` | Get full scan results |
| `GET` | `/stock/{symbol}` | Get chart data for a single stock |
| `GET` | `/app` | Serve the frontend UI |

---

## 🛠️ Customization

### Add/Remove Stocks
Edit the `STOCK_LIST` array in `backend/app.py`.

### Change Scan Parameters
In `backend/app.py`, modify:
- `high_period=123` — RS lookback window
- `timeperiod=5` — DI/ADX period
- `timeperiod=10/20/50` — EMA periods
- `>= 59` — Weekly RSI threshold
- `> 50_000_000` — Minimum volume value

### Change Backend URL
In `frontend/index.html`, update the `API_BASE` variable or set `window.API_BASE` before the script loads.

---

## 📝 License

MIT — Use freely, modify as you like.