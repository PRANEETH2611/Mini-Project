"""
Main Dashboard App - Streamlit Version (CSV-based, No MongoDB)
Routes users to appropriate dashboard based on role
"""
import os
import sys
import time
import streamlit as st

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AIOps Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "final_decision_output.csv")

# -----------------------------
# SIMPLE LOGIN DATABASE (in-memory)
# -----------------------------
USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "user": {"password": "user123", "role": "USER"}
}

# -----------------------------
# CSS STYLING
# -----------------------------
st.markdown("""
<style>
    .login-container {
        max-width: 500px;
        margin: 5rem auto;
        padding: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        color: white;
    }
    
    .login-container h1 {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .error-message {
        color: #ff6b6b;
        margin-top: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN PAGE
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="login-container">
        <h1>🔐 AIOps Portal Login</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="admin / user")
            password = st.text_input("🔒 Password", type="password", placeholder="admin123 / user123")
            
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                # Normalize inputs
                username_clean = username.strip().lower()
                password_clean = password.strip()
                
                user = USERS.get(username_clean)
                if user and user["password"] == password_clean:
                    st.session_state.user = {"username": username_clean, "role": user["role"]}
                    st.success(f"✅ Login successful! Welcome {username_clean}")
                    time.sleep(0.5) # Reduced delay for faster transition
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("""
        **Demo Credentials:**
        
        👨‍💼 **ADMIN** → username: `admin`, password: `admin123`
        
        👤 **USER** → username: `user`, password: `user123`
        """)

# -----------------------------
# ROUTE TO APPROPRIATE DASHBOARD
# -----------------------------
if st.session_state.user is None:
    login_page()
else:
    user_role = st.session_state.user.get("role")
    
    # Route to appropriate dashboard based on role
    if user_role == "ADMIN":
        # Import and run admin dashboard
        from dashboard import admin_dashboard
        admin_dashboard.main()
    else:
        # Import and run user dashboard using direct import for performance
        # We use a trick to import from the current directory
        # Since we are in the same directory, we can import directly
        from dashboard import user_dashboard
        user_dashboard.main()
