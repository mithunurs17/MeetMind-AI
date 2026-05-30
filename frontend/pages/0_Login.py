"""
0_Login.py — Login & Registration page.
"""
import streamlit as st
from utils.auth import is_logged_in, login, register, current_user

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind AI — Authentication", 
    page_icon="🔐", 
    layout="wide"
)

# ── THEME & INTERFACE STYLING ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://googleapis.com');
:root {
    --bg: #0b0a12;
    --card-bg: #13121f;
    --border: #222035;
    --fg: #f5f5f7;
    --sub: #9897a9;
    --accent: #6366f1;
    --accent-gradient: linear-gradient(135deg, #4f46e5, #7c3aed);
}

/* Base resets & layout rules */
html, body, [class*="css"] {
    font-family: 'Geist Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--fg) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stApp { background-color: var(--bg) !important; }

/* Section Header Styling */
.section-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.section-title {
    font-size: 28px;
    font-weight: 700;
    color: var(--fg);
    margin: 0;
}
.section-subtitle {
    font-size: 14px;
    color: var(--sub);
    margin: 4px 0 0 0;
}

/* Custom Side Control Cards */
.control-panel {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.control-title {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--sub);
    margin-bottom: 16px;
}

/* Forms & Input Overrides */
[data-testid="stTextInput"] input {
    background: #1a1829 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--fg) !important;
    font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}
label {
    color: var(--sub) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* Uniform Dashboard Button Styling */
.stButton>button {
    width: 100% !important;
    background: var(--border) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    color: var(--fg) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.2rem !important;
    transition: all .2s ease !important;
}
.stButton>button:hover {
    background: #2c2944 !important;
    border-color: var(--accent) !important;
}

/* Primary Action Buttons */
div.action-btn button {
    background: var(--accent-gradient) !important;
    border: none !important;
    font-weight: 600 !important;
    color: #ffffff !important;
}
div.action-btn button:hover {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
}

/* Clean Info Blocks */
.info-card {
    background: rgba(99, 102, 241, 0.04);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    padding: 16px;
    font-size: 13px;
    color: var(--sub);
    line-height: 1.6;
}
.info-card b { color: #a5b4fc; }

ul { margin-left: 20px; padding-left: 0; color: var(--sub); font-size: 13px; }
li { margin-bottom: 6px; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── LOGGED IN CHECK ──────────────────────────────────────────────────────────
if is_logged_in():
    user = current_user()
    st.markdown(
        "<div class='section-header'><h1 class='section-title'>🧠 MeetMind AI Dashboard</h1></div>", 
        unsafe_allow_html=True
    )
    st.success(f"✅ Already signed in as **{user.get('username') if user else 'you'}**.")
    st.info("Use the application sidebar navigation layout to jump into your meeting analytics.")
    st.stop()

# ── TWO-COLUMN INTERFACE LAYOUT ────────────────────────────────────────────────
# Left: Navigation & Context Panels | Right: Operational Context Forms
left_col, right_col = st.columns([1.1, 2.0], gap="large")

with left_col:
    # App Identity Block
    st.markdown(
        "<div class='control-panel'>"
        "<div style='font-size:32px; margin-bottom:4px;'>🧠</div>"
        "<div style='font-size:20px; font-weight:700;'>MeetMind AI</div>"
        "<div style='font-size:13px; color:var(--sub);'>System Access Control</div>"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Mode Selector Panel
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='control-title'>Navigation Options</div>", unsafe_allow_html=True)
    
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"
        
    if st.button("🔐 Account Sign In", use_container_width=True):
        st.session_state.auth_tab = "login"
        st.rerun()
        
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if st.button("📝 Create New Account", use_container_width=True):
        st.session_state.auth_tab = "register"
        st.rerun()
        
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if st.button("🛡️ Administrative Info", use_container_width=True):
        st.session_state.auth_tab = "admin_info"
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    # Dynamic header zone based on selection state
    if st.session_state.auth_tab == "login":
        st.markdown(
            "<div class='section-header'>"
            "<h1 class='section-title'>Sign In</h1>"
            "<p class='section-subtitle'>Access your workspace sessions</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In →")
            st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Authenticating…"):
                    ok, err = login(username, password)
                if ok:
                    st.success("✅ Signed in! Use the sidebar to navigate.")
                    st.rerun()
                else:
                    st.error(f"Login failed: {err}")

    elif st.session_state.auth_tab == "register":
        st.markdown(
            "<div class='section-header'>"
            "<h1 class='section-title'>Register Account</h1>"
            "<p class='section-subtitle'>Set up your workspace credentials</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        with st.form("register_form", clear_on_submit=True):
            reg_email    = st.text_input("Email Address", placeholder="alice@example.com")
            reg_username = st.text_input("Username", placeholder="alice")
            reg_password = st.text_input("Password", type="password", placeholder="••••••••")
            reg_confirm  = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
            st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
            submitted_r  = st.form_submit_button("Create Account →")
            st.markdown("</div>", unsafe_allow_html=True)

        if submitted_r:
            if not all([reg_email, reg_username, reg_password, reg_confirm]):
                st.error("Please fill in all fields.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating your account…"):
                    ok, err = register(reg_email, reg_username, reg_password)
                if ok:
                    st.success("✅ Account created! You can now sign in.")
                    st.session_state.auth_tab = "login"
                    st.rerun()
                else:
                    st.error(f"Registration failed: {err}")

        st.markdown(
            "<div class='info-card' style='margin-top:16px; text-align:center;'>"
            "<b>Password Policy Requirements:</b> Min 8 characters · 1 uppercase · 1 lowercase · 1 digit"
            "</div>",
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            "<div class='section-header'>"
            "<h1 class='section-title'>Platform Governance</h1>"
            "<p class='section-subtitle'>Information regarding privileged workspace access</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div class="info-card">
                <p style="margin-top:0; font-size:15px; font-weight:600; color:#d8b4fe;">
                    🛡️ Administrator Privileges
                </p>
                <p>Administrative actions are restricted strictly to verified and authorized users.</p>
                <p><b>System capabilities assigned to administrative accounts include:</b></p>
                <ul>
                    <li>Manage active platform users and assign permission layers</li>
                    <li>Global audit visibility across all meeting datasets</li>
                    <li>Access low-level administration dashboards</li>
                    <li>Real-time telemetry and resource usage monitoring</li>
                    <li>Update root-level system configurations</li>
                </ul>
                <p><b>Security Measures:</b> All admin actions are logged with user and timestamp metadata. Multi-factor authentication is enforced for all admin accounts.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        