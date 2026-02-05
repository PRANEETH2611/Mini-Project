# 🚀 Run Streamlit Dashboard - Quick Start

## Commands to Start Dashboard

### Option 1: Using Virtual Environment (Recommended)

**Windows PowerShell:**
```powershell
# Navigate to project directory
cd "D:\Downloads\AIOPS project"

# Activate virtual environment
.\venv\Scripts\activate

# Run Streamlit dashboard
streamlit run dashboard/app.py
```

**Windows CMD:**
```cmd
cd "D:\Downloads\AIOPS project"
venv\Scripts\activate
streamlit run dashboard/app.py
```

**Linux/Mac:**
```bash
cd "/path/to/AIOPS project"
source venv/bin/activate
streamlit run dashboard/app.py
```

### Option 2: Direct Run (If Streamlit is installed globally)

```bash
streamlit run dashboard/app.py
```

---

## 📝 What Happens Next

1. **Streamlit will start** and show:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Browser opens automatically** to the login page

3. **Login with:**
   - **Admin**: username `admin`, password `admin123`
   - **User**: username `user`, password `user123`

---

## 🔧 Troubleshooting

### Error: "streamlit: command not found"
**Solution:** Install streamlit or activate virtual environment
```bash
pip install streamlit
```

### Error: "Module not found"
**Solution:** Install all requirements
```bash
pip install -r requirements.txt
```

### Port 8501 already in use
**Solution:** Use different port
```bash
streamlit run dashboard/app.py --server.port 8502
```

---

## 🛑 Stop Dashboard

Press `Ctrl + C` in the terminal to stop the dashboard.
