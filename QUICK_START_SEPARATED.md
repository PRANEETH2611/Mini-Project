# Quick Start Guide - Separated Frontend/Backend

## 🎯 Architecture

- **Frontend**: HTML/CSS/JS in `frontend/` folder
- **Backend**: Python Flask API in `backend/` folder  
- **MongoDB**: ONLY for login tracking (optional)

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Backend

```bash
python backend/app.py
```

You should see:
```
🚀 Starting AIOps Backend API Server...
📊 Data file: ...
📈 Records loaded: 1498
🔐 MongoDB login tracking: Enabled/Disabled
 * Running on http://0.0.0.0:5000
```

### Step 3: Open Frontend

**Option A: Direct File**
- Open `frontend/index.html` in your browser

**Option B: Local Server (Recommended)**
```bash
cd frontend
python -m http.server 8000
```
Then open: `http://localhost:8000`

## 🔐 MongoDB Setup (Optional - Only for Login Tracking)

### If MongoDB is NOT installed:
- Dashboard still works!
- Just no login history tracking

### If MongoDB IS installed:
1. Start MongoDB:
   ```bash
   # Windows
   net start MongoDB
   
   # Mac
   brew services start mongodb-community
   ```

2. Backend will automatically connect
3. Login history will be tracked

## 📊 How It Works

```
User Login
    ↓
Frontend (HTML) → POST /api/login → Backend (Flask)
    ↓
Backend validates → Logs to MongoDB (if connected)
    ↓
Frontend displays dashboard
    ↓
Frontend → GET /api/data → Backend reads CSV
    ↓
Frontend displays charts
```

## ✅ Features

- ✅ Frontend: Pure HTML/CSS/JS (no build needed)
- ✅ Backend: Python Flask REST API
- ✅ Data: CSV files (no database needed)
- ✅ MongoDB: Only for login tracking
- ✅ Login History: View who logged in (admin only)

## 🎨 Frontend Files

- `frontend/index.html` - Main HTML
- `frontend/styles.css` - Styling
- `frontend/app.js` - JavaScript logic

## 🐍 Backend Files

- `backend/app.py` - Flask API server
- `database/login_tracker.py` - MongoDB login tracking

## 🔍 Login History (Admin Only)

1. Login as admin
2. Click "🔐 Login History" tab
3. See all recent logins from MongoDB

That's it! Simple and clean architecture! 🎉
