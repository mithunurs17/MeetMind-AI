"""
1_Upload_Meeting.py
All UI is identical to the original. Auth-aware logic:
  - Logged-in users  → call /ai/extract  (unlimited)
  - Anonymous users  → call /trial/extract (one free attempt)
  - Trial exhausted  → show sign-up prompt
"""
import json
import streamlit as st
from utils.api_client import api_client
from utils.auth import is_logged_in
from utils.export import build_export_filename, create_meeting_docx, create_meeting_pdf
from utils.ui import apply_theme

st.set_page_config(page_title="Upload Meeting", page_icon="📹", layout="wide")
apply_theme()

# ── CSS (unchanged from original) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@300;400;500;600;700&display=swap');
:root{--bg:hsl(260,87%,3%);--fg:hsl(40,6%,95%);--sub:hsl(40,6%,72%);--accent:#6366f1;--accent2:#a855f7}
html,body,[class*="css"]{font-family:'Geist Sans',sans-serif!important;background:var(--bg)!important;color:var(--fg)!important}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:var(--bg)!important}
section[data-testid="stSidebar"]{background:hsl(260,70%,5%)!important;border-right:1px solid rgba(255,255,255,0.06)}
section[data-testid="stSidebar"] *{color:var(--fg)!important}
[data-testid="stSidebarCollapseButton"] button,[data-testid="collapsedControl"] button{background:linear-gradient(135deg,#6d28d9,#a855f7)!important;border:none!important;border-radius:50%!important;color:#fff!important;box-shadow:0 4px 14px rgba(168,85,247,0.45)!important}
[data-testid="stSidebarNavLink"]{border-radius:12px!important}
[data-testid="stSidebarNavLink"]:hover{background:rgba(168,85,247,0.18)!important}
[data-testid="stSidebarNavLink"][aria-selected="true"]{background:linear-gradient(135deg,#6d28d9,#a855f7)!important}
h1{color:var(--fg)!important;font-weight:700!important}
h2,h3{color:var(--fg)!important;font-weight:600!important}
[data-testid="stForm"]{background:rgba(255,255,255,0.03)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:20px!important;padding:28px!important;backdrop-filter:blur(14px)!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;color:var(--fg)!important;font-family:'Geist Sans',sans-serif!important}
label{color:var(--sub)!important;font-size:13px!important;font-weight:500!important;letter-spacing:.04em!important;text-transform:uppercase!important}
[data-testid="stFileUploader"]{background:rgba(255,255,255,0.03)!important;border:1px dashed rgba(255,255,255,0.15)!important;border-radius:14px!important}
[data-testid="stFileUploader"] button,[data-testid="baseButton-secondary"]{background:linear-gradient(135deg,#6d28d9,#a855f7)!important;border:none!important;border-radius:999px!important;color:#fff!important;font-weight:600!important}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border:1px solid rgba(255,255,255,0.14)!important;border-radius:999px!important;background:rgba(255,255,255,0.06)!important;color:var(--fg)!important;font-weight:500!important;padding:0.65rem 1.4rem!important;font-family:'Geist Sans',sans-serif!important;transition:all .2s!important}
.stButton>button:hover,.stDownloadButton>button:hover{background:rgba(99,102,241,0.22)!important;border-color:var(--accent)!important}
.stFormSubmitButton>button{background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;border:none!important;font-weight:600!important;font-size:15px!important;padding:0.75rem 2rem!important}
.stFormSubmitButton>button:hover{background:linear-gradient(135deg,#6366f1,#a855f7)!important}
[data-testid="stAlert"]{border-radius:14px!important;border:1px solid rgba(255,255,255,0.08)!important;background:rgba(255,255,255,0.04)!important}
hr{border-color:rgba(255,255,255,0.08)!important}
.glass-section{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px 24px;margin-bottom:16px}
.tips-box{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.22);border-radius:14px;padding:18px 22px;margin-top:24px}
.trial-banner{background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(168,85,247,0.08));border:1px solid rgba(99,102,241,0.28);border-radius:16px;padding:18px 24px;margin-bottom:20px}
.trial-used{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.3);border-radius:16px;padding:18px 24px;margin-bottom:20px}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# 📹 Upload Meeting")
st.markdown(
    "<p style='color:hsl(40,6%,72%);font-size:16px;margin-top:-8px;'>"
    "Use AI to extract meeting minutes, decisions, action items, risks, and open questions "
    "from transcript text or uploaded files.</p>",
    unsafe_allow_html=True,
)

# ── Trial / auth state ────────────────────────────────────────────────────
logged_in = is_logged_in()
trial_used = False

if not logged_in:
    status_resp = api_client.trial_status()
    trial_used = status_resp.get("trial_used", False)

    if trial_used:
        st.markdown(
            "<div class='trial-used'>"
            "<b style='font-size:15px;color:#fcd34d;'>⚠️ Free trial used</b><br/>"
            "<span style='color:hsl(40,6%,75%);font-size:14px;'>"
            "You've already used your one free extraction. "
            "Create a free account to get unlimited access.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.page_link("pages/0_Login.py", label="🔐 Sign In / Register", use_container_width=True)
        st.stop()
    else:
        st.markdown(
            "<div class='trial-banner'>"
            "<b style='font-size:15px;'>🎁 Free Trial</b> &nbsp;"
            "<span style='color:hsl(40,6%,72%);font-size:13px;'>"
            "You have <b style='color:#a5b4fc;'>1 free extraction</b> — no account needed. "
            "Register for unlimited access.</span>"
            "</div>",
            unsafe_allow_html=True,
        )

MAX_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_FILE_TYPES = ["txt", "pdf", "docx"]

# ── Form ──────────────────────────────────────────────────────────────────
with st.form(key="meeting_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        meeting_title = st.text_input("Meeting Title", placeholder="Enter meeting title")
        raw_text = st.text_area(
            "Paste meeting notes or transcript",
            placeholder="Paste the raw meeting transcript here...",
            height=260,
        )
    with col2:
        st.markdown("### Upload an optional file")
        uploaded_file = st.file_uploader(
            "Upload transcript or document",
            type=SUPPORTED_FILE_TYPES if logged_in else [],   # file upload needs account
            help="Supported formats: txt, pdf, docx",
            disabled=not logged_in,
        )
        if not logged_in:
            st.markdown(
                "<p style='color:hsl(40,6%,55%);font-size:12px;'>File upload requires an account.</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p style='color:hsl(40,6%,62%);font-size:12px;'>Upload TXT, PDF, or DOCX. Max 10 MB.</p>",
                unsafe_allow_html=True,
            )
    submit = st.form_submit_button(label="✨ Generate Meeting Minutes")


# ── Results renderer (unchanged) ──────────────────────────────────────────
def _render_results(result: dict, meeting_title: str) -> None:
    if result.get("error") or result.get("detail"):
        err = result.get("error") or result.get("detail")
        if "trial already used" in str(err).lower() or "free trial" in str(err).lower():
            st.warning(
                "⚠️ Free trial already used. "
                "[Sign in or register](pages/0_Login.py) to continue."
            )
        else:
            st.error(f"Unable to extract meeting minutes: {err}")
        return

    st.success("✅ Meeting minutes extracted successfully!")

    summary      = result.get("summary", "")
    decisions    = result.get("decisions") or []
    action_items = result.get("action_items") or []
    risks        = result.get("risks") or []
    questions    = result.get("open_questions") or []

    st.markdown("---")
    st.markdown("## Executive Summary")
    editable_summary = st.text_area("Editable executive summary", summary, height=170)

    st.markdown("## Decisions")
    decision_text = "\n".join([item.get("decision_text", str(item)) for item in decisions])
    editable_decisions = st.text_area("Editable decisions", decision_text, height=140)

    st.markdown("## Results Overview")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f"<div class='glass-section' style='text-align:center'><div style='font-size:36px;font-weight:700'>{len(action_items)}</div><div style='color:hsl(40,6%,62%);font-size:13px;'>Action Items</div></div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"<div class='glass-section' style='text-align:center'><div style='font-size:36px;font-weight:700'>{len(risks)}</div><div style='color:hsl(40,6%,62%);font-size:13px;'>Risks / Dependencies</div></div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"<div class='glass-section' style='text-align:center'><div style='font-size:36px;font-weight:700'>{len(questions)}</div><div style='color:hsl(40,6%,62%);font-size:13px;'>Open Questions</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Action Items")
    if action_items:
        for item in action_items:
            st.markdown(
                f"<div class='glass-section'><b>{item.get('task')}</b><br/>"
                f"<span style='color:hsl(40,6%,62%);font-size:13px;'>"
                f"Owner: <b style='color:var(--fg)'>{item.get('owner') or 'Unassigned'}</b> &nbsp;|&nbsp; "
                f"Due: <b style='color:var(--fg)'>{item.get('due_date') or 'TBD'}</b> &nbsp;|&nbsp; "
                f"Status: <b style='color:var(--fg)'>{item.get('status') or 'pending'}</b>"
                f"</span></div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No action items were found in this meeting.")

    st.markdown("### Risks & Dependencies")
    if risks:
        for risk in risks:
            text = risk.get("risk_text") if isinstance(risk, dict) else str(risk)
            st.markdown(f"<div class='glass-section' style='padding:12px 18px;'>• {text}</div>", unsafe_allow_html=True)
    else:
        st.info("No risks or dependencies were detected.")

    st.markdown("### Open Questions")
    if questions:
        for question in questions:
            st.markdown(f"<div class='glass-section' style='padding:12px 18px;'>• {question}</div>", unsafe_allow_html=True)
    else:
        st.info("No open questions were extracted.")

    # If trial user just used their free slot, prompt to register
    if not logged_in:
        st.markdown(
            "<div class='trial-used' style='margin-top:24px;'>"
            "<b style='color:#fcd34d;'>🎉 Trial extraction complete!</b><br/>"
            "<span style='color:hsl(40,6%,75%);font-size:14px;'>"
            "Create a free account to save your meetings and get unlimited extractions.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.page_link("pages/0_Login.py", label="🔐 Create Free Account", use_container_width=False)

    export_payload = {
        "title": meeting_title, "summary": editable_summary,
        "decisions": editable_decisions.splitlines(),
        "action_items": action_items, "risks": risks, "open_questions": questions,
    }
    pdf_name, timestamp = build_export_filename(meeting_title, "pdf")
    docx_name, _ = build_export_filename(meeting_title, "docx")
    pdf_bytes = create_meeting_pdf(
        title=meeting_title, summary=editable_summary,
        decisions=[l for l in editable_decisions.splitlines() if l.strip()],
        action_items=action_items, risks=risks, open_questions=questions,
        filename=pdf_name, timestamp=timestamp,
    )
    docx_bytes = create_meeting_docx(
        title=meeting_title, summary=editable_summary,
        decisions=[l for l in editable_decisions.splitlines() if l.strip()],
        action_items=action_items, risks=risks, open_questions=questions,
        filename=docx_name, timestamp=timestamp,
    )

    st.markdown("---")
    dl1, dl2, dl3, dl4 = st.columns(4)
    with dl1:
        st.download_button("📄 JSON", json.dumps(export_payload, default=str, indent=2),
                           file_name="meetmind_minutes.json", mime="application/json")
    with dl2:
        st.download_button("📝 Summary TXT", editable_summary,
                           file_name="meetmind_summary.txt", mime="text/plain")
    with dl3:
        st.download_button("📑 PDF", pdf_bytes, file_name=pdf_name, mime="application/pdf")
    with dl4:
        st.download_button("📃 DOCX", docx_bytes, file_name=docx_name,
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


# ── Submit logic ──────────────────────────────────────────────────────────
if submit:
    if not meeting_title:
        st.error("Please enter a meeting title.")
    elif not raw_text and not uploaded_file:
        st.error("Please paste transcript text or upload a supported file.")
    elif uploaded_file is not None and logged_in:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext not in SUPPORTED_FILE_TYPES:
            st.error("Unsupported file type. Please upload TXT, PDF, or DOCX.")
        elif uploaded_file.size > MAX_FILE_SIZE:
            st.error("File too large. Maximum upload size is 10 MB.")
        else:
            with st.spinner("✨ Generating structured meeting minutes..."):
                result = api_client.extract_meeting_from_file(meeting_title, uploaded_file)
            _render_results(result, meeting_title)
    else:
        # Text-based extraction — use trial endpoint for anonymous users
        with st.spinner("✨ Generating structured meeting minutes..."):
            if logged_in:
                result = api_client.extract_meeting_from_text(meeting_title, raw_text)
            else:
                result = api_client.trial_extract(meeting_title, raw_text)
        _render_results(result, meeting_title)

# ── Tips (unchanged) ──────────────────────────────────────────────────────
st.markdown(
    "<div class='tips-box'>"
    "<b style='font-size:15px;'>💡 Tips for better AI extraction</b><br/><br/>"
    "• Use structured speaker notes where possible.<br/>"
    "• Add meeting title and agenda items for more precise outcomes.<br/>"
    "• Review and edit the generated summary before sharing."
    "</div>",
    unsafe_allow_html=True,
)