import json
from datetime import datetime

import streamlit as st
from utils.api_client import api_client

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MeetMind AI Dashboard",
    page_icon="🧠",
    layout="wide",
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Hide Streamlit default menu */
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
        radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 25%),
        radial-gradient(circle at bottom right, rgba(236,72,153,0.15), transparent 25%),
        #0f172a;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #0f172a);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Hero Section */
.hero {
    position: relative;
    overflow: hidden;
    border-radius: 30px;
    padding: 50px;
    background:
        linear-gradient(
            135deg,
            rgba(79,70,229,0.95),
            rgba(124,58,237,0.90),
            rgba(236,72,153,0.85)
        );

    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
}

.hero h1 {
    font-size: 60px;
    margin-bottom: 10px;
    font-weight: 700;
    color: white;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
    max-width: 900px;
    color: white;
}

/* Glow */
.hero::before {
    content: "";
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: rgba(255,255,255,0.10);
    top: -200px;
    right: -100px;
    filter: blur(60px);
}

/* Metric Cards */
.metric-card {
    border-radius: 24px;
    padding: 25px;
    color: white;
    transition: 0.3s ease;
    box-shadow: 0 10px 30px rgba(0,0,0,0.30);
}

.metric-card:hover {
    transform: translateY(-5px);
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

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    transition: 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px);
}

/* Progress Bar */
.progress-bar {
    width: 100%;
    height: 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
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

    animation: move 3s infinite;
}

@keyframes move {
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
    border: none;
    border-radius: 14px;

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

</style>
""", unsafe_allow_html=True)

# =====================================================
# API DATA
# =====================================================
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

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.title("🧠 MeetMind AI")

    st.markdown("---")

    st.subheader("Navigation")

    st.markdown("""
- 📹 Upload Meeting
- 📋 View Minutes
- ✅ Action Items
- 📊 Dashboard
""")

    st.markdown("---")

    st.subheader("API Status")

    if health_status.get("status") == "healthy":
        st.success("Backend Connected")
    else:
        st.error("Backend Offline")

# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class="hero">

<h1>🧠 MeetMind AI</h1>

<p>
AI-powered meeting intelligence platform that transforms
transcripts into smart summaries, action items,
decisions, risks, and analytics in real time.
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# METRIC CARDS
# =====================================================
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
        "Key decisions captured",
        "linear-gradient(135deg,#f59e0b,#ef4444)"
    ),

    (
        "Risks & Questions",
        len(risks) + len(open_questions),
        "Pending blockers",
        "linear-gradient(135deg,#ec4899,#8b5cf6)"
    ),
]

for col, card in zip([col1, col2, col3, col4], cards):

    title, value, desc, gradient = card

    with col:

        st.markdown(f"""
        <div class="metric-card" style="background:{gradient};">

            <div class="metric-title">{title}</div>

            <div class="metric-value">{value}</div>

            <div class="metric-desc">{desc}</div>

        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# ANALYTICS
# =====================================================
left, right = st.columns([3, 1.4])

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
    analytics and productivity insights.
    </p>

    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown(f"""
    <div class="glass-card">

    <h3>⚡ Quick Insights</h3>

    <br>

    <p><b>👥 Owners Engaged:</b> {len(owners)}</p>

    <p><b>🟢 AI Health:</b> {health_status.get('status', 'unknown')}</p>

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

# =====================================================
# GETTING STARTED
# =====================================================
st.markdown("""
<div class="glass-card">

<h2>🚀 Getting Started</h2>

<br>

<p>1️⃣ Upload meeting transcripts or notes.</p>

<p>2️⃣ AI automatically extracts summaries,
action items, risks, and decisions.</p>

<p>3️⃣ Review analytics and collaborate with your team efficiently.</p>

</div>
""", unsafe_allow_html=True)