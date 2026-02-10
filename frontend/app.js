// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Application State
let currentUser = null;
let refreshInterval = null;
let currentData = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus();
    setupEventListeners();
    loadFilterOptions();
});

// Check if user is logged in
function checkLoginStatus() {
    const savedUser = localStorage.getItem('aiops_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showDashboard();
        loadDashboardData();
    } else {
        showLogin();
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Login Form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // Filters
    document.getElementById('alertFilter').addEventListener('change', onFilterChange);
    document.getElementById('rootFilter').addEventListener('change', onFilterChange);
    document.getElementById('windowSlider').addEventListener('input', onFilterChange);
    document.getElementById('startDate').addEventListener('change', onFilterChange);
    document.getElementById('endDate').addEventListener('change', onFilterChange);
    
    // Auto Refresh
    document.getElementById('autoRefresh').addEventListener('change', toggleAutoRefresh);
    document.getElementById('refreshSeconds').addEventListener('input', updateRefreshInterval);
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });
    
    // Login History Refresh
    const refreshBtn = document.getElementById('refreshLogins');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadLoginHistory);
    }
}

// Login Handler
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data;
            localStorage.setItem('aiops_user', JSON.stringify(data));
            showDashboard();
            loadDashboardData();
        } else {
            errorDiv.textContent = data.message || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error. Make sure backend is running.';
    }
}

// Logout Handler
function handleLogout() {
    currentUser = null;
    localStorage.removeItem('aiops_user');
    if (refreshInterval) clearInterval(refreshInterval);
    showLogin();
}

// Show/Hide Views
function showLogin() {
    document.getElementById('loginModal').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('loginModal').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('userDisplay').textContent = `👤 ${currentUser.username} (${currentUser.role})`;
    
    // Show login history tab for admin
    if (currentUser.role === 'ADMIN') {
        document.getElementById('loginHistoryTab').style.display = 'block';
    } else {
        document.getElementById('loginHistoryTab').style.display = 'none';
    }
}

// Load Filter Options
async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/options`);
        const data = await response.json();
        
        if (data.success) {
            const rootSelect = document.getElementById('rootFilter');
            rootSelect.innerHTML = '<option value="ALL">ALL</option>';
            data.root_causes.forEach(rc => {
                const option = document.createElement('option');
                option.value = rc;
                option.textContent = rc;
                rootSelect.appendChild(option);
            });
            
            document.getElementById('startDate').value = data.date_range.min;
            document.getElementById('endDate').value = data.date_range.max;
        }
    } catch (error) {
        console.error('Error loading options:', error);
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        const params = new URLSearchParams({
            alert_status: document.getElementById('alertFilter').value,
            root_cause: document.getElementById('rootFilter').value,
            window: document.getElementById('windowSlider').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value
        });
        
        const response = await fetch(`${API_BASE_URL}/data?${params}`);
        const result = await response.json();
        
        if (result.success) {
            currentData = result;
            updateKPIs(result.latest);
            updateSummary(result.statistics);
            updateIncidentStatus(result.latest);
            updateCharts(result.data);
            loadAnalytics();
            loadInsights();
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update KPIs
function updateKPIs(latest) {
    document.getElementById('kpiCpu').textContent = `${latest.cpu_usage.toFixed(1)}%`;
    document.getElementById('kpiMemory').textContent = `${latest.memory_usage.toFixed(2)} GB`;
    document.getElementById('kpiResponse').textContent = `${latest.response_time.toFixed(0)} ms`;
    
    const failureProb = latest.failure_probability;
    const failureEl = document.getElementById('kpiFailure');
    failureEl.textContent = `${(failureProb * 100).toFixed(1)}%`;
    failureEl.style.color = failureProb > 0.5 ? '#d62728' : failureProb > 0.2 ? '#ffbb33' : '#2ca02c';
    
    const anomaly = latest.anomaly_label === 1 ? 'YES' : 'NO';
    const anomalyEl = document.getElementById('kpiAnomaly');
    anomalyEl.textContent = anomaly;
    anomalyEl.style.color = anomaly === 'YES' ? '#d62728' : '#2ca02c';
    
    const alertEl = document.getElementById('kpiAlert');
    alertEl.textContent = latest.alert_status;
    alertEl.style.color = latest.alert_status === 'ALERT' ? '#d62728' : '#2ca02c';
}

// Update Summary
function updateSummary(stats) {
    document.getElementById('summaryAlerts').textContent = stats.alerts_count;
    document.getElementById('summaryOK').textContent = stats.ok_count;
    document.getElementById('summaryAnomalies').textContent = stats.anomalies_count;
    
    const topRC = Object.keys(stats.root_causes)[0] || '--';
    document.getElementById('summaryRootCause').textContent = topRC.substring(0, 20);
}

// Update Incident Status
function updateIncidentStatus(latest) {
    const incidentCard = document.getElementById('incidentCard');
    const incidentContent = document.getElementById('incidentContent');
    const resolutionStatus = latest.resolution_status || 'MONITORING';
    const resolutionAlert = (latest.resolution_alert || '').trim();

    if (resolutionStatus === 'MANUAL_INTERVENTION_REQUIRED') {
        incidentCard.style.background = 'linear-gradient(135deg, #b91c1c 0%, #ef4444 100%)';
        incidentContent.innerHTML = `
            <h3>🚨 ESCALATION REQUIRED</h3>
            <p><b>Root Cause:</b> ${latest.predicted_root_cause}</p>
            <p><b>Resolution Alert:</b> ${resolutionAlert || 'Auto-remediation unavailable'}</p>
            <p><b>Timestamp:</b> ${new Date(latest.timestamp).toLocaleString()}</p>
        `;
    } else if (latest.alert_status === 'ALERT') {
        incidentCard.style.background = 'linear-gradient(135deg, #d62728 0%, #ff6b6b 100%)';
        incidentContent.innerHTML = `
            <h3>⚠️ ALERT: High Incident Risk</h3>
            <p><b>Root Cause:</b> ${latest.predicted_root_cause}</p>
            <p><b>Auto Resolution:</b> ${latest.auto_resolution || latest.recommended_action}</p>
            <p><b>Status:</b> ${resolutionStatus}</p>
            <p><b>Timestamp:</b> ${new Date(latest.timestamp).toLocaleString()}</p>
        `;
    } else {
        incidentCard.style.background = 'linear-gradient(135deg, #2ca02c 0%, #51cf66 100%)';
        incidentContent.innerHTML = `
            <h3>✅ System Stable</h3>
            <p>No critical incident predicted</p>
            <p><b>Timestamp:</b> ${new Date(latest.timestamp).toLocaleString()}</p>
        `;
    }

    document.getElementById('detailsContent').innerHTML = `
        <p><b>Timestamp:</b> ${new Date(latest.timestamp).toLocaleString()}</p>
        <p><b>Anomaly:</b> ${latest.anomaly_label === 1 ? 'YES' : 'NO'}</p>
        <p><b>Anomaly Score:</b> ${latest.anomaly_score || 'NA'}</p>
        <p><b>Predicted Failure:</b> ${latest.predicted_failure === 1 ? 'YES' : 'NO'}</p>
        <p><b>Failure Probability:</b> ${(latest.failure_probability * 100).toFixed(2)}%</p>
        <p><b>Root Cause:</b> ${latest.predicted_root_cause}</p>
        <p><b>Action:</b> ${latest.recommended_action}</p>
        <p><b>Auto Resolution:</b> ${latest.auto_resolution || 'N/A'}</p>
        <p><b>Resolution Status:</b> ${resolutionStatus}</p>
        ${resolutionAlert ? `<p style="color:#ef4444;"><b>Resolution Alert:</b> ${resolutionAlert}</p>` : ''}
    `;
}

// Update Charts
function updateCharts(data) {
    if (!data || data.length === 0) return;
    
    const timestamps = data.map(d => d.timestamp);
    
    // CPU Chart
    Plotly.newPlot('cpuChart', [{
        x: timestamps,
        y: data.map(d => d.cpu_usage),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'CPU Usage',
        line: { color: '#667eea', width: 2 }
    }], {
        title: 'CPU Usage Trend',
        template: 'plotly_dark',
        height: 400
    });
    
    // Memory Chart
    Plotly.newPlot('memoryChart', [{
        x: timestamps,
        y: data.map(d => d.memory_usage),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Memory Usage',
        line: { color: '#f093fb', width: 2 }
    }], {
        title: 'Memory Usage Trend',
        template: 'plotly_dark',
        height: 400
    });
    
    // Response Chart
    Plotly.newPlot('responseChart', [{
        x: timestamps,
        y: data.map(d => d.response_time),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Response Time',
        line: { color: '#4facfe', width: 2 }
    }], {
        title: 'Response Time Trend',
        template: 'plotly_dark',
        height: 400
    });
    
    // Failure Probability Chart
    Plotly.newPlot('failureChart', [{
        x: timestamps,
        y: data.map(d => d.failure_probability),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Failure Probability',
        line: { color: '#ff6b6b', width: 2 }
    }], {
        title: 'Failure Probability Trend',
        template: 'plotly_dark',
        height: 400
    });
    
    // Multi-metric Chart
    Plotly.newPlot('multiMetricChart', [
        { x: timestamps, y: data.map(d => d.cpu_usage), name: 'CPU', type: 'scatter', line: { color: '#667eea' } },
        { x: timestamps, y: data.map(d => d.memory_usage), name: 'Memory', type: 'scatter', line: { color: '#f093fb' } },
        { x: timestamps, y: data.map(d => d.response_time), name: 'Response', type: 'scatter', line: { color: '#4facfe' } },
        { x: timestamps, y: data.map(d => d.failure_probability), name: 'Failure Prob', type: 'scatter', line: { color: '#ff6b6b' } }
    ], {
        title: 'Multi-Metric Overview',
        template: 'plotly_dark',
        height: 500
    });
}

// Load Analytics
async function loadAnalytics() {
    try {
        const params = new URLSearchParams({
            window: document.getElementById('windowSlider').value
        });
        
        const response = await fetch(`${API_BASE_URL}/analytics?${params}`);
        const result = await response.json();
        
        if (result.success) {
            // Root Cause Bar Chart
            Plotly.newPlot('rootCauseChart', [{
                x: Object.keys(result.root_causes),
                y: Object.values(result.root_causes),
                type: 'bar',
                marker: { color: '#667eea' }
            }], {
                title: 'Root Cause Distribution',
                template: 'plotly_dark',
                height: 400
            });
            
            // Root Cause Pie Chart
            Plotly.newPlot('rootCausePieChart', [{
                labels: Object.keys(result.root_causes),
                values: Object.values(result.root_causes),
                type: 'pie',
                hole: 0.4
            }], {
                title: 'Root Cause Share',
                template: 'plotly_dark',
                height: 400
            });
            
            // Alert Status Pie Chart
            Plotly.newPlot('alertStatusChart', [{
                labels: Object.keys(result.alert_status),
                values: Object.values(result.alert_status),
                type: 'pie',
                hole: 0.4
            }], {
                title: 'Alert Status Distribution',
                template: 'plotly_dark',
                height: 400
            });
            
            // Correlation Heatmap
            const metrics = ['cpu_usage', 'memory_usage', 'response_time', 'failure_probability'];
            const z = metrics.map(m => metrics.map(n => result.correlation[m][n]));
            
            Plotly.newPlot('correlationChart', [{
                z: z,
                x: metrics,
                y: metrics,
                type: 'heatmap',
                colorscale: 'Viridis'
            }], {
                title: 'Metrics Correlation',
                template: 'plotly_dark',
                height: 400
            });
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Load Insights
async function loadInsights() {
    try {
        const params = new URLSearchParams({
            window: document.getElementById('windowSlider').value
        });
        
        const response = await fetch(`${API_BASE_URL}/insights?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const insights = result.insights;
            
            document.getElementById('keyInsights').innerHTML = `
                <p>✅ <b>System Health:</b> ${(100 - insights.alert_rate).toFixed(1)}% OK</p>
                <p>⚠️ <b>Alert Rate:</b> ${insights.alert_rate.toFixed(1)}%</p>
                <p>📊 <b>Anomaly Detection:</b> ${insights.anomaly_rate.toFixed(1)}%</p>
                <p>🔴 <b>Risk Level:</b> ${insights.avg_failure_prob > 0.5 ? 'High' : insights.avg_failure_prob > 0.2 ? 'Medium' : 'Low'}</p>
            `;
            
            document.getElementById('performanceMetrics').innerHTML = `
                <p><b>Average CPU:</b> ${insights.avg_cpu.toFixed(1)}%</p>
                <p><b>Average Memory:</b> ${insights.avg_memory.toFixed(2)} GB</p>
                <p><b>Average Response:</b> ${insights.avg_response.toFixed(0)} ms</p>
                <p><b>Avg Failure Prob:</b> ${(insights.avg_failure_prob * 100).toFixed(2)}%</p>
            `;
            
            // Hourly Trends Chart
            Plotly.newPlot('hourlyTrendChart', [
                {
                    x: insights.hourly_trends.map(h => h.hour),
                    y: insights.hourly_trends.map(h => h.cpu_usage),
                    name: 'Avg CPU %',
                    type: 'scatter',
                    line: { color: '#667eea', width: 2 }
                },
                {
                    x: insights.hourly_trends.map(h => h.hour),
                    y: insights.hourly_trends.map(h => h.alert_status * 10),
                    name: 'Alerts (x10)',
                    type: 'scatter',
                    line: { color: '#d62728', width: 2 }
                }
            ], {
                title: 'Hourly Trends',
                template: 'plotly_dark',
                height: 400
            });
        }
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Filter Change Handler
function onFilterChange() {
    document.getElementById('windowValue').textContent = 
        `${document.getElementById('windowSlider').value} records`;
    loadDashboardData();
}

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabButton) {
        tabButton.classList.add('active');
    }
    
    // Handle tab name with hyphens
    const tabId = tabName.replace(/-/g, '-') + 'Tab';
    const tabContent = document.getElementById(tabId);
    if (!tabContent) {
        // Try alternative format
        const altTabId = tabName + 'Tab';
        const altTabContent = document.getElementById(altTabId);
        if (altTabContent) {
            altTabContent.classList.add('active');
        }
    } else {
        tabContent.classList.add('active');
    }
    
    if (tabName === 'analytics') {
        loadAnalytics();
    } else if (tabName === 'insights') {
        loadInsights();
    } else if (tabName === 'login-history') {
        loadLoginHistory();
    }
}

// Auto Refresh
function toggleAutoRefresh() {
    const enabled = document.getElementById('autoRefresh').checked;
    document.getElementById('refreshInterval').classList.toggle('hidden', !enabled);
    
    if (enabled) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
}

function startAutoRefresh() {
    const seconds = parseInt(document.getElementById('refreshSeconds').value);
    refreshInterval = setInterval(loadDashboardData, seconds * 1000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function updateRefreshInterval() {
    const seconds = parseInt(document.getElementById('refreshSeconds').value);
    document.getElementById('refreshValue').textContent = `${seconds}s`;
    if (refreshInterval) {
        stopAutoRefresh();
        startAutoRefresh();
    }
}

// Load Login History (Admin Only)
async function loadLoginHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/login-history?limit=20`);
        const result = await response.json();
        
        if (result.success && result.logins.length > 0) {
            let html = '<table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">';
            html += '<thead><tr style="background: rgba(255,255,255,0.1);">';
            html += '<th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.2);">Username</th>';
            html += '<th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.2);">Role</th>';
            html += '<th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.2);">Login Time</th>';
            html += '<th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid rgba(255,255,255,0.2);">IP Address</th>';
            html += '</tr></thead><tbody>';
            
            result.logins.forEach(login => {
                const loginTime = new Date(login.timestamp).toLocaleString();
                html += `<tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">`;
                html += `<td style="padding: 0.75rem;">${login.username}</td>`;
                html += `<td style="padding: 0.75rem;">${login.role || 'N/A'}</td>`;
                html += `<td style="padding: 0.75rem;">${loginTime}</td>`;
                html += `<td style="padding: 0.75rem;">${login.ip_address || 'N/A'}</td>`;
                html += `</tr>`;
            });
            
            html += '</tbody></table>';
            document.getElementById('loginHistoryContent').innerHTML = html;
        } else {
            document.getElementById('loginHistoryContent').innerHTML = 
                '<p style="color: #b0b0b0;">No login history available. MongoDB may not be connected.</p>';
        }
    } catch (error) {
        console.error('Error loading login history:', error);
        document.getElementById('loginHistoryContent').innerHTML = 
            '<p style="color: #d62728;">Error loading login history. Make sure backend is running and MongoDB is connected.</p>';
    }
}

// Setup refresh button for login history
document.addEventListener('DOMContentLoaded', () => {
    // This will run after initial setup
    setTimeout(() => {
        const refreshBtn = document.getElementById('refreshLogins');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', loadLoginHistory);
        }
    }, 1000);
});
