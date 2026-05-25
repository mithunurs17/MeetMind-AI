import json
from datetime import datetime, date

import streamlit as st
from utils.api_client import api_client
from utils.ui import apply_theme, info_card

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
apply_theme()

st.markdown("# 📊 Meeting Dashboard")
st.markdown("Review historical meetings, search and filter by owner or date, and export meeting analytics.")

meetings_response = api_client.get_meetings()
if "error" in meetings_response:
    st.error(f"Error loading meetings: {meetings_response.get('error')}")
    st.stop()

meetings = meetings_response or []
if not meetings:
    st.info("No meetings found yet. Upload a meeting to populate dashboard analytics.")
    st.stop()

owners = sorted({item.get("owner") for meeting in meetings for item in meeting.get("action_items", []) if item.get("owner")})
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

search_text = st.text_input("Search meetings", placeholder="Search by title, summary, or owner")
owner_filter = st.selectbox("Filter by owner", ["All"] + owners)
selected_range = st.date_input("Date range", [min_date, max_date])

filtered_meetings = []
for meeting in meetings:
    created_at = meeting.get("created_at")
    try:
        meeting_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date() if created_at else None
    except Exception:
        meeting_date = None

    if selected_range and meeting_date and not (selected_range[0] <= meeting_date <= selected_range[1]):
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

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    info_card("Meetings", str(len(filtered_meetings)), "Meetings in this view", "#b30000")
with col2:
    info_card("Action Items", str(sum(len(m.get("action_items", [])) for m in filtered_meetings)), "Filtered tasks", "#a3103a")
with col3:
    info_card("Decisions", str(sum(len(m.get("decisions", [])) for m in filtered_meetings)), "Filtered decisions", "#421522")
with col4:
    info_card("Risks", str(sum(len(m.get("risks", [])) for m in filtered_meetings)), "Filtered risks", "#99ab0f")

st.markdown("---")

if filtered_meetings:
    st.markdown("### Historical Meetings")
    for meeting in filtered_meetings:
        with st.expander(f"{meeting.get('title')} — {meeting.get('created_at', 'N/A')}"):
            st.markdown(f"**Summary:** {meeting.get('summary', 'No summary available.')}")
            st.markdown(f"**Action items:** {len(meeting.get('action_items', []))}")
            st.markdown(f"**Decisions:** {len(meeting.get('decisions', []))}")
            st.markdown(f"**Risks:** {len(meeting.get('risks', []))}")
            if meeting.get('open_questions'):
                st.markdown("**Open Questions:**")
                for q in meeting.get('open_questions', []):
                    st.write(f"- {q}")

    st.download_button(
        "Export filtered meeting history",
        json.dumps(filtered_meetings, default=str, indent=2),
        file_name="filtered_meetings.json",
        mime="application/json",
    )
else:
    st.warning("No meetings match this dashboard filter set.")
