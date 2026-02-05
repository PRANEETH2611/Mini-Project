# How to Connect MongoDB in VSCode - Step by Step

## ✅ Your Connection String
You're using: `mongodb://localhost:27017/`

This is already configured in the code! No changes needed.

---

## 📋 Step-by-Step: Connect MongoDB in VSCode

### Step 1: Install MongoDB Extension

1. Open VSCode
2. Press `Ctrl+Shift+X` (Extensions)
3. Search: **"MongoDB for VS Code"**
4. Install the extension by **MongoDB Inc.**

### Step 2: Connect to MongoDB

1. **Click MongoDB icon** in left sidebar (looks like a leaf/leaf icon)
   
   OR
   
   Press `Ctrl+Shift+P` → Type "MongoDB: Add Connection"

2. **Enter connection string:**
   ```
   mongodb://localhost:27017/
   ```

3. **Press Enter**

4. You should see:
   - ✅ Connection successful
   - Your connection appears in sidebar

### Step 3: Browse Your Database

1. **Expand the connection** in sidebar
2. You'll see databases:
   - `admin`
   - `config`
   - `local`
   - `aiops_db` (created when you first run the app)

3. **Expand `aiops_db`** to see collections:
   - `users`
   - `incidents`
   - `metrics`
   - `alerts`

4. **Click on collections** to view documents

---

## 🎯 Where the Connection is Configured in Code

### File: `database/mongodb_connection.py`

**Line 22-26:**
```python
if connection_string is None:
    connection_string = os.getenv(
        'MONGODB_URI', 
        'mongodb://localhost:27017/'  # ← Your connection string is here
    )
```

**This means:**
- ✅ Code automatically uses `mongodb://localhost:27017/` by default
- ✅ No file editing needed!
- ✅ Just make sure MongoDB is running

---

## 🧪 Test Your Connection

### Method 1: Run Test Script
```bash
python test_mongodb.py
```

Expected output:
```
✅ Connected to MongoDB: aiops_db
✅ All tests passed!
```

### Method 2: Run Dashboard
```bash
streamlit run dashboard/app.py
```

If connection works, you'll see the login page.
If it fails, you'll see an error message.

---

## 🔍 Verify MongoDB is Running

### Windows:
```powershell
# Check if MongoDB service is running
Get-Service MongoDB

# Or start it manually
net start MongoDB
```

### Mac:
```bash
# Check status
brew services list

# Start if needed
brew services start mongodb-community
```

### Linux:
```bash
# Check status
sudo systemctl status mongod

# Start if needed
sudo systemctl start mongod
```

---

## 📊 What You'll See in VSCode

After connecting, you can:

1. **View Collections:**
   - Right-click on collection → "View Collection"
   - See all documents in a table

2. **Query Data:**
   - Right-click on collection → "Run MongoDB Command"
   - Run queries like: `db.incidents.find().limit(10)`

3. **Create Documents:**
   - Right-click on collection → "Insert Document"
   - Add new data

4. **Delete Documents:**
   - Right-click on document → "Delete Document"

---

## 🎨 Visual Guide

```
VSCode Sidebar:
├── 📁 Explorer
├── 🔍 Search
├── 🌿 MongoDB          ← Click here!
│   └── mongodb://localhost:27017/
│       └── aiops_db
│           ├── users
│           ├── incidents
│           ├── metrics
│           └── alerts
└── ...
```

---

## ❌ Troubleshooting

### Problem: "Connection failed" in VSCode

**Solution:**
1. Make sure MongoDB is running:
   ```bash
   # Windows
   net start MongoDB
   
   # Mac
   brew services start mongodb-community
   ```

2. Check if port 27017 is open:
   ```bash
   # Windows
   netstat -an | findstr 27017
   
   # Mac/Linux
   netstat -an | grep 27017
   ```

3. Try reconnecting in VSCode

### Problem: "Extension not found"

**Solution:**
- Make sure you installed "MongoDB for VS Code" (by MongoDB Inc.)
- Not "MongoDB" by other developers
- Reload VSCode window: `Ctrl+Shift+P` → "Reload Window"

### Problem: "Database not showing"

**Solution:**
- Database `aiops_db` is created automatically when you first run the app
- Run: `streamlit run dashboard/app.py` once
- Or run: `python test_mongodb.py`
- Then refresh VSCode MongoDB view

---

## ✅ Quick Checklist

- [ ] MongoDB installed and running
- [ ] VSCode MongoDB extension installed
- [ ] Connection added: `mongodb://localhost:27017/`
- [ ] Connection shows as connected in VSCode
- [ ] Can see `aiops_db` database
- [ ] Test script works: `python test_mongodb.py`

---

## 🚀 Next Steps

1. **Connect in VSCode** (using extension)
2. **Run test**: `python test_mongodb.py`
3. **Start dashboard**: `streamlit run dashboard/app.py`
4. **Login and import data** (as admin)
5. **View data in VSCode** MongoDB extension

---

## 💡 Pro Tips

1. **Keep VSCode MongoDB extension open** while developing
2. **Use it to verify data** after importing CSV
3. **Run queries** directly in VSCode instead of MongoDB shell
4. **View documents** in a nice table format

That's it! Your connection string is already configured. Just connect via the VSCode extension! 🎉
