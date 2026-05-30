"""
guards.py — Call require_auth() at the top of every protected page.

Usage:
    from utils.guards import require_auth
    require_auth()
"""
import streamlit as st
from utils.auth import is_logged_in, current_user, logout, is_admin


def require_auth() -> None:
    """Redirect to login if the user is not authenticated."""
    if not is_logged_in():
        st.warning("🔐 Please sign in to access this page.")
        st.page_link("pages/0_Login.py", label="Go to Sign In", icon="🔐")
        st.stop()


def render_user_badge() -> None:
    """Render a small user badge + logout button in the sidebar."""
    user = current_user()
    if user is None:
        return

    role_color = "#d8b4fe" if user.get("role") == "admin" else "#a5b4fc"
    st.sidebar.markdown(
        f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:14px;padding:14px 16px;margin-bottom:12px;">
          <div style="font-size:13px;font-weight:600;color:hsl(40,6%,95%);">
            👤 {user.get('username', 'User')}
          </div>
          <div style="font-size:11px;color:hsl(40,6%,62%);margin-top:2px;">
            {user.get('email','')}
          </div>
          <div style="margin-top:8px;">
            <span style="background:rgba(99,102,241,0.15);color:{role_color};
                         border:1px solid rgba(99,102,241,0.28);border-radius:999px;
                         padding:2px 10px;font-size:11px;font-weight:700;
                         text-transform:uppercase;">
              {user.get('role','user')}
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("🚪 Sign Out", use_container_width=True, key="_logout_btn"):
        logout()
        st.rerun()

    if is_admin():
        st.sidebar.markdown(
            "<p style='font-size:11px;color:hsl(40,6%,55%);text-align:center;'>"
            "Admin mode active</p>",
            unsafe_allow_html=True,
        )