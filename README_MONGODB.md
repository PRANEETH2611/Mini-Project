# MongoDB Setup Guide for VSCode

## 📋 Table of Contents
1. [Install MongoDB](#install-mongodb)
2. [Connect MongoDB to VSCode](#connect-mongodb-to-vscode)
3. [Configure Project](#configure-project)
4. [Test Connection](#test-connection)
5. [Troubleshooting](#troubleshooting)

---

## 1. Install MongoDB

### Option A: MongoDB Community Server (Recommended)

#### Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer
3. Choose "Complete" installation
4. Install MongoDB as a Windows Service (recommended)
5. Install MongoDB Compass (GUI tool) - optional but helpful

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian):
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Option B: MongoDB Atlas (Cloud - Free Tier Available)
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create a free cluster
4. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

---

## 2. Connect MongoDB to VSCode

### Step 1: Install MongoDB Extension for VSCode

1. Open VSCode
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "MongoDB for VS Code"
4. Install the extension by MongoDB

### Step 2: Connect to MongoDB

1. Click on MongoDB icon in VSCode sidebar (left panel)
2. Click "Add Connection"
3. Enter connection string:
   - **Local MongoDB**: `mongodb://localhost:27017/`
   - **MongoDB Atlas**: Your connection string from Atlas dashboard
4. Click "Connect"

### Step 3: Verify Connection

- You should see your MongoDB instance in the sidebar
- Expand it to see databases and collections
- Right-click to create databases/collections

---

## 3. Configure Project

### Step 1: Install Python Dependencies

```bash
pip install pymongo
```

Or update requirements.txt (already included):
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variable (Optional)

Create a `.env` file in project root:
```env
MONGODB_URI=mongodb://localhost:27017/
```

Or set in your system:
```bash
# Windows PowerShell
$env:MONGODB_URI="mongodb://localhost:27017/"

# Windows CMD
set MONGODB_URI=mongodb://localhost:27017/

# Linux/Mac
export MONGODB_URI="mongodb://localhost:27017/"
```

### Step 3: Update Connection String (if needed)

Edit `database/mongodb_connection.py`:
```python
# For local MongoDB
connection_string = 'mongodb://localhost:27017/'

# For MongoDB Atlas
connection_string = 'mongodb+srv://username:password@cluster.mongodb.net/'
```

---

## 4. Test Connection

### Option A: Using Python Script

Create `test_mongodb.py`:
```python
from database.mongodb_connection import get_database

try:
    db = get_database()
    print("✅ MongoDB connection successful!")
    print(f"Database: {db.mongo.database_name}")
    
    # Test collections
    print(f"Users: {db.users_collection.count_documents({})}")
    print(f"Incidents: {db.incidents_collection.count_documents({})}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run:
```bash
python test_mongodb.py
```

### Option B: Using Streamlit Dashboard

1. Start MongoDB service:
   ```bash
   # Windows (if installed as service, it auto-starts)
   # Or manually:
   mongod
   
   # Linux/Mac
   sudo systemctl start mongod
   # or
   brew services start mongodb-community
   ```

2. Run dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

3. Login with admin credentials
4. Check "Settings" tab for database status

---

## 5. Troubleshooting

### Problem: "Connection refused" or "Cannot connect"

**Solutions:**
1. Check if MongoDB is running:
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl status mongod
   ```

2. Check MongoDB port (default: 27017):
   ```bash
   # Windows
   netstat -an | findstr 27017
   
   # Linux/Mac
   netstat -an | grep 27017
   ```

3. Check MongoDB logs:
   - Windows: `C:\Program Files\MongoDB\Server\6.0\log\mongod.log`
   - Linux: `/var/log/mongodb/mongod.log`
   - Mac: Check with `brew services list`

### Problem: "Authentication failed"

**Solutions:**
1. If using MongoDB Atlas, check username/password
2. If using local MongoDB without auth, remove authentication from connection string
3. Check IP whitelist in MongoDB Atlas (if using cloud)

### Problem: "ModuleNotFoundError: No module named 'pymongo'"

**Solution:**
```bash
pip install pymongo
```

### Problem: "Database not found" or "Collection not found"

**Solution:**
- MongoDB creates databases/collections automatically on first insert
- Run the dashboard and it will create default collections
- Or manually import CSV data using Admin dashboard

### Problem: VSCode MongoDB Extension not working

**Solutions:**
1. Reload VSCode window: `Ctrl+Shift+P` → "Reload Window"
2. Check extension is enabled
3. Try disconnecting and reconnecting
4. Check MongoDB connection string format

---

## 6. MongoDB Atlas Setup (Cloud Option)

### Step 1: Create Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free tier available)

### Step 2: Create Cluster
1. Click "Build a Database"
2. Choose FREE tier (M0)
3. Select cloud provider and region
4. Click "Create"

### Step 3: Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Set username and password (save these!)
5. Set user privileges: "Atlas admin" or "Read and write to any database"

### Step 4: Whitelist IP Address
1. Go to "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for development)
   - Or add your specific IP: `0.0.0.0/0`

### Step 5: Get Connection String
1. Go to "Database" → "Connect"
2. Choose "Connect your application"
3. Copy connection string
4. Replace `<password>` with your database user password
5. Replace `<database>` with your database name (e.g., `aiops_db`)

Example:
```
mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/aiops_db?retryWrites=true&w=majority
```

### Step 6: Update Project
Update `database/mongodb_connection.py`:
```python
connection_string = 'mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/'
```

---

## 7. Useful MongoDB Commands

### Using MongoDB Shell (mongosh)

```bash
# Connect to MongoDB
mongosh

# Show databases
show dbs

# Use database
use aiops_db

# Show collections
show collections

# Find documents
db.incidents.find().limit(5)

# Count documents
db.incidents.countDocuments()

# Find one document
db.incidents.findOne()

# Delete all documents (careful!)
db.incidents.deleteMany({})
```

### Using Python

```python
from database.mongodb_connection import get_database

db = get_database()

# Get all incidents
incidents = db.get_incidents(limit=10)

# Get user
user = db.get_user("admin")

# Import CSV
db.import_csv_to_mongodb("data/processed/final_decision_output.csv")
```

---

## 8. Project Structure

```
AIOPS project/
├── database/
│   └── mongodb_connection.py    # MongoDB connection and operations
├── dashboard/
│   ├── app.py                   # Main entry point (routes to admin/user)
│   ├── admin_dashboard.py        # Admin dashboard
│   └── user_dashboard.py        # User dashboard
├── backend/
│   └── app.py                   # Flask API (can be updated for MongoDB)
└── README_MONGODB.md            # This file
```

---

## 9. Quick Start Checklist

- [ ] Install MongoDB (local or Atlas)
- [ ] Install MongoDB VSCode extension
- [ ] Install Python dependencies (`pip install pymongo`)
- [ ] Start MongoDB service
- [ ] Test connection (`python test_mongodb.py`)
- [ ] Run dashboard (`streamlit run dashboard/app.py`)
- [ ] Login and verify data loads
- [ ] Import CSV data via Admin dashboard

---

## 10. Support

If you encounter issues:
1. Check MongoDB logs
2. Verify MongoDB is running
3. Check connection string format
4. Verify network/firewall settings
5. Check VSCode extension status

For MongoDB Atlas issues:
- Check IP whitelist
- Verify username/password
- Check cluster status in Atlas dashboard

---

## Next Steps

1. **Import Data**: Use Admin dashboard → Data Management → Import CSV
2. **Create Users**: Use Admin dashboard → User Management
3. **View Analytics**: Check Admin dashboard → Advanced Analytics
4. **Monitor System**: Use User dashboard for real-time monitoring

Happy coding! 🚀
