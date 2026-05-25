import streamlit as st

PALETTE = {
    "primary": "#b30000",
    "rich": "#a3103a",
    "dark": "#421522",
    "accent": "#99ab0f",
    "surface": "#12090f",
    "text": "#f5f5f5",
}


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top left, rgba(179,0,0,0.20), transparent 32%),
                        linear-gradient(180deg, #421522 0%, #0d0610 100%);
            color: {PALETTE['text']};
        }}

        .block-container {{
            padding: 1.8rem 2rem 2rem;
            background: rgba(10, 8, 14, 0.96) !important;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 22px 70px rgba(0, 0, 0, 0.25);
        }}

        .css-1d391kg, .css-1n8n4u7, .css-1g5fg8e, .css-1r6slb0, .css-1dx3gnn {{ background-color: rgba(255,255,255,0.04) !important; }}

        .stButton>button, .stDownloadButton>button, button {{
            border-radius: 14px !important;
            background-color: {PALETTE['primary']} !important;
            color: #fff !important;
            border: none !important;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18) !important;
        }}

        .stButton>button:hover, .stDownloadButton>button:hover, button:hover {{
            background-color: {PALETTE['rich']} !important;
        }}

        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div>select, .stDateInput>div>div>input {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: {PALETTE['text']} !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }}

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
            color: {PALETTE['accent']} !important;
        }}

        .stMarkdown p, .stMarkdown li, .stMarkdown div {{
            color: #e8e8e8 !important;
        }}

        .streamlit-expanderHeader {{
            color: {PALETTE['primary']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, value: str, caption: str, accent: str) -> None:
    st.markdown(
        f"""
        <div style="background: rgba(255,255,255,0.05); padding: 20px 22px; border-radius: 20px; border-left: 5px solid {accent}; min-height: 120px;">
            <div style="font-size: 13px; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.7); margin-bottom: 8px;">{title}</div>
            <div style="font-size: 34px; font-weight: 700; color: #ffffff; line-height: 1.1;">{value}</div>
            <div style="font-size: 13px; color: rgba(255,255,255,0.65); margin-top: 10px;">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
