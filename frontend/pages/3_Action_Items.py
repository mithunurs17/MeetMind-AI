import streamlit as st
from utils.api_client import api_client
from utils.auth import is_logged_in
from utils.ui import apply_theme

st.set_page_config(page_title="Action Items", page_icon="✅", layout="wide")
apply_theme()

# ── Sidebar user badge ────────────────────────────────────────────────────
try:
    from utils.guards import render_user_badge
    render_user_badge()
except Exception:
    pass

# ── Global CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');
:root{--bg:hsl(260,87%,3%);--fg:hsl(40,6%,95%);--sub:hsl(40,6%,72%);--accent:#6366f1;--accent2:#a855f7}
html,body,[class*="css"]{font-family:'Geist Sans',sans-serif!important;background:var(--bg)!important;color:var(--fg)!important}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:var(--bg)!important}
section[data-testid="stSidebar"]{background:hsl(260,70%,5%)!important;border-right:1px solid rgba(255,255,255,0.06)}
section[data-testid="stSidebar"] *{color:var(--fg)!important}
h1{color:var(--fg)!important;font-weight:700!important}
h2,h3{color:var(--fg)!important;font-weight:600!important}
[data-testid="stMetricLabel"]{color:var(--sub)!important;font-size:12px!important;text-transform:uppercase!important;letter-spacing:.06em!important}
[data-testid="stMetricValue"]{color:var(--fg)!important;font-weight:700!important;font-size:36px!important}
[data-testid="metric-container"]{background:rgba(255,255,255,0.03)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:16px!important;padding:18px 20px!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"]{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;color:var(--fg)!important;font-family:'Geist Sans',sans-serif!important}
[data-baseweb="popover"]{background:hsl(260,60%,6%)!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:12px!important}
[data-baseweb="option"]{color:var(--fg)!important}
[data-baseweb="option"]:hover{background:rgba(99,102,241,0.15)!important}
label{color:var(--sub)!important;font-size:12px!important;font-weight:500!important;letter-spacing:.04em!important;text-transform:uppercase!important}
.stButton>button{border:1px solid rgba(255,255,255,0.14)!important;border-radius:999px!important;background:rgba(255,255,255,0.06)!important;color:var(--fg)!important;font-weight:500!important;padding:0.65rem 1.6rem!important;font-family:'Geist Sans',sans-serif!important;transition:all .2s!important}
.stButton>button:hover{background:rgba(99,102,241,0.22)!important;border-color:var(--accent)!important;transform:scale(1.02)!important}
hr{border-color:rgba(255,255,255,0.08)!important}
[data-testid="stAlert"]{border-radius:14px!important;border:1px solid rgba(255,255,255,0.08)!important;background:rgba(255,255,255,0.04)!important}
.action-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:16px 20px;margin-bottom:10px;transition:border-color .2s,transform .2s}
.action-card:hover{border-color:rgba(99,102,241,0.35);transform:translateX(4px)}
.action-title{font-size:15px;font-weight:600;color:hsl(40,6%,95%);margin-bottom:6px}
.action-meta{font-size:13px;color:hsl(40,6%,62%)}
.action-meta b{color:hsl(40,6%,88%)}
.badge{display:inline-block;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}
.badge-pending{background:rgba(245,158,11,0.15);color:#fcd34d;border:1px solid rgba(245,158,11,0.3)}
.badge-progress{background:rgba(99,102,241,0.15);color:#a5b4fc;border:1px solid rgba(99,102,241,0.3)}
.badge-completed{background:rgba(34,197,94,0.12);color:#86efac;border:1px solid rgba(34,197,94,0.25)}
.update-panel{background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);border-radius:18px;padding:24px 28px;margin-top:8px}
.filter-bar{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:20px 24px;margin-bottom:24px}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────
st.markdown("# ✅ Action Items")
st.markdown(
    "<p style='color:hsl(40,6%,72%);font-size:16px;margin-top:-8px;'>"
    "Track and manage action items extracted from meeting minutes with quick filters and updates.</p>",
    unsafe_allow_html=True,
)

# ── Auth guard (soft) ─────────────────────────────────────────────────────
if not is_logged_in():
    st.info("🔐 Please sign in to view action items. Use the sidebar to navigate to Sign In.")
    st.stop()

# ── Fetch data ───────────────────────────────────────────────────────────
meetings_response = api_client.get_meetings()
all_items = []

if isinstance(meetings_response, list):
    for meeting in meetings_response:
        for item in meeting.get("action_items", []):
            record = item.copy()
            record["meeting_title"] = meeting.get("title")
            record["meeting_id"]    = meeting.get("id")
            all_items.append(record)
elif isinstance(meetings_response, dict) and "error" in meetings_response:
    err = meetings_response.get("error", "")
    if "401" in str(err) or "not authenticated" in str(err).lower():
        st.error("🔐 Session expired. Please sign in again via the sidebar.")
    else:
        st.error(f"Error loading meetings: {err}")
    st.stop()

status_values = sorted({item.get("status", "pending") for item in all_items})
owners        = sorted({item.get("owner") for item in all_items if item.get("owner")})

# ── Summary metrics ──────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Total Action Items", len(all_items))
c2.metric("Pending",   sum(1 for i in all_items if i.get("status") == "pending"))
c3.metric("Completed", sum(1 for i in all_items if i.get("status") == "completed"))

st.markdown("---")

if not all_items:
    st.info("No action items found. Upload a meeting transcript to extract action items.")
    st.stop()

# ── Filters ──────────────────────────────────────────────────────────────
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
f1, f2 = st.columns(2)
with f1:
    filter_owner  = st.selectbox("Filter by owner",  ["All"] + owners)
with f2:
    filter_status = st.selectbox("Filter by status", ["All"] + status_values)
st.markdown("</div>", unsafe_allow_html=True)

filtered_items = [
    item for item in all_items
    if (filter_owner  == "All" or item.get("owner")           == filter_owner)
    and (filter_status == "All" or item.get("status", "pending") == filter_status)
]

# ── Item list ────────────────────────────────────────────────────────────
def _badge(status: str) -> str:
    cls = {
        "pending":     "badge-pending",
        "in progress": "badge-progress",
        "completed":   "badge-completed",
    }.get((status or "pending").lower(), "badge-pending")
    return f"<span class='badge {cls}'>{status or 'pending'}</span>"

if filtered_items:
    for item in filtered_items:
        st.markdown(
            f"<div class='action-card'>"
            f"  <div class='action-title'>{item.get('task')}"
            f"    <span style='font-size:12px;font-weight:400;color:hsl(40,6%,55%);margin-left:10px;'>"
            f"      {item.get('meeting_title', 'Meeting')}</span>"
            f"  </div>"
            f"  <div class='action-meta'>"
            f"    Owner: <b>{item.get('owner') or 'Unassigned'}</b> &nbsp;|&nbsp; "
            f"    Due: <b>{item.get('due_date') or 'TBD'}</b> &nbsp;|&nbsp; "
            f"    {_badge(item.get('status', 'pending'))}"
            f"  </div>"
            f"</div>",
            unsafe_allow_html=True,
        )
else:
    st.info("No action items match the selected filters.")

# ── Update panel ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🔄 Update Action Item Status")

st.markdown("<div class='update-panel'>", unsafe_allow_html=True)

item_options = {f"{item['id']} — {item['task']}": item for item in all_items}
if item_options:
    selected_key = st.selectbox("Select an action item", list(item_options.keys()))

    if selected_key:
        selected_item = item_options[selected_key]
        current_status = selected_item.get("status", "pending")
        status_list = ["pending", "in progress", "completed"]
        idx = status_list.index(current_status) if current_status in status_list else 0

        new_status = st.selectbox("New Status", status_list, index=idx)

        if st.button("Update Status"):
            result = api_client.update_action_item_status(selected_item["id"], new_status)
            if result.get("error"):
                st.error(f"Error updating action item: {result['error']}")
            else:
                st.success("✅ Action item updated successfully.")
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)