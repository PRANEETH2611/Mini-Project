# ☁️ IBM Cloud Deployment Guide (Phase 8)

This guide covers how to deploy the AIOps Dashboard to **IBM Cloud Code Engine** from scratch on Windows.

## 1. Prerequisites (Install these first)

Since you don't have the IBM Cloud tools installed, run these commands in **PowerShell as Administrator**:

### Step A: Install IBM Cloud CLI
```powershell
# Download and install the CLI
iex(New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```
*After installation, close and reopen PowerShell.*

### Step B: Install Code Engine Plugin
```powershell
ibmcloud plugin install code-engine
```

---

## 2. Deployment Steps

Once the tools are ready, run these commands in your project folder (`D:\Downloads\AIOPS project`):

### Step 1: Login to IBM Cloud
```powershell
ibmcloud login --sso
# A browser window will open. Log in and copy the one-time code.
# Then select a region (e.g., us-south).
```

### Step 2: Create a Project
A "Project" is like a folder for your apps in the cloud.
```powershell
ibmcloud ce project create --name aiops-project
ibmcloud ce project select --name aiops-project
```

### Step 3: Deploy the App 🚀
This command uploads your code, builds the Docker image, and runs it.
```powershell
ibmcloud ce application create --name aiops-dashboard `
    --build-source . `
    --cpu 1 `
    --memory 2G `
    --port 8501 `
    --env GOOGLE_API_KEY=AIzaSyC6MI7Z9rG_8kTMgk12-1_FH6TlOLrqp6s
```
*(Note: We pass your API key as an environment variable so it works instantly)*

## 3. Access Your App
Once the deployment finishes (takes ~2-3 minutes), it will give you a public URL (e.g., `https://aiops-dashboard.xxxx.codeengine.appdomain.cloud`).

**Click that link, and your AIOps Command Center is live on the internet!** 🌍
