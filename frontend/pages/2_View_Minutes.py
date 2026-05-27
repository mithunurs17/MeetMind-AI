import json
from datetime import datetime, date

import streamlit as st
from utils.api_client import api_client
from utils.export import (
    build_export_filename,
    create_meeting_docx,
    create_meeting_pdf,
)
from utils.ui import apply_theme

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="View Minutes", page_icon="📋", layout="wide")
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
[data-testid="stSidebarNavLink"][aria-selected="true"] span,
[data-testid="stSidebarNavLink"][aria-selected="true"] p {
  color: #fff !important;
}
[data-testid="stSidebarNavLink"]::before {
  background: transparent !important;
  display: none !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"]::after,
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"]::before {
  display: none !important;
  background: transparent !important;
}

h1 { color: var(--fg) !important; font-weight: 700 !important; }
h2, h3 { color: var(--fg) !important; font-weight: 600 !important; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stDateInput"] input {
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

/* Selectbox dropdown */
[data-baseweb="popover"] {
  background: hsl(260, 60%, 6%) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 12px !important;
}
[data-baseweb="option"] { color: var(--fg) !important; }
[data-baseweb="option"]:hover { background: rgba(99,102,241,0.15) !important; }

/* Labels */
label {
  color: var(--sub) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 999px !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--fg) !important;
  font-weight: 500 !important;
  padding: 0.6rem 1.2rem !important;
  font-family: 'Geist Sans', sans-serif !important;
  transition: background 0.2s ease, transform 0.2s ease !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
  background: rgba(99,102,241,0.22) !important;
  border-color: var(--accent) !important;
  transform: scale(1.02) !important;
}

/* Table */
[data-testid="stTable"] table {
  background: transparent !important;
  color: var(--fg) !important;
  border-collapse: collapse !important;
  width: 100% !important;
}
[data-testid="stTable"] th {
  background: rgba(99,102,241,0.15) !important;
  color: var(--fg) !important;
  font-size: 12px !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  padding: 10px 14px !important;
  border: none !important;
}
[data-testid="stTable"] td {
  background: rgba(255,255,255,0.02) !important;
  color: var(--sub) !important;
  border-top: 1px solid rgba(255,255,255,0.06) !important;
  padding: 10px 14px !important;
}
[data-testid="stTable"] tr:hover td {
  background: rgba(255,255,255,0.05) !important;
}

hr { border-color: rgba(255,255,255,0.08) !important; }

[data-testid="stAlert"] {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  background: rgba(255,255,255,0.04) !important;
}

/* Utility cards */
.glass-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(14px);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.glass-row {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 12px 18px;
  margin-bottom: 8px;
}
.meta-pill {
  display: inline-block;
  background: rgba(99,102,241,0.12);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: 999px;
  padding: 3px 12px;
  font-size: 12px;
  color: #a5b4fc;
  margin-right: 8px;
}

/* Search header section */
.filter-header {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  padding: 20px 24px;
  margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────
st.markdown("# 📋 View Meeting Minutes")
st.markdown(
    "<p style='color:hsl(40,6%,72%);font-size:16px;margin-top:-8px;'>"
    "Review extracted meeting minutes, edit summaries, and export polished outputs.</p>",
    unsafe_allow_html=True,
)

# ── Fetch meetings ───────────────────────────────────────────────────────
meetings_response = api_client.get_meetings()
if "error" in meetings_response:
    st.error(f"Error loading meetings: {meetings_response.get('error')}")
    st.stop()

meetings = meetings_response or []
if not meetings:
    st.info("No meetings found yet. Upload a meeting to begin.")
    st.stop()

# ── Filter data prep ─────────────────────────────────────────────────────
owners = sorted({
    item.get("owner")
    for m in meetings
    for item in m.get("action_items", [])
    if item.get("owner")
})

all_dates = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    if created_at:
        try:
            all_dates.append(datetime.fromisoformat(created_at.replace("Z", "+00:00")).date())
        except Exception:
            pass

min_date = min(all_dates) if all_dates else date.today()
max_date = max(all_dates) if all_dates else date.today()

# ── Filter UI ────────────────────────────────────────────────────────────
st.markdown("<div class='filter-header'>", unsafe_allow_html=True)
st.markdown("## 🔍 Search & Filters")
col1, col2 = st.columns(2)
with col1:
    search_text = st.text_input("Search meetings", placeholder="Search by title, summary, decisions...")
with col2:
    owner_filter = st.selectbox("Filter by action item owner", ["All"] + owners)

date_range = st.date_input("Filter meetings by date", [min_date, max_date])
st.markdown("</div>", unsafe_allow_html=True)

# ── Apply filters ────────────────────────────────────────────────────────
filtered_meetings = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    try:
        meeting_date = (
            datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
            if created_at else None
        )
    except Exception:
        meeting_date = None

    if date_range and meeting_date and not (date_range[0] <= meeting_date <= date_range[1]):
        continue

    if owner_filter != "All":
        owners_in_meeting = {item.get("owner") for item in meeting.get("action_items", []) if item.get("owner")}
        if owner_filter not in owners_in_meeting:
            continue

    if search_text:
        query = search_text.lower()
        text_blob = " ".join([
            str(meeting.get("title", "")),
            str(meeting.get("summary", "")),
            " ".join([d.get("decision_text", "") for d in meeting.get("decisions", [])]),
            " ".join([a.get("task", "") for a in meeting.get("action_items", [])]),
            " ".join(meeting.get("open_questions", [])),
        ]).lower()
        if query not in text_blob:
            continue

    filtered_meetings.append(meeting)

if not filtered_meetings:
    st.warning("No meetings match the selected filters. Adjust filters or upload a new meeting.")
    st.stop()

# ── Meeting selector ─────────────────────────────────────────────────────
meeting_options = {
    f"{meeting.get('title')} ({meeting.get('created_at', 'N/A')})": meeting
    for meeting in filtered_meetings
}
selected_label = st.selectbox("Select a meeting to view details", list(meeting_options.keys()))
selected_meeting = meeting_options[selected_label]

# ── Extract data ─────────────────────────────────────────────────────────
summary_text   = selected_meeting.get("summary", "")
decisions_text = "\n".join([item.get("decision_text", str(item)) for item in selected_meeting.get("decisions", [])])
open_questions = selected_meeting.get("open_questions") or []
action_items   = selected_meeting.get("action_items") or []
risks          = selected_meeting.get("risks") or []

st.markdown("---")

# ── Two-column layout ────────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown("## Executive Summary")
    editable_summary = st.text_area("Editable executive summary", summary_text, height=220)

    st.markdown("## Decisions")
    editable_decisions = st.text_area("Editable decisions", decisions_text, height=180)

    st.markdown("## Open Questions")
    editable_questions = st.text_area("Editable open questions", "\n".join(open_questions), height=150)

with right:
    st.markdown("## Action Items")
    if action_items:
        table_data = [
            {
                "Task":   item.get("task"),
                "Owner":  item.get("owner") or "Unassigned",
                "Due":    str(item.get("due_date") or "TBD"),
                "Status": item.get("status") or "pending",
            }
            for item in action_items
        ]
        st.table(table_data)
    else:
        st.info("No action items available for this meeting.")

    st.markdown("## Risks & Dependencies")
    if risks:
        for risk in risks:
            risk_text = risk.get("risk_text") if isinstance(risk, dict) else str(risk)
            st.markdown(f"<div class='glass-row'>• {risk_text}</div>", unsafe_allow_html=True)
    else:
        st.info("No risks detected.")

    st.markdown("## Metadata")
    st.markdown(
        f"<span class='meta-pill'>📅 {selected_meeting.get('created_at', 'N/A')}</span>"
        f"<span class='meta-pill'>🔑 {selected_meeting.get('id')}</span>",
        unsafe_allow_html=True,
    )

# ── Export payload ───────────────────────────────────────────────────────
export_payload = {
    "id":           selected_meeting.get("id"),
    "title":        selected_meeting.get("title"),
    "created_at":   selected_meeting.get("created_at"),
    "summary":      editable_summary,
    "decisions":    [l for l in editable_decisions.splitlines() if l.strip()],
    "action_items": action_items,
    "risks":        risks,
    "open_questions": [l for l in editable_questions.splitlines() if l.strip()],
}

# ── Markdown export ──────────────────────────────────────────────────────
markdown_export = f"# {selected_meeting.get('title')}\n\n## Executive Summary\n{editable_summary}\n\n## Decisions\n"
for line in export_payload["decisions"]:
    markdown_export += f"- {line}\n"
markdown_export += "\n## Action Items\n"
for item in action_items:
    markdown_export += (
        f"- {item.get('task')} (Owner: {item.get('owner') or 'Unassigned'}, "
        f"Due: {item.get('due_date') or 'TBD'}, Status: {item.get('status') or 'pending'})\n"
    )
markdown_export += "\n## Risks & Dependencies\n"
for risk in risks:
    risk_text = risk.get("risk_text") if isinstance(risk, dict) else str(risk)
    markdown_export += f"- {risk_text}\n"
markdown_export += "\n## Open Questions\n"
for question in export_payload["open_questions"]:
    markdown_export += f"- {question}\n"

# ── Export files ─────────────────────────────────────────────────────────
pdf_name, timestamp = build_export_filename(selected_meeting.get("title", "meeting"), "pdf")
docx_name, _ = build_export_filename(selected_meeting.get("title", "meeting"), "docx")

pdf_bytes = create_meeting_pdf(
    title=selected_meeting.get("title", "Meeting"),
    summary=editable_summary,
    decisions=export_payload["decisions"],
    action_items=action_items, risks=risks,
    open_questions=export_payload["open_questions"],
    filename=pdf_name, timestamp=timestamp,
)
docx_bytes = create_meeting_docx(
    title=selected_meeting.get("title", "Meeting"),
    summary=editable_summary,
    decisions=export_payload["decisions"],
    action_items=action_items, risks=risks,
    open_questions=export_payload["open_questions"],
    filename=docx_name, timestamp=timestamp,
)

# ── Download row ─────────────────────────────────────────────────────────
st.markdown("---")
dl1, dl2, dl3, dl4 = st.columns(4)
with dl1:
    st.download_button("📝 Markdown", markdown_export,
                       file_name=f"meeting_{selected_meeting.get('id')}_notes.md", mime="text/markdown")
with dl2:
    st.download_button("📃 DOCX", docx_bytes, file_name=docx_name,
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
