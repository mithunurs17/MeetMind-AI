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