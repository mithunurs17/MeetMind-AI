"""
0_Login.py — Login & Registration page.

Numbered 0 so it appears first in the sidebar.
"""
import streamlit as st
from utils.auth import is_logged_in, login, register

st.set_page_config(page_title="MeetMind AI — Sign In", page_icon="🔐", layout="centered")

# ── If already authenticated, redirect to home ────────────────────────────
if is_logged_in():
    st.switch_page("app.py")

# ── Styles ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:      hsl(260, 87%, 3%);
  --fg:      hsl(40, 6%, 95%);
  --sub:     hsl(40, 6%, 72%);
  --accent:  #6366f1;
  --accent2: #a855f7;
  --error:   #f87171;
  --success: #86efac;
}

html, body, [class*="css"] {
  font-family: 'Geist Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--fg) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: var(--bg) !important; }

.auth-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 24px;
  padding: 40px 44px;
  max-width: 440px;
  margin: 60px auto 0;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

.auth-logo {
  text-align: center;
  font-size: 42px;
  margin-bottom: 4px;
}
.auth-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: var(--fg);
  margin-bottom: 4px;
}
.auth-sub {
  text-align: center;
  color: var(--sub);
  font-size: 14px;
  margin-bottom: 32px;
}

/* Tab pills */
.tab-row {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
  background: rgba(255,255,255,0.04);
  border-radius: 14px;
  padding: 4px;
}
.tab-btn {
  flex: 1;
  border: none;
  border-radius: 10px;
  padding: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Geist Sans', sans-serif;
  transition: all .2s;
}
.tab-active {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  box-shadow: 0 4px 12px rgba(99,102,241,0.35);
}
.tab-inactive {
  background: transparent;
  color: var(--sub);
}

/* Inputs */
[data-testid="stTextInput"] input {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--fg) !important;
  font-family: 'Geist Sans', sans-serif !important;
  font-size: 15px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

label {
  color: var(--sub) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
}

/* Submit button */
.stButton > button {
  width: 100% !important;
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  border: none !important;
  border-radius: 14px !important;
  color: #fff !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  padding: 0.8rem 1.5rem !important;
  font-family: 'Geist Sans', sans-serif !important;
  transition: all .2s !important;
  margin-top: 8px !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #6366f1, #a855f7) !important;
  transform: scale(1.02) !important;
  box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

[data-testid="stAlert"] {
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
}

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────
_, col, _ = st.columns([1, 2.2, 1])
with col:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<div class='auth-logo'>🧠</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-title'>MeetMind AI</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-sub'>AI-powered meeting intelligence</div>",
        unsafe_allow_html=True,
    )

    # Tab switcher
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    tab_col1, tab_col2 = st.columns(2)
    with tab_col1:
        login_cls = "tab-active" if st.session_state.auth_tab == "login" else "tab-inactive"
        if st.button("Sign In", key="tab_login", use_container_width=True):
            st.session_state.auth_tab = "login"
    with tab_col2:
        reg_cls = "tab-active" if st.session_state.auth_tab == "register" else "tab-inactive"
        if st.button("Register", key="tab_reg", use_container_width=True):
            st.session_state.auth_tab = "register"

    st.markdown("---")

    # ── Login form ────────────────────────────────────────────────────────
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
                    st.success("Welcome back! Redirecting…")
                    st.rerun()
                else:
                    st.error(f"Login failed: {err}")

    # ── Register form ─────────────────────────────────────────────────────
    else:
        with st.form("register_form", clear_on_submit=True):
            reg_email    = st.text_input("Email", placeholder="alice@example.com")
            reg_username = st.text_input("Username", placeholder="alice")
            reg_password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 chars, upper + lower + digit",
            )
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
                    st.success("Account created! You can now sign in.")
                    st.session_state.auth_tab = "login"
                    st.rerun()
                else:
                    st.error(f"Registration failed: {err}")

        st.markdown(
            "<p style='color:hsl(40,6%,55%);font-size:12px;margin-top:12px;text-align:center;'>"
            "Password must be at least 8 characters with one uppercase, one lowercase, and one digit."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)