"""
5_Admin.py — User management page (admin only).
"""
import streamlit as st
from utils.api_client import api_client
from utils.auth import current_user, is_admin, is_logged_in

st.set_page_config(page_title="Admin — Users", page_icon="🛡️", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────────────
if not is_logged_in():
    st.warning("Please sign in to continue.")
    st.switch_page("pages/0_Login.py")

if not is_admin():
    st.error("🚫 Admin access required.")
    st.stop()

# ── Styles ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');
:root{--bg:hsl(260,87%,3%);--fg:hsl(40,6%,95%);--sub:hsl(40,6%,72%);--accent:#6366f1}
html,body,[class*="css"]{font-family:'Geist Sans',sans-serif!important;background:var(--bg)!important;color:var(--fg)!important}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:var(--bg)!important}
section[data-testid="stSidebar"]{background:hsl(260,70%,5%)!important;border-right:1px solid rgba(255,255,255,0.06)}
section[data-testid="stSidebar"] *{color:var(--fg)!important}
h1,h2,h3{color:var(--fg)!important;font-weight:700!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"]{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;color:var(--fg)!important}
label{color:var(--sub)!important;font-size:12px!important;font-weight:500!important;text-transform:uppercase!important;letter-spacing:.04em!important}
.stButton>button{border:1px solid rgba(255,255,255,0.14)!important;border-radius:999px!important;background:rgba(255,255,255,0.06)!important;color:var(--fg)!important;font-weight:500!important;padding:0.6rem 1.3rem!important;font-family:'Geist Sans',sans-serif!important;transition:all .2s!important}
.stButton>button:hover{background:rgba(99,102,241,0.22)!important;border-color:var(--accent)!important}
[data-testid="stAlert"]{border-radius:14px!important}
hr{border-color:rgba(255,255,255,0.08)!important}
.user-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:16px 20px;margin-bottom:10px}
.role-admin{background:rgba(168,85,247,0.15);color:#d8b4fe;border:1px solid rgba(168,85,247,0.3);border-radius:999px;padding:2px 10px;font-size:11px;font-weight:700;text-transform:uppercase}
.role-user{background:rgba(99,102,241,0.12);color:#a5b4fc;border:1px solid rgba(99,102,241,0.28);border-radius:999px;padding:2px 10px;font-size:11px;font-weight:700;text-transform:uppercase}
.active-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#86efac;margin-right:6px}
.inactive-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#f87171;margin-right:6px}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🛡️ User Management")
st.markdown(
    "<p style='color:hsl(40,6%,72%);font-size:16px;margin-top:-8px;'>"
    "Manage users, roles, and account status.</p>",
    unsafe_allow_html=True,
)

# ── Fetch users ───────────────────────────────────────────────────────────
users_resp = api_client.get_users()
if isinstance(users_resp, dict) and "error" in users_resp:
    st.error(f"Failed to load users: {users_resp['error']}")
    st.stop()

users = users_resp or []
me = current_user() or {}

# ── Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Total Users", len(users))
c2.metric("Admins", sum(1 for u in users if u.get("role") == "admin"))
c3.metric("Active", sum(1 for u in users if u.get("is_active")))

st.markdown("---")

# ── User list ─────────────────────────────────────────────────────────────
st.markdown("## 👥 Registered Users")
for user in users:
    role_badge = (
        "<span class='role-admin'>admin</span>"
        if user.get("role") == "admin"
        else "<span class='role-user'>user</span>"
    )
    active_dot = (
        "<span class='active-dot'></span>Active"
        if user.get("is_active")
        else "<span class='inactive-dot'></span>Inactive"
    )

    with st.expander(f"#{user['id']} — {user['username']}  ({user['email']})"):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                f"**Role:** {role_badge} &nbsp;&nbsp; **Status:** {active_dot}",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Joined:** {user.get('created_at', 'N/A')}")

        with col2:
            # Don't let admin deactivate themselves
            is_self = user["id"] == me.get("id")

            new_role = st.selectbox(
                "Role",
                ["user", "admin"],
                index=0 if user.get("role") == "user" else 1,
                key=f"role_{user['id']}",
                disabled=is_self,
            )
            new_active = st.checkbox(
                "Active",
                value=user.get("is_active", True),
                key=f"active_{user['id']}",
                disabled=is_self,
            )

            update_col, del_col = st.columns(2)
            with update_col:
                if st.button("Save", key=f"save_{user['id']}", disabled=is_self):
                    result = api_client.update_user(
                        user["id"], {"role": new_role, "is_active": new_active}
                    )
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("Updated!")
                        st.rerun()

            with del_col:
                if not is_self:
                    if st.button("🗑️ Delete", key=f"del_{user['id']}", type="secondary"):
                        result = api_client.delete_user(user["id"])
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"User {user['username']} deleted.")
                            st.rerun()