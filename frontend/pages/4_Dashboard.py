import json
from datetime import datetime, date

import streamlit as st
import streamlit.components.v1 as components
from utils.api_client import api_client
from utils.auth import is_logged_in
from utils.ui import apply_theme, info_card

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
apply_theme()

# ── Global CSS matching app.py hero theme ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:      hsl(260, 87%, 3%);
  --fg:      hsl(40, 6%, 95%);
  --sub:     hsl(40, 6%, 72%);
  --accent:  #6366f1;
  --accent2: #a855f7;
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

h1 { color: var(--fg) !important; font-weight: 700 !important; }
h2, h3 { color: var(--fg) !important; font-weight: 600 !important; }

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stDateInput"] input {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--fg) !important;
  font-family: 'Geist Sans', sans-serif !important;
}

label {
  color: var(--sub) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
}

[data-testid="stExpander"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
  margin-bottom: 10px !important;
}
[data-testid="stExpander"] summary {
  color: var(--fg) !important;
  font-weight: 500 !important;
}

.stButton > button,
.stDownloadButton > button {
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
.stDownloadButton > button:hover {
  background: rgba(99,102,241,0.22) !important;
  border-color: var(--accent) !important;
  transform: scale(1.02) !important;
}

hr { border-color: rgba(255,255,255,0.08) !important; }

[data-testid="stAlert"] {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  background: rgba(255,255,255,0.04) !important;
}

.glass-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(14px);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.filter-bar {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  padding: 20px 24px;
  margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar user badge ────────────────────────────────────────────────────
try:
    from utils.guards import render_user_badge
    render_user_badge()
except Exception:
    pass

# ── Header ───────────────────────────────────────────────────────────────
st.markdown("# 📊 Meeting Dashboard")
st.markdown(
    "<p style='color:hsl(40,6%,72%);font-size:16px;margin-top:-8px;'>"
    "Review your meetings, search and filter by owner or date, and export analytics.</p>",
    unsafe_allow_html=True,
)

# ── Auth guard ────────────────────────────────────────────────────────────
if not is_logged_in():
    st.info("🔐 Please sign in to view your dashboard. Use the sidebar to navigate to Sign In.")
    st.stop()

# ── Fetch data ───────────────────────────────────────────────────────────
meetings_response = api_client.get_meetings()

# Handle error response (dict with "error" key)
if isinstance(meetings_response, dict) and "error" in meetings_response:
    err = meetings_response.get("error", "")
    if "401" in str(err) or "not authenticated" in str(err).lower():
        st.error("🔐 Session expired. Please sign in again via the sidebar.")
    else:
        st.error(f"Error loading meetings: {err}")
    st.stop()

meetings = meetings_response if isinstance(meetings_response, list) else []

if not meetings:
    st.info("No meetings found yet. Upload a meeting to populate dashboard analytics.")
    st.stop()

owners = sorted({
    item.get("owner")
    for meeting in meetings
    for item in meeting.get("action_items", [])
    if item.get("owner")
})
all_dates = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    if created_at:
        try:
            all_dates.append(datetime.fromisoformat(created_at.replace("Z", "+00:00")).date())
        except ValueError:
            continue

min_date = min(all_dates) if all_dates else date.today()
max_date = max(all_dates) if all_dates else date.today()

# ── Filters ──────────────────────────────────────────────────────────────
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
search_text    = st.text_input("Search meetings", placeholder="Search by title, summary, or owner")
owner_filter   = st.selectbox("Filter by owner", ["All"] + owners)
selected_range = st.date_input("Date range", [min_date, max_date])
st.markdown("</div>", unsafe_allow_html=True)

# ── Apply filters ────────────────────────────────────────────────────────
filtered_meetings = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    try:
        meeting_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date() if created_at else None
    except Exception:
        meeting_date = None

    if (
        selected_range
        and len(selected_range) == 2
        and meeting_date
        and not (selected_range[0] <= meeting_date <= selected_range[1])
    ):
        continue
    if owner_filter != "All":
        action_item_owners = {item.get("owner") for item in meeting.get("action_items", []) if item.get("owner")}
        if owner_filter not in action_item_owners:
            continue
    if search_text:
        query = search_text.lower()
        full_text = " ".join([
            str(meeting.get("title", "")),
            str(meeting.get("summary", "")),
            " ".join([item.get("task", "") for item in meeting.get("action_items", [])]),
        ]).lower()
        if query not in full_text:
            continue
    filtered_meetings.append(meeting)

# ── Metric cards via inline HTML ─────────────────────────────────────────
total_meetings  = len(filtered_meetings)
total_actions   = sum(len(m.get("action_items", [])) for m in filtered_meetings)
total_decisions = sum(len(m.get("decisions", [])) for m in filtered_meetings)
total_risks     = sum(len(m.get("risks", [])) for m in filtered_meetings)

st.markdown("---")
components.html(f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Geist+Sans:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:'Geist Sans',sans-serif}}
.row{{display:flex;gap:18px}}
.card{{flex:1;border-radius:20px;padding:26px 22px;color:hsl(40,6%,95%);box-shadow:0 12px 32px rgba(0,0,0,.6);transition:transform .28s ease;min-width:0}}
.card:hover{{transform:translateY(-6px)}}
.label{{font-size:11px;font-weight:500;letter-spacing:.7px;text-transform:uppercase;opacity:.78}}
.value{{font-size:48px;font-weight:700;line-height:1;margin:10px 0 6px}}
.desc{{font-size:12px;opacity:.62}}
</style></head><body>
<div class="row">
  <div class="card" style="background:linear-gradient(135deg,#3730a3,#6366f1)">
    <div class="label">My Meetings</div><div class="value">{total_meetings}</div><div class="desc">Meetings in this view</div>
  </div>
  <div class="card" style="background:linear-gradient(135deg,#0369a1,#3b82f6)">
    <div class="label">Action Items</div><div class="value">{total_actions}</div><div class="desc">Filtered tasks</div>
  </div>
  <div class="card" style="background:linear-gradient(135deg,#b45309,#f59e0b)">
    <div class="label">Decisions</div><div class="value">{total_decisions}</div><div class="desc">Filtered decisions</div>
  </div>
  <div class="card" style="background:linear-gradient(135deg,#7e22ce,#a855f7)">
    <div class="label">Risks</div><div class="value">{total_risks}</div><div class="desc">Filtered risks</div>
  </div>
</div>
</body></html>""", height=148)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Meeting list ─────────────────────────────────────────────────────────
if filtered_meetings:
    st.markdown("### My Meetings")
    for meeting in filtered_meetings:
        with st.expander(f"{meeting.get('title')} — {meeting.get('created_at', 'N/A')}"):
            st.markdown(f"**Summary:** {meeting.get('summary', 'No summary available.')}")
            col1, col2, col3 = st.columns(3)
            col1.markdown(
                f"<div style='text-align:center;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:12px;'>"
                f"<div style='font-size:28px;font-weight:700'>{len(meeting.get('action_items', []))}</div>"
                f"<div style='font-size:12px;color:#a5b4fc;'>Action Items</div></div>",
                unsafe_allow_html=True,
            )
            col2.markdown(
                f"<div style='text-align:center;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:12px;padding:12px;'>"
                f"<div style='font-size:28px;font-weight:700'>{len(meeting.get('decisions', []))}</div>"
                f"<div style='font-size:12px;color:#fcd34d;'>Decisions</div></div>",
                unsafe_allow_html=True,
            )
            col3.markdown(
                f"<div style='text-align:center;background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:12px;'>"
                f"<div style='font-size:28px;font-weight:700'>{len(meeting.get('risks', []))}</div>"
                f"<div style='font-size:12px;color:#d8b4fe;'>Risks</div></div>",
                unsafe_allow_html=True,
            )
            if meeting.get("open_questions"):
                st.markdown("**Open Questions:**")
                for q in meeting.get("open_questions", []):
                    st.write(f"• {q}")

    st.markdown("<br/>", unsafe_allow_html=True)

else:
    st.warning("No meetings match this filter set.")