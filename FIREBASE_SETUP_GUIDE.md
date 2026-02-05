# 🔥 Firebase Firestore Setup Guide for Login Tracking

This guide explains how to **replace MongoDB with Google Firebase Firestore** for login tracking in your AIOps Dashboard project.

---

## 📋 Overview

### Current Setup (MongoDB)
- Uses MongoDB for login tracking only
- Stores: username, role, timestamp, IP address, user agent, status
- Location: `database/login_tracker.py`

### Proposed Setup (Firebase)
- Replace MongoDB with Firebase Firestore
- Same data structure and functionality
- Cloud-based, no local database server needed
- Better for production deployments

---

## 🎯 Why Firebase Instead of MongoDB?

### Advantages:
✅ **No Local Server** - No need to install/run MongoDB locally  
✅ **Cloud-Based** - Access from anywhere, automatic backups  
✅ **Free Tier** - Generous free tier for small projects  
✅ **Easy Setup** - Simple configuration with JSON credentials  
✅ **Scalable** - Automatically scales with your needs  
✅ **Real-time** - Built-in real-time capabilities (if needed later)

### Considerations:
⚠️ **Internet Required** - Needs internet connection  
⚠️ **Cost** - Free tier has limits, may cost for high usage  
⚠️ **Learning Curve** - Different API than MongoDB

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or select existing project
3. Enter project name (e.g., "aiops-dashboard")
4. Follow setup wizard:
   - Google Analytics: Optional (can disable)
   - Click **"Create project"**
5. Wait for project creation (30-60 seconds)

### Step 2: Enable Firestore Database

1. In Firebase Console, click **"Firestore Database"** in left sidebar
2. Click **"Create database"**
3. Choose mode:
   - **Test mode** (for development) - Allows read/write for 30 days
   - **Production mode** (for production) - Requires security rules
4. Select database location (choose closest to your users)
5. Click **"Enable"**

### Step 3: Create Service Account (For Admin SDK)

1. Go to **Project Settings** (gear icon ⚙️) → **"Service accounts"** tab
2. Click **"Generate new private key"** button
3. A JSON file will download - **SAVE THIS FILE SECURELY!**
4. This file contains:
   - Project ID
   - Private key
   - Client email
   - All credentials needed for authentication

**⚠️ SECURITY WARNING:** Never commit this file to Git! It has full admin access.

### Step 4: Set Up Security Rules

1. Go to **Firestore Database** → **"Rules"** tab
2. For development, use:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write for development
    match /user_logins/{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click **"Publish"**

**For Production**, use stricter rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /user_logins/{document=**} {
      // Only allow authenticated admin access
      allow read, write: if request.auth != null && 
                           request.auth.token.admin == true;
    }
  }
}
```

---

## 🔧 Configuration Options

### Option 1: Using Credentials File (Recommended for Development)

1. Place downloaded JSON file in project directory:
   ```
   D:\Downloads\AIOPS project\firebase-credentials.json
   ```

2. Add to `.gitignore`:
   ```
   firebase-credentials.json
   *-firebase-adminsdk-*.json
   ```

3. Set environment variable:

**Windows PowerShell:**
```powershell
$env:FIREBASE_CREDENTIALS_PATH="D:\Downloads\AIOPS project\firebase-credentials.json"
```

**Windows CMD:**
```cmd
set FIREBASE_CREDENTIALS_PATH=D:\Downloads\AIOPS project\firebase-credentials.json
```

**Linux/Mac:**
```bash
export FIREBASE_CREDENTIALS_PATH="/path/to/firebase-credentials.json"
```

### Option 2: Using GOOGLE_APPLICATION_CREDENTIALS (Recommended for Production)

**Windows:**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\Downloads\AIOPS project\firebase-credentials.json"
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/firebase-credentials.json"
```

### Option 3: Default Credentials (Google Cloud Environments)

If running on Google Cloud Platform (App Engine, Cloud Run, Compute Engine), Firebase Admin SDK automatically uses default credentials - no configuration needed!

---

## 📦 Installation

### Install Firebase Admin SDK

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install Firebase Admin SDK
pip install firebase-admin

# Or update requirements.txt and install all
pip install -r requirements.txt
```

### Update requirements.txt

Replace:
```
pymongo
```

With:
```
firebase-admin
```

---

## 🔄 Code Changes Required

### 1. Update `database/login_tracker.py`

**Current (MongoDB):**
- Uses `pymongo.MongoClient`
- Connects to `mongodb://localhost:27017/`
- Uses MongoDB collections and queries

**New (Firebase):**
- Uses `firebase_admin` and `firestore`
- Connects using service account credentials
- Uses Firestore collections and queries

**Key Changes:**
- Replace `MongoClient` with `firestore.client()`
- Replace `collection.insert_one()` with `collection.add()`
- Replace MongoDB queries with Firestore queries
- Handle Firestore timestamps differently

### 2. Update `backend/app.py`

**Minimal changes needed:**
- Update comments from "MongoDB" to "Firebase"
- Update health check endpoint response
- All API endpoints remain the same!

### 3. Update `requirements.txt`

- Remove: `pymongo`
- Add: `firebase-admin`

---

## 📊 Firestore Data Structure

After migration, your Firestore will have:

```
Project: aiops-dashboard
└── Collection: user_logins
    ├── Document 1
    │   ├── username: "admin"
    │   ├── role: "ADMIN"
    │   ├── timestamp: Timestamp (2026-02-02 10:30:00)
    │   ├── ip_address: "127.0.0.1"
    │   ├── user_agent: "Mozilla/5.0..."
    │   └── status: "success"
    ├── Document 2
    │   └── ... (failed login)
    └── ...
```

---

## ✅ Testing

### Test Script

Create `test_firebase.py`:

```python
from database.login_tracker import get_login_tracker

# Initialize
tracker = get_login_tracker()

# Test login logging
success = tracker.log_login(
    username="test_user",
    role="USER",
    ip_address="127.0.0.1",
    user_agent="Test Agent"
)

if success:
    print("✅ Firebase connection successful!")
    
    # Test retrieving
    logins = tracker.get_recent_logins(limit=5)
    print(f"✅ Retrieved {len(logins)} logins")
    
    # Test stats
    stats = tracker.get_login_stats()
    print(f"✅ Stats: {stats}")
else:
    print("❌ Connection failed")
```

Run:
```bash
python test_firebase.py
```

---

## 🔒 Security Best Practices

1. **Never Commit Credentials**
   - Add `firebase-credentials.json` to `.gitignore`
   - Use environment variables in production

2. **Use Proper Security Rules**
   - Start with test mode for development
   - Implement proper authentication for production

3. **Rotate Credentials**
   - Generate new service account keys periodically
   - Revoke old keys in Firebase Console

4. **Limit Permissions**
   - Service account should only have Firestore access
   - Use principle of least privilege

---

## 💰 Firebase Pricing

### Free Tier (Spark Plan)
- **50,000 reads/day**
- **20,000 writes/day**
- **20,000 deletes/day**
- Perfect for development and small projects

### Paid Tier (Blaze Plan - Pay as you go)
- **$0.06 per 100,000 document reads**
- **$0.18 per 100,000 document writes**
- **$0.02 per 100,000 document deletes**
- Very affordable for most projects

**For login tracking:** Even with 1000 logins/day, you're well within free tier!

---

## 🐛 Troubleshooting

### Error: "firebase-admin not installed"
**Solution:** `pip install firebase-admin`

### Error: "Failed to initialize Firebase"
**Solutions:**
- Check credentials file path is correct
- Verify JSON file is valid
- Ensure environment variables are set

### Error: "Permission denied"
**Solutions:**
- Check Firestore security rules
- Verify service account has proper permissions
- Ensure database is created and enabled

### Error: "Project ID not found"
**Solutions:**
- Set `FIREBASE_PROJECT_ID` environment variable
- Or ensure project ID is in credentials JSON

---

## 📝 Migration Checklist

- [ ] Create Firebase project
- [ ] Enable Firestore database
- [ ] Download service account JSON
- [ ] Set up security rules
- [ ] Set environment variables
- [ ] Install firebase-admin
- [ ] Update login_tracker.py code
- [ ] Update requirements.txt
- [ ] Test connection
- [ ] Update backend/app.py comments
- [ ] Test all login tracking functions
- [ ] Verify in Firebase Console

---

## 🎯 Next Steps

1. **Review this guide** - Understand what needs to change
2. **Set up Firebase** - Follow steps 1-4 above
3. **Decide if you want to implement** - Consider pros/cons
4. **If yes, I can implement** - I'll update all code for you!

---

## ❓ Questions to Consider

1. **Do you need cloud-based database?** (Firebase advantage)
2. **Do you prefer local database?** (MongoDB advantage)
3. **Will you deploy to cloud?** (Firebase better)
4. **Do you need real-time features?** (Firebase has built-in)
5. **Budget concerns?** (Both have free tiers)

---

**Ready to implement?** Let me know and I'll update all the code for you! 🔥
