"""
guards.py — Sidebar user badge and page auth guard.
"""
import streamlit as st
from utils.auth import is_logged_in, current_user, logout, is_admin


def require_auth() -> None:
    if not is_logged_in():
        st.warning("🔐 Please sign in to access this page.")
        st.markdown(
            "<a href='/' target='_self' style='color:#a5b4fc;'>← Go to Sign In</a>",
            unsafe_allow_html=True,
        )
        st.stop()


def render_user_badge() -> None:
    user = current_user()
    if user is None:
        return

    role        = (user.get("role") or "user").lower()
    is_adm      = role == "admin"
    role_color  = "#d8b4fe" if is_adm else "#a5b4fc"
    role_bg     = "rgba(168,85,247,0.15)" if is_adm else "rgba(99,102,241,0.12)"
    role_border = "rgba(168,85,247,0.30)" if is_adm else "rgba(99,102,241,0.28)"
    role_label  = role.upper()
    username    = user.get("username") or "User"
    email       = user.get("email") or ""
    initial     = username[0].upper()

    # Injected into the MAIN document (not just sidebar) so it has global reach.
    # This neutralises the .block-container styling that other pages apply to
    # the sidebar and that causes the card to look boxed/padded differently.
    st.markdown(
        """
        <style>
        /* ── Neutralise page-level block-container overrides inside sidebar ── */
        section[data-testid="stSidebar"] .block-container {
            padding       : 0 !important;
            background    : transparent !important;
            border        : none !important;
            border-radius : 0 !important;
            box-shadow    : none !important;
            max-width     : 100% !important;
        }

        /* ── Consistent sidebar inner padding on every page ── */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top   : 1rem !important;
            padding-left  : 0.75rem !important;
            padding-right : 0.75rem !important;
        }

        /* ── Badge card ── */
        .mm-card {
            background    : rgba(255,255,255,0.04);
            border        : 1px solid rgba(255,255,255,0.09);
            border-radius : 16px;
            padding       : 14px;
            margin-bottom : 8px;
            box-sizing    : border-box;
        }
        .mm-top-row {
            display       : flex;
            align-items   : center;
            gap           : 10px;
            margin-bottom : 10px;
        }
        .mm-avatar {
            width           : 36px;
            height          : 36px;
            min-width       : 36px;
            border-radius   : 50%;
            background      : linear-gradient(135deg, #4f46e5, #7c3aed);
            display         : flex;
            align-items     : center;
            justify-content : center;
            font-size       : 15px;
            font-weight     : 700;
            color           : #fff;
        }
        .mm-info {
            flex      : 1;
            min-width : 0;
            overflow  : hidden;
        }
        .mm-name {
            font-size     : 14px;
            font-weight   : 600;
            color         : hsl(40, 6%, 95%);
            white-space   : nowrap;
            overflow      : hidden;
            text-overflow : ellipsis;
        }
        .mm-email {
            font-size     : 12px;
            color         : hsl(40, 6%, 60%);
            white-space   : nowrap;
            overflow      : hidden;
            text-overflow : ellipsis;
            margin-top    : 2px;
        }

        /* ── Sign Out button — override every page's button rules ── */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
        section[data-testid="stSidebar"] .stButton > button {
            background    : rgba(255,255,255,0.04) !important;
            border        : 1px solid rgba(255,255,255,0.12) !important;
            border-radius : 12px !important;
            color         : hsl(40, 6%, 82%) !important;
            font-size     : 14px !important;
            font-weight   : 500 !important;
            width         : 100% !important;
            padding       : 10px 0 !important;
            margin        : 0 !important;
            box-shadow    : none !important;
            transform     : none !important;
            transition    : background 0.18s, border-color 0.18s, color 0.18s !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
        section[data-testid="stSidebar"] .stButton > button:hover {
            background   : rgba(239, 68, 68, 0.10) !important;
            border-color : rgba(239, 68, 68, 0.32) !important;
            color        : #fca5a5 !important;
            transform    : none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Badge card HTML (injected via sidebar) ────────────────────────────
    st.sidebar.markdown(
        f"""
        <style>
        .mm-role-pill {{
            display        : inline-block;
            background     : {role_bg};
            color          : {role_color};
            border         : 1px solid {role_border};
            border-radius  : 999px;
            padding        : 3px 11px;
            font-size      : 10px;
            font-weight    : 700;
            letter-spacing : 0.06em;
            text-transform : uppercase;
        }}
        </style>

        <div class="mm-card">
            <div class="mm-top-row">
                <div class="mm-avatar">{initial}</div>
                <div class="mm-info">
                    <div class="mm-name">{username}</div>
                    <div class="mm-email">{email}</div>
                </div>
            </div>
            <div class="mm-role-pill">{role_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sign Out button ───────────────────────────────────────────────────
    if st.sidebar.button("Sign Out", use_container_width=True, key="_logout_btn"):
        logout()
        st.rerun()

    if is_adm:
        st.sidebar.markdown(
            "<p style='font-size:11px;color:hsl(40,6%,44%);text-align:center;"
            "margin-top:6px;letter-spacing:0.04em;'>Admin mode active</p>",
            unsafe_allow_html=True,
        )