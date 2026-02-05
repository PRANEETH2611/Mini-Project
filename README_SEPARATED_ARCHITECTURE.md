# Separated Frontend/Backend Architecture

## 📁 Project Structure

```
AIOPS project/
├── frontend/              # Frontend (HTML, CSS, JavaScript)
│   ├── index.html        # Main HTML file
│   ├── styles.css        # CSS styling
│   └── app.js            # JavaScript logic
│
├── backend/              # Backend (Python Flask API)
│   └── app.py           # Flask REST API server
│
├── database/            # Database utilities
│   └── login_tracker.py # MongoDB login tracking ONLY
│
└── data/               # CSV data files
    └── processed/
        └── final_decision_output.csv
```

## 🎯 Architecture Overview

### Frontend (HTML/CSS/JS)
- **Location**: `frontend/` folder
- **Technology**: Pure HTML5, CSS3, JavaScript (Vanilla JS)
- **Charts**: Plotly.js (CDN)
- **No build process needed** - Just open HTML file!

### Backend (Python Flask)
- **Location**: `backend/` folder
- **Technology**: Flask REST API
- **Data Source**: CSV files (no database needed for data)
- **MongoDB**: Used ONLY for login tracking

### MongoDB Usage
- **Purpose**: Login tracking ONLY
- **Collections**: `user_logins` (stores login records)
- **Not required**: Dashboard works without MongoDB (just no login tracking)

## 🚀 How to Run

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Backend (Terminal 1)

```bash
python backend/app.py
```

Backend will run on: `http://localhost:5000`

### Step 3: Open Frontend (Terminal 2)

**Option A: Direct File Open**
- Open `frontend/index.html` in your browser

**Option B: Local Server (Recommended)**
```bash
cd frontend
python -m http.server 8000
```
Then open: `http://localhost:8000`

## 🔐 MongoDB Login Tracking

### Setup MongoDB (Optional)

1. **Install MongoDB** (if not installed)
   - Windows: Download from mongodb.com
   - Mac: `brew install mongodb-community`
   - Linux: `sudo apt-get install mongodb`

2. **Start MongoDB**
   ```bash
   # Windows
   net start MongoDB
   
   # Mac/Linux
   brew services start mongodb-community
   # or
   sudo systemctl start mongod
   ```

3. **Connection String**
   - Default: `mongodb://localhost:27017/`
   - Set environment variable: `MONGODB_URI=mongodb://localhost:27017/`

### What Gets Tracked

When users login, MongoDB stores:
- Username
- Role (ADMIN/USER)
- Login timestamp
- IP address
- User agent (browser info)
- Status (success/failed)

### View Login History

1. Login as **admin**
2. Go to **"Login History"** tab
3. See all recent logins from MongoDB

## 📊 Data Flow

```
User Login
    ↓
Frontend (HTML/JS) → POST /api/login
    ↓
Backend (Flask) → Validates credentials
    ↓
MongoDB → Logs login (if connected)
    ↓
Frontend → Displays dashboard
    ↓
Frontend → GET /api/data
    ↓
Backend → Reads CSV file
    ↓
Frontend → Displays charts & data
```

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User login (tracks in MongoDB)

### Data
- `GET /api/data` - Get filtered dashboard data (from CSV)
- `GET /api/kpi` - Get KPI metrics
- `GET /api/analytics` - Get analytics data
- `GET /api/insights` - Get AI insights
- `GET /api/options` - Get filter options

### Login Tracking (Admin Only)
- `GET /api/login-history` - Get recent logins from MongoDB
- `GET /api/login-stats` - Get login statistics

## 📝 Key Features

### Frontend Features
- ✅ Modern, responsive UI
- ✅ Interactive Plotly charts
- ✅ Real-time data updates
- ✅ Filtering and date range selection
- ✅ Login history view (admin only)

### Backend Features
- ✅ RESTful API
- ✅ CSV data reading
- ✅ MongoDB login tracking
- ✅ CORS enabled for frontend
- ✅ Error handling

### MongoDB Features
- ✅ Login tracking only
- ✅ Stores login records
- ✅ Login history view
- ✅ Statistics tracking
- ✅ Optional (dashboard works without it)

## 🎨 Frontend Structure

### HTML (`index.html`)
- Login modal
- Dashboard layout
- KPI cards
- Charts containers
- Tabs structure

### CSS (`styles.css`)
- Modern gradient designs
- Responsive layout
- Dark theme
- Card styling
- Animations

### JavaScript (`app.js`)
- API calls to backend
- Chart rendering (Plotly)
- Filter handling
- Tab switching
- Login management

## 🐍 Backend Structure

### Flask App (`backend/app.py`)
- REST API endpoints
- CSV data loading
- Login validation
- MongoDB login tracking
- Data filtering
- Statistics calculation

## 🔍 MongoDB Collections

### `user_logins`
```json
{
  "username": "admin",
  "role": "ADMIN",
  "timestamp": "2025-01-15T10:30:00",
  "ip_address": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "status": "success"
}
```

## ⚙️ Configuration

### Backend Configuration
- **Port**: 5000 (default)
- **Host**: 0.0.0.0 (all interfaces)
- **Debug**: True (development mode)

### MongoDB Configuration
- **Connection**: `mongodb://localhost:27017/`
- **Database**: `aiops_db`
- **Collection**: `user_logins`

### Frontend Configuration
- **API URL**: `http://localhost:5000/api` (in `app.js`)

## 🐛 Troubleshooting

### Backend not starting?
- Check if port 5000 is available
- Verify CSV file exists: `data/processed/final_decision_output.csv`
- Check Python dependencies installed

### Frontend not connecting?
- Verify backend is running on port 5000
- Check browser console for errors
- Verify CORS is enabled in backend

### MongoDB not tracking?
- Check MongoDB is running
- Verify connection string
- Check backend logs for MongoDB errors
- Dashboard still works without MongoDB!

### Charts not showing?
- Check browser console for errors
- Verify Plotly.js is loading (CDN)
- Check data is being returned from API

## ✅ Benefits of This Architecture

1. **Separation of Concerns**: Frontend and backend are separate
2. **Scalability**: Can deploy frontend and backend separately
3. **Flexibility**: Easy to change frontend or backend independently
4. **MongoDB Optional**: Dashboard works without MongoDB
5. **Login Tracking**: MongoDB only used for login history
6. **No Build Process**: Frontend is pure HTML/CSS/JS
7. **Easy Development**: Simple file structure

## 🎯 Summary

- **Frontend**: HTML/CSS/JS in `frontend/` folder
- **Backend**: Python Flask in `backend/` folder
- **MongoDB**: Only for login tracking (optional)
- **Data**: CSV files (no database needed)
- **Simple**: No complex build processes!

Happy coding! 🚀
