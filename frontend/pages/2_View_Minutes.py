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

st.set_page_config(page_title="View Minutes", page_icon="📋", layout="wide")
apply_theme()

st.markdown("# 📋 View Meeting Minutes")
st.markdown("Review extracted meeting minutes, edit summaries, and export polished outputs.")

meetings_response = api_client.get_meetings()
if "error" in meetings_response:
    st.error(f"Error loading meetings: {meetings_response.get('error')}")
    st.stop()

meetings = meetings_response or []
if not meetings:
    st.info("No meetings found yet. Upload a meeting to begin.")
    st.stop()

owners = sorted({item.get("owner") for m in meetings for item in m.get("action_items", []) if item.get("owner")})
all_dates = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    if created_at:
        try:
            all_dates.append(datetime.fromisoformat(created_at.replace("Z", "+00:00")).date())
        except ValueError:
            continue

if all_dates:
    min_date, max_date = min(all_dates), max(all_dates)
else:
    min_date = date.today()
    max_date = date.today()

search_text = st.text_input("🔍 Search meetings", placeholder="Title, summary, or decision text")
owner_filter = st.selectbox("Filter action item owner", ["All"] + owners)
date_range = st.date_input("Filter meetings by date", [min_date, max_date])

filtered_meetings = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    try:
        meeting_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date() if created_at else None
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
        ]).lower()
        if query not in text_blob:
            continue
    filtered_meetings.append(meeting)

if not filtered_meetings:
    st.warning("No meetings match the selected filters. Adjust filters or upload a new meeting.")
    st.stop()

selected_label = st.selectbox(
    "Select a meeting to view details",
    [f"{meeting.get('id')} — {meeting.get('title')} ({meeting.get('created_at', 'N/A')})" for meeting in filtered_meetings]
)
selected_meeting = next(
    (meeting for meeting in filtered_meetings if str(meeting.get('id')) in selected_label),
    filtered_meetings[0],
)

summary_text = selected_meeting.get("summary", "")
decisions_text = "\n".join([item.get("decision_text", str(item)) for item in selected_meeting.get("decisions", [])])
open_questions = selected_meeting.get("open_questions") or []
action_items = selected_meeting.get("action_items") or []
risks = selected_meeting.get("risks") or []

st.markdown("---")
left, right = st.columns([3, 2])
with left:
    st.markdown("## Executive Summary")
    editable_summary = st.text_area("Editable executive summary", summary_text, height=200)

    st.markdown("## Decisions")
    editable_decisions = st.text_area("Editable decisions", decisions_text, height=160)

    st.markdown("## Open Questions")
    editable_questions = st.text_area("Editable open questions", "\n".join(open_questions), height=140)

with right:
    st.markdown("## Action Items")
    if action_items:
        table_data = [
            {
                "Task": item.get("task"),
                "Owner": item.get("owner") or "Unassigned",
                "Due": str(item.get("due_date") or "TBD"),
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
            st.write(f"• {risk.get('risk_text', str(risk))}")
    else:
        st.info("No risks detected.")

    st.markdown("## Metadata")
    st.write(f"**Created:** {selected_meeting.get('created_at', 'N/A')}")
    st.write(f"**Meeting ID:** {selected_meeting.get('id')}")

export_payload = {
    "id": selected_meeting.get("id"),
    "title": selected_meeting.get("title"),
    "created_at": selected_meeting.get("created_at"),
    "summary": editable_summary,
    "decisions": [line for line in editable_decisions.splitlines() if line.strip()],
    "action_items": action_items,
    "risks": risks,
    "open_questions": [line for line in editable_questions.splitlines() if line.strip()],
}

markdown_export = f"# {selected_meeting.get('title')}\n\n## Executive Summary\n{editable_summary}\n\n## Decisions\n"
for line in export_payload["decisions"]:
    markdown_export += f"- {line}\n"
markdown_export += "\n## Action Items\n"
for item in action_items:
    markdown_export += f"- {item.get('task')} (Owner: {item.get('owner') or 'Unassigned'}, Due: {item.get('due_date') or 'TBD'}, Status: {item.get('status') or 'pending'})\n"
markdown_export += "\n## Risks & Dependencies\n"
for risk in risks:
    markdown_export += f"- {risk.get('risk_text', str(risk))}\n"
markdown_export += "\n## Open Questions\n"
for question in export_payload["open_questions"]:
    markdown_export += f"- {question}\n"

pdf_name, timestamp = build_export_filename(selected_meeting.get("title", "meeting"), "pdf")
docx_name, _ = build_export_filename(selected_meeting.get("title", "meeting"), "docx")
pdf_bytes = create_meeting_pdf(
    title=selected_meeting.get("title", "Meeting"),
    summary=editable_summary,
    decisions=export_payload["decisions"],
    action_items=action_items,
    risks=risks,
    open_questions=export_payload["open_questions"],
    filename=pdf_name,
    timestamp=timestamp,
)
docx_bytes = create_meeting_docx(
    title=selected_meeting.get("title", "Meeting"),
    summary=editable_summary,
    decisions=export_payload["decisions"],
    action_items=action_items,
    risks=risks,
    open_questions=export_payload["open_questions"],
    filename=docx_name,
    timestamp=timestamp,
)


st.download_button(
    "Download editable minutes (Markdown)",
    markdown_export,
    file_name=f"meeting_{selected_meeting.get('id')}_notes.md",
    mime="text/markdown",
)

st.download_button(
    "Download editable minutes (DOCX)",
    docx_bytes,
    file_name=docx_name,
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)
