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

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="View Minutes",
    page_icon="📋",
    layout="wide"
)

apply_theme()

st.markdown("# 📋 View Meeting Minutes")
st.markdown(
    "Review extracted meeting minutes, edit summaries, and export polished outputs."
)

# ---------------------------------------------------
# FETCH MEETINGS
# ---------------------------------------------------

meetings_response = api_client.get_meetings()

if "error" in meetings_response:
    st.error(f"Error loading meetings: {meetings_response.get('error')}")
    st.stop()

meetings = meetings_response or []

if not meetings:
    st.info("No meetings found yet. Upload a meeting to begin.")
    st.stop()

# ---------------------------------------------------
# FILTER DATA PREP
# ---------------------------------------------------

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
            parsed_date = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).date()

            all_dates.append(parsed_date)

        except Exception:
            pass

if all_dates:
    min_date = min(all_dates)
    max_date = max(all_dates)
else:
    min_date = date.today()
    max_date = date.today()

# ---------------------------------------------------
# FILTER UI
# ---------------------------------------------------

st.markdown("## 🔍 Search & Filters")

col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input(
        "Search meetings",
        placeholder="Search by title, summary, decisions..."
    )

with col2:
    owner_filter = st.selectbox(
        "Filter by action item owner",
        ["All"] + owners
    )

date_range = st.date_input(
    "Filter meetings by date",
    [min_date, max_date]
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_meetings = []

for meeting in meetings:

    # ---------------- DATE FILTER ----------------

    created_at = meeting.get("created_at")

    try:
        meeting_date = (
            datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).date()
            if created_at
            else None
        )
    except Exception:
        meeting_date = None

    if (
        date_range
        and meeting_date
        and not (date_range[0] <= meeting_date <= date_range[1])
    ):
        continue

    # ---------------- OWNER FILTER ----------------

    if owner_filter != "All":

        owners_in_meeting = {
            item.get("owner")
            for item in meeting.get("action_items", [])
            if item.get("owner")
        }

        if owner_filter not in owners_in_meeting:
            continue

    # ---------------- SEARCH FILTER ----------------

    if search_text:

        query = search_text.lower()

        text_blob = " ".join([
            str(meeting.get("title", "")),
            str(meeting.get("summary", "")),

            " ".join([
                d.get("decision_text", "")
                for d in meeting.get("decisions", [])
            ]),

            " ".join([
                a.get("task", "")
                for a in meeting.get("action_items", [])
            ]),

            " ".join(meeting.get("open_questions", [])),
        ]).lower()

        if query not in text_blob:
            continue

    filtered_meetings.append(meeting)

# ---------------------------------------------------
# NO MATCH
# ---------------------------------------------------

if not filtered_meetings:
    st.warning(
        "No meetings match the selected filters. "
        "Adjust filters or upload a new meeting."
    )
    st.stop()

# ---------------------------------------------------
# MEETING SELECTOR
# ---------------------------------------------------

meeting_options = {
    f"{meeting.get('title')} ({meeting.get('created_at', 'N/A')})": meeting
    for meeting in filtered_meetings
}

selected_label = st.selectbox(
    "Select a meeting to view details",
    list(meeting_options.keys())
)

selected_meeting = meeting_options[selected_label]

# ---------------------------------------------------
# EXTRACT MEETING DATA
# ---------------------------------------------------

summary_text = selected_meeting.get("summary", "")

decisions_text = "\n".join([
    item.get("decision_text", str(item))
    for item in selected_meeting.get("decisions", [])
])

open_questions = selected_meeting.get("open_questions") or []

action_items = selected_meeting.get("action_items") or []

risks = selected_meeting.get("risks") or []

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------

st.markdown("---")

left, right = st.columns([3, 2])

# ---------------------------------------------------
# LEFT COLUMN
# ---------------------------------------------------

with left:

    st.markdown("## Executive Summary")

    editable_summary = st.text_area(
        "Editable executive summary",
        summary_text,
        height=220
    )

    st.markdown("## Decisions")

    editable_decisions = st.text_area(
        "Editable decisions",
        decisions_text,
        height=180
    )

    st.markdown("## Open Questions")

    editable_questions = st.text_area(
        "Editable open questions",
        "\n".join(open_questions),
        height=150
    )

# ---------------------------------------------------
# RIGHT COLUMN
# ---------------------------------------------------

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

    # ---------------- RISKS ----------------

    st.markdown("## Risks & Dependencies")

    if risks:

        for risk in risks:

            risk_text = (
                risk.get("risk_text")
                if isinstance(risk, dict)
                else str(risk)
            )

            st.write(f"• {risk_text}")

    else:
        st.info("No risks detected.")

    # ---------------- METADATA ----------------

    st.markdown("## Metadata")

    st.write(
        f"**Created:** "
        f"{selected_meeting.get('created_at', 'N/A')}"
    )

    st.write(
        f"**Meeting ID:** "
        f"{selected_meeting.get('id')}"
    )

# ---------------------------------------------------
# EXPORT PAYLOAD
# ---------------------------------------------------

export_payload = {
    "id": selected_meeting.get("id"),
    "title": selected_meeting.get("title"),
    "created_at": selected_meeting.get("created_at"),
    "summary": editable_summary,
    "decisions": [
        line
        for line in editable_decisions.splitlines()
        if line.strip()
    ],
    "action_items": action_items,
    "risks": risks,
    "open_questions": [
        line
        for line in editable_questions.splitlines()
        if line.strip()
    ],
}

# ---------------------------------------------------
# MARKDOWN EXPORT
# ---------------------------------------------------

markdown_export = (
    f"# {selected_meeting.get('title')}\n\n"
)

markdown_export += (
    f"## Executive Summary\n"
    f"{editable_summary}\n\n"
)

markdown_export += "## Decisions\n"

for line in export_payload["decisions"]:
    markdown_export += f"- {line}\n"

markdown_export += "\n## Action Items\n"

for item in action_items:

    markdown_export += (
        f"- {item.get('task')} "
        f"(Owner: {item.get('owner') or 'Unassigned'}, "
        f"Due: {item.get('due_date') or 'TBD'}, "
        f"Status: {item.get('status') or 'pending'})\n"
    )

markdown_export += "\n## Risks & Dependencies\n"

for risk in risks:

    risk_text = (
        risk.get("risk_text")
        if isinstance(risk, dict)
        else str(risk)
    )

    markdown_export += f"- {risk_text}\n"

markdown_export += "\n## Open Questions\n"

for question in export_payload["open_questions"]:
    markdown_export += f"- {question}\n"

# ---------------------------------------------------
# EXPORT FILES
# ---------------------------------------------------

pdf_name, timestamp = build_export_filename(
    selected_meeting.get("title", "meeting"),
    "pdf"
)

docx_name, _ = build_export_filename(
    selected_meeting.get("title", "meeting"),
    "docx"
)

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

# ---------------------------------------------------
# DOWNLOAD BUTTONS
# ---------------------------------------------------

st.markdown("---")

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

st.download_button(
    "Download editable minutes (PDF)",
    pdf_bytes,
    file_name=pdf_name,
    mime="application/pdf",
)

st.download_button(
    "Download JSON",
    json.dumps(export_payload, indent=2, default=str),
    file_name="meeting_minutes.json",
    mime="application/json",
)