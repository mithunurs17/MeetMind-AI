import json
from datetime import datetime

import streamlit as st
from utils.api_client import api_client

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="MeetMind AI Dashboard",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: #0f172a;
    color: white;
}

/* Hide Streamlit Branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Main Background */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(124,58,237,0.25), transparent 30%),
        radial-gradient(circle at bottom right, rgba(236,72,153,0.20), transparent 30%),
        #0f172a;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #0f172a);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Hero Section */
.hero {
    position: relative;
    overflow: hidden;
    padding: 45px;
    border-radius: 30px;
    background:
        linear-gradient(
            135deg,
            rgba(79,70,229,0.95),
            rgba(124,58,237,0.85),
            rgba(236,72,153,0.80)
        );
    box-shadow: 0 15px 45px rgba(0,0,0,0.45);
}

.hero h1 {
    font-size: 58px;
    margin-bottom: 10px;
    font-weight: 700;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
    max-width: 850px;
}

/* Floating Glow */
.hero::before {
    content: "";
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
    top: -180px;
    right: -100px;
    filter: blur(60px);
}

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    border-radius: 25px;
    padding: 28px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    transition: 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px);
}

/* Metric Cards */
.metric-card {
    padding: 25px;
    border-radius: 25px;
    color: white;
    transition: 0.3s ease;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

.metric-card:hover {
    transform: scale(1.03);
}

.metric-title {
    font-size: 15px;
    opacity: 0.85;
}

.metric-value {
    font-size: 42px;
    font-weight: 700;
    margin-top: 10px;
}

.metric-desc {
    margin-top: 8px;
    font-size: 13px;
    opacity: 0.75;
}

/* Progress Bar */
.progress-bar {
    width: 100%;
    height: 14px;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(255,255,255,0.08);
}

.progress-fill {
    width: 70%;
    height: 100%;
    background:
        linear-gradient(
            90deg,
            #06b6d4,
            #8b5cf6,
            #ec4899
        );
    animation: loading 3s infinite;
}

@keyframes loading {
    0% {
        transform: translateX(-40%);
    }

    100% {
        transform: translateX(100%);
    }
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {

    width: 100%;
    border-radius: 14px;
    border: none;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );

    color: white;
    font-weight: 600;
    padding: 0.7rem 1rem;

    transition: 0.3s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: scale(1.03);
}

/* Text */
h1, h2, h3, h4 {
    color: white;
}

p {
    color: rgba(255,255,255,0.82);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API CALLS
# ---------------------------------------------------
health_status = api_client.health_check()

meetings_response = api_client.get_meetings()

meetings = meetings_response if isinstance(meetings_response, list) else []

action_items = [
    item
    for meeting in meetings
    for item in meeting.get("action_items", [])
]

decisions = [
    item
    for meeting in meetings
    for item in meeting.get("decisions", [])
]

risks = [
    item
    for meeting in meetings
    for item in meeting.get("risks", [])
]

open_questions = [
    q
    for meeting in meetings
    for q in (meeting.get("open_questions") or [])
]

owners = sorted({
    item.get("owner")
    for item in action_items
    if item.get("owner")
})

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.markdown("## 🧠 MeetMind AI")

    st.markdown("---")

    st.markdown("### Navigation")

    st.markdown("""
- 📹 Upload Meeting  
- 📋 View Minutes  
- ✅ Action Items  
- 📊 Dashboard  
""")

    st.markdown("---")

    st.markdown("### System Status")

    if health_status.get("status") == "healthy":
        st.success("Backend Connected")
    else:
        st.error("Backend Offline")

    if health_status.get("database"):
        st.info(f"Database: {health_status.get('database')}")

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------
st.markdown("""
<div class="hero">

    <h1>🧠 MeetMind AI</h1>

    <p>
        AI-powered meeting intelligence dashboard that transforms
        meeting transcripts into actionable insights, decisions,
        risks, summaries, and analytics in real-time.
    </p>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# METRIC CARDS
# ---------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

cards = [
    (
        "Total Meetings",
        len(meetings),
        "Meetings analyzed",
        "linear-gradient(135deg,#4f46e5,#7c3aed)"
    ),

    (
        "Action Items",
        len(action_items),
        "Tasks extracted",
        "linear-gradient(135deg,#06b6d4,#3b82f6)"
    ),

    (
        "Decisions",
        len(decisions),
        "Critical decisions captured",
        "linear-gradient(135deg,#f59e0b,#ef4444)"
    ),

    (
        "Risks & Questions",
        len(risks) + len(open_questions),
        "Pending blockers & doubts",
        "linear-gradient(135deg,#ec4899,#8b5cf6)"
    ),
]

for col, card in zip([col1, col2, col3, col4], cards):

    title, value, desc, gradient = card

    with col:

        st.markdown(f"""
        <div class="metric-card"
             style="background:{gradient};">

            <div class="metric-title">
                {title}
            </div>

            <div class="metric-value">
                {value}
            </div>

            <div class="metric-desc">
                {desc}
            </div>

        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# ANALYTICS SECTION
# ---------------------------------------------------
left, right = st.columns([3, 1.5])

# LEFT SIDE
with left:

    st.markdown("""
    <div class="glass-card">

        <h2>📈 Meeting Analytics</h2>

        <p style="opacity:0.8;">
            Visualize collaboration efficiency and meeting insights
            in real-time using AI-powered analysis.
        </p>

        <br>

        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>

        <br>

        <p style="opacity:0.7;">
            Keep uploading meeting transcripts to unlock richer
            analytics and team productivity insights.
        </p>

    </div>
    """, unsafe_allow_html=True)

# RIGHT SIDE
with right:

    st.markdown(f"""
    <div class="glass-card">

        <h3>⚡ Quick Insights</h3>

        <br>

        <p><b>👥 Owners Engaged:</b> {len(owners)}</p>

        <p><b>🟢 AI Health:</b> {health_status.get('status','unknown')}</p>

        <p><b>🕒 Last Sync:</b><br>
        {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.download_button(
        "⬇ Export Meetings JSON",
        json.dumps(meetings, default=str, indent=2),
        file_name="meetmind_export.json",
        mime="application/json",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# GETTING STARTED
# ---------------------------------------------------
st.markdown("""
<div class="glass-card">

    <h2>🚀 Getting Started</h2>

    <br>

    <p>
        1️⃣ Upload meeting transcripts or notes.
    </p>

    <p>
        2️⃣ AI automatically extracts minutes, action items,
        risks, and decisions.
    </p>

    <p>
        3️⃣ Review analytics and collaborate with your team
        efficiently.
    </p>

</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
