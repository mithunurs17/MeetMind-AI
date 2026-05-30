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
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:       hsl(260, 87%, 3%);
  --fg:       hsl(40, 6%, 95%);
  --sub:      hsl(40, 6%, 72%);
  --accent:   #6366f1;
  --accent2:  #a855f7;
}

html, body, [class*="css"] {
  font-family: 'Geist Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--fg) !important;
}

#MainMenu, footer, header { visibility: hidden; }

.stApp { background: var(--bg) !important; }

section[data-testid="stSidebar"] {
  background: hsl(260, 70%, 5%) !important;
  border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color: var(--fg) !important; }

/* Sidebar collapse / close button — override Streamlit's red/orange */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] > button,
button[kind="header"],
[data-testid="collapsedControl"] button {
  background: linear-gradient(135deg, #6d28d9, #a855f7) !important;
  border: none !important;
  border-radius: 50% !important;
  color: #fff !important;
  box-shadow: 0 4px 14px rgba(168,85,247,0.45) !important;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="collapsedControl"] button:hover {
  background: linear-gradient(135deg, #7c3aed, #c084fc) !important;
  box-shadow: 0 6px 20px rgba(168,85,247,0.55) !important;
  transform: scale(1.08) !important;
}
/* Also target via SVG icon color inside the button */
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="collapsedControl"] button svg {
  fill: #fff !important;
  color: #fff !important;
}

/* Sidebar nav links — purple, kill the orange active state */
[data-testid="stSidebarNavLink"] {
  border-radius: 12px !important;
  transition: background 0.2s ease !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: rgba(168,85,247,0.18) !important;
}
[data-testid="stSidebarNavLink"][aria-selected="true"],
[data-testid="stSidebarNavLink"]:focus {
  background: linear-gradient(135deg, #6d28d9, #a855f7) !important;
  box-shadow: 0 4px 18px rgba(168,85,247,0.32) !important;
}
/* Kill Streamlit's orange/red default highlight on active nav items */
[data-testid="stSidebarNavLink"][aria-selected="true"] span,
[data-testid="stSidebarNavLink"][aria-selected="true"] p {
  color: #fff !important;
}
/* Override the ::before colored bar Streamlit adds */
[data-testid="stSidebarNavLink"]::before {
  background: transparent !important;
  display: none !important;
}
/* Also target the inner li active highlight */
section[data-testid="stSidebar"] li[data-testid="stSidebarNavItems"] > ul > li > a {
  border-radius: 12px !important;
}
section[data-testid="stSidebar"] li[data-testid="stSidebarNavItems"] > ul > li > a[aria-selected="true"] {
  background: linear-gradient(135deg, #6d28d9, #a855f7) !important;
  color: #fff !important;
}
/* Nuke the orange active indicator stripe */
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"]::after,
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"]::before {
  display: none !important;
  background: transparent !important;
}

/* Page title */
h1 { color: var(--fg) !important; font-weight: 700 !important; }
h2, h3 { color: var(--fg) !important; font-weight: 600 !important; }

/* Glass form container */
[data-testid="stForm"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 20px !important;
  padding: 28px !important;
  backdrop-filter: blur(14px) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}

/* Inputs & textareas */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--fg) !important;
  font-family: 'Geist Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

/* Labels */
label, .stTextInput label, .stTextArea label, .stFileUploader label {
  color: var(--sub) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px dashed rgba(255,255,255,0.15) !important;
  border-radius: 14px !important;
  color: var(--fg) !important;
}

/* Browse files button — purple gradient */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button,
[data-testid="baseButton-secondary"] {
  background: linear-gradient(135deg, #6d28d9, #a855f7) !important;
  border: none !important;
  border-radius: 999px !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-family: 'Geist Sans', sans-serif !important;
  padding: 0.55rem 1.3rem !important;
  box-shadow: 0 4px 14px rgba(168,85,247,0.35) !important;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="baseButton-secondary"]:hover {
  background: linear-gradient(135deg, #7c3aed, #c084fc) !important;
  box-shadow: 0 6px 20px rgba(168,85,247,0.5) !important;
  transform: scale(1.03) !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 999px !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--fg) !important;
  font-weight: 500 !important;
  padding: 0.65rem 1.4rem !important;
  font-family: 'Geist Sans', sans-serif !important;
  transition: background 0.2s ease, transform 0.2s ease !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: rgba(99,102,241,0.22) !important;
  border-color: var(--accent) !important;
  transform: scale(1.02) !important;
}

/* Submit button — accent pill */
.stFormSubmitButton > button {
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  border: none !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  padding: 0.75rem 2rem !important;
}
.stFormSubmitButton > button:hover {
  background: linear-gradient(135deg, #6366f1, #a855f7) !important;
  transform: scale(1.03) !important;
}

/* Success / error / info banners */
[data-testid="stAlert"] {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  background: rgba(255,255,255,0.04) !important;
}

/* Metrics / result cards */
[data-testid="stMetricValue"] { color: var(--fg) !important; }

/* Horizontal divider */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Markdown helpers */
.glass-section {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
}
.tips-box {
  background: rgba(99,102,241,0.08);
  border: 1px solid rgba(99,102,241,0.22);
  border-radius: 14px;
  padding: 18px 22px;
  margin-top: 24px;
}
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
