import streamlit as st
from utils.api_client import api_client
from utils.ui import apply_theme

st.set_page_config(page_title="Action Items", page_icon="✅", layout="wide")
apply_theme()

st.markdown("# ✅ Action Items")
st.markdown("Track and manage action items extracted from meeting minutes with quick filters and updates.")

meetings_response = api_client.get_meetings()
all_items = []
if "error" not in meetings_response:
    meetings = meetings_response or []
    for meeting in meetings:
        for item in meeting.get("action_items", []):
            item_record = item.copy()
            item_record["meeting_title"] = meeting.get("title")
            item_record["meeting_id"] = meeting.get("id")
            all_items.append(item_record)
else:
    st.error(f"Error loading meetings: {meetings_response.get('error')}")
    st.stop()

status_values = sorted({item.get("status", "pending") for item in all_items})
owners = sorted({item.get("owner") for item in all_items if item.get("owner")})

col1, col2, col3 = st.columns(3)
col1.metric("Total Action Items", len(all_items))
col2.metric("Pending", sum(1 for i in all_items if i.get("status") == "pending"))
col3.metric("Completed", sum(1 for i in all_items if i.get("status") == "completed"))

st.markdown("---")

filters_col1, filters_col2 = st.columns(2)
with filters_col1:
    filter_owner = st.selectbox("Filter by owner", ["All"] + owners)
with filters_col2:
    filter_status = st.selectbox("Filter by status", ["All"] + status_values)

filtered_items = [
    item for item in all_items
    if (filter_owner == "All" or item.get("owner") == filter_owner)
    and (filter_status == "All" or item.get("status", "pending") == filter_status)
]

if filtered_items:
    for item in filtered_items:
        st.markdown(
            f"**{item.get('task')}** — {item.get('meeting_title', 'Meeting')}  \n"
            f"Owner: **{item.get('owner') or 'Unassigned'}** | Due: **{item.get('due_date') or 'TBD'}** | Status: **{item.get('status') or 'pending'}**"
        )
        st.write("---")
else:
    st.info("No action items match the selected filters.")

st.markdown("---")
st.subheader("Update Action Item Status")
item_options = {f"{item['id']} — {item['task']}": item for item in all_items}
selected_key = st.selectbox("Select an action item", list(item_options.keys()))
if selected_key:
    selected_item = item_options[selected_key]
    new_status = st.selectbox(
        "New Status",
        ["pending", "in progress", "completed"],
        index=["pending", "in progress", "completed"].index(selected_item.get("status", "pending"))
    )
    if st.button("Update Status"):
        result = api_client.update_action_item_status(selected_item["id"], new_status)
        if result.get("error"):
            st.error(f"Error updating action item: {result['error']}")
        else:
            st.success("Action item updated successfully.")
            st.experimental_rerun()
