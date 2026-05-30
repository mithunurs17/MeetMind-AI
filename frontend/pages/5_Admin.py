"""
5_Admin.py — User management page (admin only).

What admins can do here:
  • View all registered users
  • Promote a regular user to admin (or demote)
  • Deactivate / reactivate accounts
  • Delete users
"""
import streamlit as st
from utils.api_client import api_client
from utils.auth import current_user, is_admin, is_logged_in

st.set_page_config(page_title="Admin — Users", page_icon="🛡️", layout="wide")

try:
    from utils.guards import render_user_badge
    render_user_badge()
except Exception:
    pass

# ── Auth guards ───────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("🔐 Please sign in. Use the sidebar to navigate to Sign In.")
    st.stop()

user = current_user()
if user is None:
    try:
        from utils.auth import _load_profile
        _load_profile()
        user = current_user()
    except Exception:
        pass

if not is_admin():
    st.error("🚫 Admin access required.")
    if user:
        st.info(
            f"You are signed in as **{user.get('username')}** (role: **{user.get('role')}**). "
            "Ask an existing admin to promote your account, or sign in as the default admin "
            "(`admin` / `Admin@12345!`)."
        )
    st.stop()

# ── Styles ────────────────────────────────────────────────────────────────
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

# ── Admin capabilities info box ───────────────────────────────────────────
st.markdown(
    "<div class='info-box'>"
    "<b>What you can do as admin:</b><br/>"
    "• <b>Promote to admin</b> — change a user's role to <code>admin</code> so they can access this panel<br/>"
    "• <b>Demote to user</b> — change an admin back to a regular user<br/>"
    "• <b>Deactivate/reactivate</b> — toggle the Active checkbox to block or restore login<br/>"
    "• <b>Delete</b> — permanently remove a user and all their meetings<br/>"
    "• <b>View all meetings</b> — admins see every user's meetings on the Dashboard page"
    "</div>",
    unsafe_allow_html=True,
)

# ── Fetch users ───────────────────────────────────────────────────────────
users_resp = api_client.get_users()
if isinstance(users_resp, dict) and "error" in users_resp:
    st.error(f"Failed to load users: {users_resp['error']}")
    st.stop()

users = users_resp if isinstance(users_resp, list) else []
me = current_user() or {}

# ── Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Users", len(users))
c2.metric("Admins", sum(1 for u in users if u.get("role") == "admin"))
c3.metric("Active", sum(1 for u in users if u.get("is_active")))
c4.metric("Inactive", sum(1 for u in users if not u.get("is_active")))

st.markdown("---")

# ── Quick promote panel ───────────────────────────────────────────────────
st.markdown("## ⚡ Quick Promote to Admin")
st.markdown(
    "<div class='promote-box'>"
    "Select a regular user below and click <b>Promote to Admin</b> to give them full admin access. "
    "They will be able to manage all users and view all meetings.<br/>"
    "<span style='color:#f87171;font-size:12px;'>⚠️ Only promote trusted users — admins can delete accounts and data.</span>"
    "</div>",
    unsafe_allow_html=True,
)

regular_users = [u for u in users if u.get("role") == "user" and u["id"] != me.get("id")]
if regular_users:
    promote_options = {f"{u['username']} ({u['email']})": u for u in regular_users}
    pcol1, pcol2 = st.columns([3, 1])
    with pcol1:
        selected_promote = st.selectbox(
            "Select user to promote",
            list(promote_options.keys()),
            key="promote_select",
        )
    with pcol2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🛡️ Promote to Admin", key="do_promote"):
            target = promote_options[selected_promote]
            result = api_client.update_user(target["id"], {"role": "admin"})
            if isinstance(result, dict) and "error" in result:
                st.error(f"Failed: {result['error']}")
            else:
                st.success(f"✅ {target['username']} is now an admin!")
                st.rerun()
else:
    st.info("No regular users to promote — all users are already admins.")

st.markdown("---")

# ── Full user list ────────────────────────────────────────────────────────
st.markdown("## 👥 All Users")

for u in users:
    role_badge = (
        "<span class='role-admin'>admin</span>"
        if u.get("role") == "admin"
        else "<span class='role-user'>user</span>"
    )
    active_status = (
        "<span class='active-dot'></span>Active"
        if u.get("is_active")
        else "<span class='inactive-dot'></span>Inactive"
    )
    is_self = u["id"] == me.get("id")
    self_label = " (you)" if is_self else ""

    with st.expander(f"#{u['id']} — {u['username']}{self_label}  ·  {u['email']}"):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                f"**Role:** {role_badge} &nbsp;&nbsp; **Status:** {active_status}",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Joined:** {u.get('created_at', 'N/A')}")
            if is_self:
                st.markdown(
                    "<span style='color:#fcd34d;font-size:12px;'>⚠️ You cannot modify your own account here.</span>",
                    unsafe_allow_html=True,
                )

        with col2:
            new_role = st.selectbox(
                "Role",
                ["user", "admin"],
                index=0 if u.get("role") == "user" else 1,
                key=f"role_{u['id']}",
                disabled=is_self,
                help="Change to 'admin' to grant full access, 'user' to demote.",
            )
            new_active = st.checkbox(
                "Active",
                value=u.get("is_active", True),
                key=f"active_{u['id']}",
                disabled=is_self,
                help="Uncheck to prevent this user from logging in.",
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("💾 Save", key=f"save_{u['id']}", disabled=is_self):
                    result = api_client.update_user(
                        u["id"], {"role": new_role, "is_active": new_active}
                    )
                    if isinstance(result, dict) and "error" in result:
                        st.error(result["error"])
                    else:
                        action = "promoted to admin" if new_role == "admin" else "updated"
                        st.success(f"✅ {u['username']} {action}!")
                        st.rerun()

            with btn_col2:
                if not is_self:
                    if st.button("🗑️ Delete", key=f"del_{u['id']}", type="secondary"):
                        result = api_client.delete_user(u["id"])
                        if isinstance(result, dict) and "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"User {u['username']} deleted.")
                            st.rerun()