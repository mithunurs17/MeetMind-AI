import json
from datetime import datetime

import streamlit as st
from utils.api_client import api_client
from utils.ui import apply_theme, info_card

st.set_page_config(
    page_title="MeetMind AI Dashboard",
    page_icon="🎯",
    layout="wide",
)

apply_theme()

health_status = api_client.health_check()
meetings_response = api_client.get_meetings()
meetings = meetings_response if isinstance(meetings_response, list) else []
action_items = [item for meeting in meetings for item in meeting.get("action_items", [])]
decisions = [item for meeting in meetings for item in meeting.get("decisions", [])]
risks = [item for meeting in meetings for item in meeting.get("risks", [])]
open_questions = [question for meeting in meetings for question in (meeting.get("open_questions") or [])]
owners = sorted({item.get("owner") for item in action_items if item.get("owner")})

st.markdown(
    """
    <div style='border-radius:22px; padding:26px; background: linear-gradient(135deg, rgba(179,0,0,0.90), rgba(66,21,34,0.92));'>
        <h1 style='margin:0; color:#fff; letter-spacing:0.02em;'>MeetMind AI Dashboard</h1>
        <p style='margin:8px 0 0 0; color:rgba(255,255,255,0.84); font-size:17px;'>Enterprise-ready meeting minutes, action items, decisions, and risk insights — all connected to your FastAPI backend.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# MeetMind AI")
    st.markdown("### Navigation")
    st.markdown("- 📹 Upload Meeting")
    st.markdown("- 📋 View Minutes")
    st.markdown("- ✅ Action Items")
    st.markdown("- 📊 Dashboard")
    st.markdown("---")
    st.markdown("### API Status")
    if health_status.get("status") == "healthy":
        st.success("Backend Connected")
    else:
        st.error("Backend Disconnected")

    if health_status.get("database"):
        st.info(f"Database: {health_status.get('database')}")

st.markdown("---")

card_col1, card_col2, card_col3, card_col4 = st.columns(4)
with card_col1:
    info_card("Total Meetings", str(len(meetings)), "All uploaded and generated meetings", "#b30000")
with card_col2:
    info_card("Action Items", str(len(action_items)), "Tasks parsed from recent meetings", "#a3103a")
with card_col3:
    info_card("Decisions", str(len(decisions)), "Decisions captured from meeting notes", "#421522")
with card_col4:
    info_card("Risks & Questions", str(len(risks) + len(open_questions)), "Risks, dependencies, and open questions", "#99ab0f")

st.markdown("---")

st.markdown("### Meeting Analytics")
analytics_col1, analytics_col2 = st.columns([3, 2])
with analytics_col1:
    if meetings:
        st.markdown(
            """
            <div style='border-radius:24px; padding:24px; background:linear-gradient(135deg, rgba(179,0,0,0.18), rgba(66,21,34,0.12)); border: 1px solid rgba(255,255,255,0.08);'>
                <h3 style='margin:0; color:#fff;'>Recent Meeting Energy</h3>
                <p style='margin:8px 0 0; color:rgba(255,255,255,0.78);'>A sleek summary of your latest meeting capture trends.</p>
                <div style='margin-top:20px; height:12px; background:rgba(255,255,255,0.07); border-radius:999px; overflow:hidden;'>
                    <div style='width:90%; height:100%; background: linear-gradient(90deg, #b30000, #a3103a, #99ab0f); animation: slide 3.5s ease-in-out infinite;'></div>
                </div>
                <p style='margin:14px 0 0; color:rgba(255,255,255,0.66);'>Keep capturing notes to enrich your dashboard and unlock deeper insights.</p>
            </div>
            <style>
            @keyframes slide {
                0% { transform: translateX(-100%); }
                50% { transform: translateX(0); }
                100% { transform: translateX(100%); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style='border-radius:24px; padding:24px; background:rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);'>
                <h3 style='margin:0; color:#fff;'>No meetings yet</h3>
                <p style='margin:8px 0 0; color:rgba(255,255,255,0.66);'>Upload your first transcript to populate the dashboard and reveal analytics.</p>
                <div style='margin-top:20px; height:8px; background:rgba(255,255,255,0.07); border-radius:999px;'></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with analytics_col2:
    st.markdown("#### Quick Insights")
    st.write(f"**Owners engaged:** {len(owners)}")
    st.write(f"**AI health:** {health_status.get('status', 'unknown')}" )
    st.write(f"**Last sync:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}" )
    st.download_button(
        "Export History",
        json.dumps(meetings, default=str, indent=2),
        file_name="meetmind_meetings.json",
        mime="application/json",
    )

st.markdown("---")

st.markdown("### How to Use")
st.write(
    "1. Open **Upload Meeting** to paste notes or upload a transcript.\n"
    "2. After extraction, review minutes in **View Minutes**.\n"
    "3. Manage follow-ups in **Action Items** and track trends in **Dashboard**."
)
