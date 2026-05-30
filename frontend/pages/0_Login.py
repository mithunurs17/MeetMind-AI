"""
0_Login.py — Login & Registration page.
"""
import streamlit as st
from utils.auth import is_logged_in, login, register, current_user

st.set_page_config(page_title="MeetMind AI — Sign In", page_icon="🔐", layout="centered")

if is_logged_in():
    user = current_user()
    st.success(f"✅ Already signed in as **{user.get('username') if user else 'you'}**.")
    st.markdown("<p style='color:hsl(40,6%,72%);'>Use the sidebar to navigate to any page.</p>", unsafe_allow_html=True)
    st.stop()

st.markdown("""
<style>
@import url('https://googleapis.com');
:root{--bg:hsl(260,87%,3%);--fg:hsl(40,6%,95%);--sub:hsl(40,6%,72%);--accent:#6366f1}
html,body,[class*="css"]{font-family:'Geist Sans',sans-serif!important;background:var(--bg)!important;color:var(--fg)!important}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:var(--bg)!important}
.auth-card{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:24px;padding:40px 44px;max-width:460px;margin:40px auto 0;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.auth-logo{text-align:center;font-size:42px;margin-bottom:4px}
.auth-title{text-align:center;font-size:24px;font-weight:700;color:var(--fg);margin-bottom:4px}
.auth-sub{text-align:center;color:var(--sub);font-size:14px;margin-bottom:28px}
.info-box{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);border-radius:14px;padding:16px 20px;margin-bottom:20px;font-size:13px;color:hsl(40,6%,80%);line-height:1.7}
.info-box b{color:#a5b4fc}
.admin-box{background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.25);border-radius:14px;padding:16px 20px;margin-bottom:20px;font-size:13px;color:hsl(40,6%,80%);line-height:1.7}
.admin-box b{color:#d8b4fe}
[data-testid="stTextInput"] input{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;color:var(--fg)!important;font-family:'Geist Sans',sans-serif!important;font-size:15px!important}
[data-testid="stTextInput"] input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(99,102,241,0.18)!important}
label{color:var(--sub)!important;font-size:12px!important;font-weight:500!important;letter-spacing:.06em!important;text-transform:uppercase!important}
.stButton>button{width:100%!important;background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;border:none!important;border-radius:14px!important;color:#fff!important;font-size:15px!important;font-weight:600!important;padding:0.8rem 1.5rem!important;font-family:'Geist Sans',sans-serif!important;transition:all .2s!important;margin-top:8px!important}
.stButton>button:hover{background:linear-gradient(135deg,#6366f1,#a855f7)!important;transform:scale(1.02)!important}
[data-testid="stAlert"]{border-radius:12px!important;border:1px solid rgba(255,255,255,0.08)!important}
hr{border-color:rgba(255,255,255,0.08)!important}
</style>
""", unsafe_allow_html=True)

_, col, _ = st.columns([1, 2.4, 1])
with col:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<div class='auth-logo'>🧠</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-title'>MeetMind AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-sub'>AI-powered meeting intelligence</div>", unsafe_allow_html=True)

    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    tab_col1, tab_col2, tab_col3 = st.columns(3)
    with tab_col1:
        if st.button("Sign In", key="tab_login", use_container_width=True):
            st.session_state.auth_tab = "login"
            st.rerun()
    with tab_col2:
        if st.button("Register", key="tab_reg", use_container_width=True):
            st.session_state.auth_tab = "register"
            st.rerun()
    with tab_col3:
        if st.button("ℹ️ Admin Info", key="tab_admin", use_container_width=True):
            st.session_state.auth_tab = "admin_info"
            st.rerun()

    st.markdown("---")

    # ── LOGIN ──────────────────────────────────────────────────────────────
    if st.session_state.auth_tab == "login":
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →")

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

    # ── REGISTER ────────────────────────────────────────────────────────────
    elif st.session_state.auth_tab == "register":
        with st.form("register_form", clear_on_submit=True):
            reg_email    = st.text_input("Email", placeholder="alice@example.com")
            reg_username = st.text_input("Username", placeholder="alice")
            reg_password = st.text_input("Password", type="password", placeholder="Min 8 chars, upper + lower + digit")
            reg_confirm  = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            submitted_r  = st.form_submit_button("Create Account →")

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
            "<p style='color:hsl(40,6%,55%);font-size:12px;margin-top:12px;text-align:center;'>"
            "Password: min 8 chars · one uppercase · one lowercase · one digit"
            "</p>",
            unsafe_allow_html=True,
        )

    # ── ADMIN INFO ──────────────────────────────────────────────────────────
    else:
        st.markdown(
            """
            <div class="admin-box">
                <h4 style="margin-top:0;color:#d8b4fe;">
                    🛡️ Administrator Access
                </h4>
                <p>
                    Administrative features are restricted to authorized users.
                </p>
                <p><b>Administrator capabilities include:</b></p>
                <ul style="margin-left:20px;">
                    <li>Manage users and permissions</li>
                    <li>View and manage all meetings</li>
                    <li>Access administrative controls</li>
                    <li>Monitor platform activity</li>
                    <li>Configure system settings</li>
                </ul>
                <p>
                    <b>Need administrator access?</b><br>
                    Contact your organization administrator to request elevated privileges.
                </p>
                <p style="color:#a5b4fc;font-size:13px;">
                    For security reasons, administrator credentials and internal
                    configuration details are not displayed on this page.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
      
    st.markdown("</div>", unsafe_allow_html=True)
