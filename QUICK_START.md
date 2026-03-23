# Quick Start Guide - MongoDB + Separate Admin/User Dashboards

## 🚀 Quick Setup (5 minutes)

### Step 1: Install MongoDB

**Windows:**
- Download from: https://www.mongodb.com/try/download/community
- Install with default settings
- MongoDB will start automatically as a service

**Mac:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongod
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test MongoDB Connection

```bash
python test_mongodb.py
```

You should see: ✅ All tests passed!

### Step 4: Run Backend + Streamlit Dashboard (single command)

```bash
python run_all.py
```

This starts:
- Flask backend API at `http://localhost:5000`
- Streamlit frontend at `http://localhost:8501`

### Step 5: Login

- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

---

## 📁 Project Structure

```
AIOPS project/
├── database/
│   └── mongodb_connection.py    # MongoDB operations
├── dashboard/
│   ├── app.py                   # Main login page (routes to admin/user)
│   ├── admin_dashboard.py       # 👨‍💼 Admin dashboard
│   └── user_dashboard.py        # 👤 User dashboard
├── test_mongodb.py              # Test MongoDB connection
└── README_MONGODB.md            # Detailed MongoDB setup guide
```

---

## 🎯 Features

### Admin Dashboard (`admin_dashboard.py`)
- ✅ User Management (add/edit users)
- ✅ System Overview & Statistics
- ✅ Advanced Analytics
- ✅ Data Management (import CSV)
- ✅ System Settings

### User Dashboard (`user_dashboard.py`)
- ✅ Real-time Monitoring
- ✅ KPI Cards
- ✅ Incident Tracking
- ✅ Charts & Analytics
- ✅ Filtering Options
- ✅ AI-based automatic resolution suggestions for anomalies
- ✅ Groq/Gemini-powered AI command center and runbook generation

---

## 🔧 MongoDB Connection

### Local MongoDB (Default)
```python
# Uses: mongodb://localhost:27017/
# Database: aiops_db
```

### MongoDB Atlas (Cloud)
1. Get connection string from Atlas dashboard
2. Update `database/mongodb_connection.py`:
```python
connection_string = 'mongodb+srv://username:password@cluster.mongodb.net/'
```

---

## 📊 Import Data

1. Login as **admin**
2. Go to **Data Management** tab
3. Click **"Import CSV to MongoDB"**
4. Data will be imported from `data/processed/final_decision_output.csv`

---

## 🐛 Troubleshooting

### MongoDB Not Connecting?
```bash
# Check if MongoDB is running
# Windows
net start MongoDB

# Mac/Linux
brew services list
# or
sudo systemctl status mongod
```

### Import Errors?
- Make sure CSV file exists: `data/processed/final_decision_output.csv`
- Check file permissions
- Verify CSV format matches expected schema

### Dashboard Not Loading?
- Check MongoDB connection: `python test_mongodb.py`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Streamlit version: `streamlit --version`

---

## 📖 More Information

- **MongoDB Setup**: See `README_MONGODB.md`
- **Architecture**: See `README_ARCHITECTURE.md`
- **API Documentation**: See `backend/app.py` (Flask API)

---

## 🎉 You're Ready!

1. ✅ MongoDB installed and running
2. ✅ Dependencies installed
3. ✅ Connection tested
4. ✅ Dashboard running
5. ✅ Logged in as admin/user

**Next Steps:**
- Import your CSV data
- Explore admin dashboard features
- Check user dashboard for monitoring
- Customize dashboards as needed

Happy coding! 🚀
