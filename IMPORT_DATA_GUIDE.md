# How to Import Data and Fix Missing Root Cause Options/Graphs

## Problem
- ❌ No root cause options in dropdown
- ❌ No graphs showing
- ❌ "No data found" message

## Solution: Import CSV Data to MongoDB

### Step 1: Login as Admin
1. Run: `streamlit run dashboard/app.py`
2. Login with:
   - Username: `admin`
   - Password: `admin123`

### Step 2: Import Data
1. Go to **"Data Management"** tab (4th tab)
2. Click **"📥 Import CSV to MongoDB"** button
3. Wait for import to complete (shows success message)
4. You should see: "✅ Successfully imported X records!"

### Step 3: Adjust Date Range
The data is from **January 2025**, so:
1. Go to **User Dashboard** or refresh page
2. In sidebar, set **Date Range**:
   - Start Date: **2025-01-01**
   - End Date: **2025-01-31** (or later, depending on your data)

### Step 4: Verify
After importing:
- ✅ Root cause dropdown should show options (NORMAL, CPU_OVERLOAD, etc.)
- ✅ Graphs should appear in Monitoring tab
- ✅ KPI cards should show values
- ✅ Analytics charts should display

## Quick Test

After importing, check:
```bash
python test_mongodb.py
```

You should see:
```
Incidents: 1498 documents  (or similar number)
```

## Troubleshooting

### Still no root cause options?
1. Check date range matches your data dates
2. Make sure import was successful (check count)
3. Try refreshing the page (F5 or click refresh button)

### Still no graphs?
1. Verify data was imported: Check "Settings" tab → Collections count
2. Adjust date range to match your data
3. Check filters aren't too restrictive (try "ALL" for all filters)

### Import button not working?
1. Check CSV file exists: `data/processed/final_decision_output.csv`
2. Check MongoDB is running
3. Look for error messages in the dashboard

## Data File Location
```
AIOPS project/
└── data/
    └── processed/
        └── final_decision_output.csv  ← This file should exist
```

## Expected Data Dates
- Start: 2025-01-01 00:04:00
- End: Check last row in CSV file

## After Import
- Root causes available: NORMAL, CPU_OVERLOAD, MEMORY_LEAK, NETWORK_LATENCY, etc.
- Charts will show: CPU, Memory, Response Time, Failure Probability
- Analytics will display: Root cause distribution, statistics

---

**Remember:** Data must be imported to MongoDB before you can see options and graphs!
