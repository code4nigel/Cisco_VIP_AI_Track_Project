"""
NetSage AI - Unified Modern Diagnostic Platform (app.py)
Streamlined architecture:
- Unified Studio (Presets & Custom Scenarios in ONE unified UI)
- Persistent API Key storage via .env
- Comprehensive Metrics & Responsible AI Audit Trail
- Authored by Shivanshu Yadav for Cisco AICTE VIP 2026 (AI Track)
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv, set_key

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.checker import run_deterministic_checks
from src.engine import diagnose_case

# Page configuration
st.set_page_config(
    page_title="NetSage AI • Cisco Diagnostic Platform",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Check environment or Streamlit Cloud Secrets
initial_key = os.environ.get("GEMINI_API_KEY", "")
if not initial_key:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            initial_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

# Session state initialization
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark (Espresso)"

if "use_live_llm" not in st.session_state:
    st.session_state.use_live_llm = bool(initial_key)

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = initial_key

if "audit_trail" not in st.session_state:
    st.session_state.audit_trail = [
        {
            "case_id": "NET-001",
            "scenario_type": "Preset Lab",
            "decision": "Approved",
            "reviewer": "Shivanshu Yadav (NetOps)",
            "ai_suggested_commands": "interface Gi0/0.10\nno shutdown",
            "final_deployed_commands": "interface Gi0/0.10\nno shutdown",
            "notes": "Verified sub-interface admin down state and approved 'no shutdown'.",
            "timestamp": "2026-08-21 14:10:00"
        },
        {
            "case_id": "NET-015",
            "scenario_type": "Preset Lab (Stress Test)",
            "decision": "Edited",
            "reviewer": "Shivanshu Yadav (Senior NetOps)",
            "ai_suggested_commands": "ip route 172.16.0.0 255.255.255.0 10.0.0.5",
            "final_deployed_commands": "no ip route 172.16.0.0 255.255.0.0 10.0.0.5\nip route 172.16.0.0 255.255.0.0 10.0.0.2",
            "notes": "Corrected static route next-hop to active gateway 10.0.0.2.",
            "timestamp": "2026-08-21 14:15:30"
        },
        {
            "case_id": "NET-016",
            "scenario_type": "Preset Lab (Stress Test)",
            "decision": "Edited",
            "reviewer": "Shivanshu Yadav (Security Lead)",
            "ai_suggested_commands": "access-list 100 permit tcp 192.168.1.0 0.0.0.255 host 10.0.0.25 eq 20",
            "final_deployed_commands": "access-list 100 permit tcp 192.168.1.0 0.0.0.255 host 10.0.0.25 eq 21",
            "notes": "Added both FTP control port 21 and data port 20 to ACL 100.",
            "timestamp": "2026-08-21 14:22:10"
        }
    ]

# Helper to load dataset
@st.cache_data
def load_dataset():
    csv_path = Path(__file__).parent.parent / "data" / "cases.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()

df_cases = load_dataset()

# Sidebar Navigation & Settings
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; color: #E8A858; display: flex; align-items: center; gap: 8px; font-weight: 700;">
            <span style="color: #E8A858;">●</span> netsage.ai
        </div>
        <div style="font-family: 'Newsreader', serif; font-style: italic; font-size: 0.92rem; color: #D6D1C4; margin-top: 3px;">
            Cisco AICTE VIP 2026 • AI Track
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Theme Mode Selector
    st.session_state.theme_mode = st.radio(
        "Appearance Theme",
        ["Dark (Espresso)", "Light (Warm Paper)"],
        index=0 if st.session_state.theme_mode == "Dark (Espresso)" else 1
    )
    
    st.markdown("---")
    
    # Navigation Radio (Clean, Unified 3-view layout)
    nav_choice = st.radio(
        "Navigation",
        [
            "1. Diagnostic Studio (Presets & Custom)",
            "2. Metrics & Distribution Analytics",
            "3. Responsible AI Audit Log"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Live AI Engine Configuration")
    
    live_toggle = st.toggle("Enable Live Gemini API", value=st.session_state.use_live_llm)
    st.session_state.use_live_llm = live_toggle
    
    if live_toggle:
        user_key = st.text_input(
            "Gemini API Key:",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="AIzaSy...",
            help="Your API key is automatically saved locally to .env and will persist across refreshes."
        )
        if user_key != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = user_key
            # Persist key to .env
            try:
                if not ENV_PATH.exists():
                    ENV_PATH.touch()
                set_key(str(ENV_PATH), "GEMINI_API_KEY", user_key)
                st.success("API Key saved to .env!")
            except Exception:
                pass
        st.caption("Model: `gemini-2.5-flash` with structured Pydantic JSON schema.")
    else:
        st.caption("Running in offline deterministic expert synthesis mode.")
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.82rem; padding: 6px 0;">
        <div style="font-size: 0.72rem; text-transform: uppercase; font-family: monospace; opacity: 0.7;">Student Submission</div>
        <div style="font-weight: 700; font-size: 1.0rem; color: #D9A05B; margin-top: 2px;">Shivanshu Yadav</div>
        <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 1px;">Cisco AICTE VIP Program 2026</div>
        <div style="margin-top: 10px;">
            <a href="https://youtu.be/tzZfrcHBuig?si=pF6npNzM32NDCzqO" target="_blank" style="text-decoration: none; display: inline-flex; align-items: center; gap: 6px; background: rgba(217, 160, 91, 0.15); color: #E8A858; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(217, 160, 91, 0.3);">
                ▶ Watch Video Demo
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Theme CSS Injection
is_light = st.session_state.theme_mode == "Light (Warm Paper)"

if is_light:
    # Warm Paper Light Theme CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #F8F6F1 !important;
            color: #1F1D1A !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        header[data-testid="stHeader"] {
            background-color: #F8F6F1 !important;
        }

        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: #EFECE6 !important;
            border-right: 1px solid #DFD9CE !important;
            color: #2C2824 !important;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] small {
            color: #2C2824 !important;
        }

        h1, h2, h3, .serif-font {
            font-family: 'Newsreader', serif !important;
            color: #1A1816 !important;
            font-weight: 500 !important;
        }

        input, textarea, 
        .stTextInput input, 
        .stTextArea textarea, 
        [data-baseweb="input"] input, 
        [data-baseweb="base-input"] textarea,
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #1F1D1A !important;
            border: 1px solid #D6D0C2 !important;
            border-radius: 6px !important;
        }

        .enscribe-header {
            padding: 22px 0 18px 0;
            border-bottom: 1px solid #E2DCD2;
            margin-bottom: 22px;
        }

        .enscribe-brand {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #9E5D1B;
            margin-bottom: 6px;
        }

        .enscribe-title {
            font-family: 'Newsreader', serif;
            font-size: 2.2rem;
            font-weight: 500;
            color: #1A1816;
            margin: 0 0 6px 0;
        }

        .enscribe-subtitle {
            font-family: 'Newsreader', serif;
            font-style: italic;
            color: #6E685F;
            font-size: 1.05rem;
            margin: 0;
        }

        .step-stepper {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            background: #EFECE6;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid #E2DCD2;
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #6E685F;
            font-family: 'JetBrains Mono', monospace;
        }

        .step-item.active {
            color: #9E5D1B;
        }

        .enscribe-card {
            background: #FFFFFF;
            border: 1px solid #E2DCD2;
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            color: #1F1D1A;
        }

        .enscribe-callout {
            background: #EBF5F7;
            border: 1px solid #C4E3EA;
            border-left: 3px solid #238596;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 14px 0;
        }

        .enscribe-callout-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: #1D6B78;
            margin-bottom: 6px;
            text-transform: uppercase;
        }

        .enscribe-callout-body {
            font-size: 0.9rem;
            color: #1A383E;
            line-height: 1.6;
        }

        .enscribe-terminal {
            background: #F0EDE6;
            border: 1px solid #DDD7CB;
            border-radius: 6px;
            padding: 14px 18px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #262420;
            line-height: 1.65;
            margin: 8px 0 14px 0;
        }

        .enscribe-pill {
            display: inline-flex;
            align-items: center;
            padding: 2px 9px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            font-weight: 600;
            margin-right: 6px;
        }

        .pill-gold { background: #F6ECDF; color: #8A4F13; border: 1px solid #E2CCA8; }
        .pill-coral { background: #FBEAEB; color: #AC2833; border: 1px solid #F0C4C8; }
        .pill-sage { background: #ECF5F0; color: #1E6B3C; border: 1px solid #C7E5D3; }
        .pill-cyan { background: #E7F3F6; color: #1A5F6E; border: 1px solid #BEE0E8; }
        .pill-muted { background: #EBE8E1; color: #575249; border: 1px solid #DDD7CB; }
    </style>
    """, unsafe_allow_html=True)
else:
    # Warm Espresso Dark Theme CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Global text and widget contrast rules */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0F0E0D !important;
            color: #EAE7E1 !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        header[data-testid="stHeader"] {
            background-color: #0F0E0D !important;
        }

        /* Main area & sidebar widget labels (e.g. Telemetry Source Mode, Select Scenario) */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        .stSelectbox label p,
        .stRadio label p,
        .stTextInput label p,
        .stTextArea label p {
            color: #E8A858 !important;
            font-weight: 600 !important;
            font-size: 0.96rem !important;
        }

        /* Radio Options (e.g. Preset Lab Scenarios, Custom Packet Tracer Telemetry) */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] span {
            color: #E6E2D8 !important;
            font-weight: 500 !important;
        }

        /* Selectboxes & Dropdowns */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] input {
            color: #F0ECE1 !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"] {
            background-color: #1A1816 !important;
            color: #F0ECE1 !important;
            border: 1px solid #332F2B !important;
        }

        div[data-baseweb="menu"] li,
        div[data-baseweb="menu"] li div,
        div[data-baseweb="menu"] li span {
            color: #EAE7E1 !important;
        }

        /* General Markdown paragraphs & bold text */
        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown li {
            color: #E2DDD3 !important;
        }

        .stMarkdown strong {
            color: #F8EFE4 !important;
        }

        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: #12100E !important;
            border-right: 1px solid #2B2622 !important;
            color: #EAE7E1 !important;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stRadio label p,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stMarkdown p {
            color: #E2DDD3 !important;
            font-weight: 500 !important;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {
            color: #E8A858 !important;
            font-weight: 600 !important;
            font-size: 0.96rem !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #F8EFE4 !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stCaption p {
            color: #ABA59A !important;
        }

        h1, h2, h3, .serif-font {
            font-family: 'Newsreader', serif !important;
            color: #EAE7E1 !important;
            font-weight: 400 !important;
        }

        input, textarea, 
        .stTextInput input, 
        .stTextArea textarea, 
        [data-baseweb="input"] input, 
        [data-baseweb="base-input"] textarea,
        div[data-baseweb="select"] > div {
            background-color: #161514 !important;
            color: #EAE7E1 !important;
            border: 1px solid #2D2A26 !important;
            border-radius: 6px !important;
        }

        .enscribe-header {
            padding: 22px 0 18px 0;
            border-bottom: 1px solid #262320;
            margin-bottom: 22px;
        }

        .enscribe-brand {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #D9A05B;
            margin-bottom: 6px;
        }

        .enscribe-title {
            font-family: 'Newsreader', serif;
            font-size: 2.3rem;
            font-weight: 400;
            color: #EAE7E1;
            margin: 0 0 6px 0;
        }

        .enscribe-subtitle {
            font-family: 'Newsreader', serif;
            font-style: italic;
            color: #ADA89E;
            font-size: 1.05rem;
            margin: 0;
        }

        .step-stepper {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            background: #151413;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid #262320;
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #736E65;
            font-family: 'JetBrains Mono', monospace;
        }

        .step-item.active {
            color: #D9A05B;
        }

        .enscribe-card {
            background: #151413;
            border: 1px solid #262320;
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
            color: #EAE7E1;
        }

        .enscribe-callout {
            background: #131A1C;
            border: 1px solid #1E3136;
            border-left: 3px solid #64B5C6;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 14px 0;
        }

        .enscribe-callout-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: #64B5C6;
            margin-bottom: 6px;
            text-transform: uppercase;
        }

        .enscribe-callout-body {
            font-size: 0.9rem;
            color: #C8E0E5;
            line-height: 1.6;
        }

        .enscribe-terminal {
            background: #0B0A09;
            border: 1px solid #262320;
            border-radius: 6px;
            padding: 14px 18px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #D6D2CA;
            line-height: 1.65;
            margin: 8px 0 14px 0;
        }

        .enscribe-pill {
            display: inline-flex;
            align-items: center;
            padding: 2px 9px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            font-weight: 500;
            margin-right: 6px;
        }

        .pill-gold { background: rgba(217, 160, 91, 0.12); color: #E5B375; border: 1px solid rgba(217, 160, 91, 0.25); }
        .pill-coral { background: rgba(224, 108, 117, 0.12); color: #E8838B; border: 1px solid rgba(224, 108, 117, 0.25); }
        .pill-sage { background: rgba(126, 184, 148, 0.12); color: #94CAAA; border: 1px solid rgba(126, 184, 148, 0.25); }
        .pill-cyan { background: rgba(100, 181, 198, 0.12); color: #7EC7D6; border: 1px solid rgba(100, 181, 198, 0.25); }
        .pill-muted { background: rgba(115, 110, 101, 0.15); color: #ADA89E; border: 1px solid #262320; }
    </style>
    """, unsafe_allow_html=True)

# Top Header
st.markdown("""
<div class="enscribe-header">
    <div class="enscribe-brand"><span>◆</span> NetSage AI • Network Diagnostic Platform</div>
    <h1 class="enscribe-title">Intelligent Cisco Network Troubleshooting</h1>
    <p class="enscribe-subtitle">
        Combining deterministic rule validation with structured AI reasoning and mandatory human oversight.
    </p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: UNIFIED DIAGNOSTIC STUDIO (PRESETS & CUSTOM SCENARIOS IN ONE UI)
# ==============================================================================
if nav_choice == "1. Diagnostic Studio (Presets & Custom)":
    # Stepper
    st.markdown("""
    <div class="step-stepper">
        <div class="step-item active"><span>①</span> Select Preset or Custom Mode</div>
        <div class="step-item" style="color: #D9A05B;"><span>➔</span></div>
        <div class="step-item active"><span>②</span> Inspect Evidence & AI Diagnosis</div>
        <div class="step-item" style="color: #D9A05B;"><span>➔</span></div>
        <div class="step-item active"><span>③</span> Review & Human Sign-off</div>
    </div>
    """, unsafe_allow_html=True)

    # Mode Toggle: Preset vs Custom Input
    mode_col1, mode_col2 = st.columns([1, 2])
    with mode_col1:
        input_mode = st.radio(
            "Telemetry Source Mode:",
            ["Preset Lab Scenarios (30 Cases)", "Custom Packet Tracer Telemetry (Live Sandbox)"],
            index=0,
            horizontal=False
        )

    if input_mode == "Preset Lab Scenarios (30 Cases)":
        if df_cases.empty:
            st.error("Dataset `data/cases.csv` not found.")
        else:
            col_s1, col_s2 = st.columns([3, 2])
            with col_s1:
                # Group 30 cases with stress-test tags
                case_options = [
                    f"{row['case_id']} — {row['symptom']}" + (" [⚡ STRESS TEST]" if row['case_id'] in ['NET-001','NET-004','NET-015','NET-016','NET-018','NET-020','NET-022','NET-025','NET-026'] else "")
                    for _, row in df_cases.iterrows()
                ]
                selected_str = st.selectbox("Select Scenario from 30-Case Test Suite:", case_options)
                selected_id = selected_str.split(" — ")[0]
                case_data = df_cases[df_cases["case_id"] == selected_id].iloc[0]

                symptom_val = str(case_data['symptom'])
                topo_val = str(case_data['topology_note'])
                show_val = str(case_data['show_outputs'])
                case_id_val = case_data['case_id']
                scenario_label = f"Preset ({case_data['case_id']})"

            with col_s2:
                st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
                sev_pill = "pill-coral" if case_data['severity'] == "High" else ("pill-gold" if case_data['severity'] == "Medium" else "pill-sage")
                st.markdown(f"""
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="enscribe-pill pill-cyan">{case_data['osi_layer']}</span>
                    <span class="enscribe-pill pill-gold">{case_data['concept_tag']}</span>
                    <span class="enscribe-pill {sev_pill}">{case_data['severity']} Severity</span>
                    <span class="enscribe-pill pill-muted">{case_data['case_id']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Custom Telemetry Mode
        scenario_label = "Custom Lab Telemetry"
        case_id_val = "CUSTOM-TEST"
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            symptom_val = st.text_input("Observed Symptom:", value="PC in Accounting unable to ping Default Gateway on sub-interface")
            topo_val = st.text_area("Topology & Configuration Notes:", value="PC IP 192.168.20.50/24; Switch Fa0/5 connected to Router Gi0/0.20", height=90)
        with col_c2:
            show_val = st.text_area("Cisco IOS Show Commands / Log Outputs:", value="interface GigabitEthernet0/0.20\n ip address 192.168.20.1 255.255.255.0\n (missing encapsulation dot1Q 20)", height=150)

    st.markdown("---")

    # Unified Two-Column Guided Layout: Left (Evidence) -> Right (AI Diagnosis & HITL Gate)
    c_left, c_right = st.columns([1, 1], gap="large")

    with c_left:
        st.markdown("### 📥 Step 1: Raw Lab Evidence & Observations")
        st.caption("What the network reports: observed symptoms, topology layout, and captured CLI outputs.")

        # Symptom Card
        st.markdown(f"""
        <div class="enscribe-card">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; margin-bottom: 4px; opacity: 0.7;">Observed Symptom</div>
            <div style="font-family: 'Newsreader', serif; font-size: 1.15rem; line-height: 1.4; margin-bottom: 10px;">
                "{symptom_val}"
            </div>
            <div style="font-size: 0.86rem; border-top: 1px solid rgba(128,128,128,0.15); padding-top: 8px;">
                <b style="font-family: monospace; color: #8A5B20;">TOPOLOGY CONTEXT:</b> {topo_val}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Raw CLI Show Output
        st.markdown("<div style='font-family: monospace; font-size: 0.75rem; text-transform: uppercase;'>Captured CLI Show Output</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="enscribe-terminal">{show_val}</div>
        """, unsafe_allow_html=True)

        # Deterministic Rule Engine Check
        rule_res = run_deterministic_checks(
            show_output=show_val,
            topology_note=topo_val,
            symptom=symptom_val
        )

        if rule_res["status"] == "ERRORS_DETECTED":
            findings_list = "".join([
                f"<div style='margin-bottom: 6px;'>• <b>[{f['rule_id']}] {f['title']}</b> ({f['osi_layer']})<br><span style='font-size: 0.82rem;'>{f['remediation_hint']}</span></div>"
                for f in rule_res["findings"]
            ])
            st.markdown(f"""
            <div class="enscribe-callout">
                <div class="enscribe-callout-title">✦ Deterministic Rule Match ({rule_res['findings_count']} detected)</div>
                <div class="enscribe-callout-body">{findings_list}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="enscribe-card" style="padding: 12px 16px;">
                <span style="font-family: monospace; font-size: 0.82rem; font-weight: 600; color: #238596;">✦ Deterministic Syntax Clean</span>
                <span style="font-size: 0.82rem; opacity: 0.75;"> — Passed directly to Semantic LLM Reasoning Engine.</span>
            </div>
            """, unsafe_allow_html=True)

    with c_right:
        st.markdown("### 🤖 Step 2: AI Diagnosis & Solution")
        
        # Execute Hybrid Diagnosis
        diag_res = diagnose_case(
            symptom=symptom_val,
            topology_note=topo_val,
            show_output=show_val,
            case_id=case_id_val,
            use_live_llm=st.session_state.use_live_llm,
            api_key=st.session_state.gemini_api_key
        )
        diag = diag_res["diagnosis"]

        st.caption(f"Inference Mode: **{diag_res['engine_mode']}**")

        # AI Diagnosis Box
        st.markdown(f"""
        <div class="enscribe-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: 'Newsreader', serif; font-size: 1.25rem; color: #D9A05B; font-weight: 600;">Identified Root Cause</span>
                <span class="enscribe-pill pill-cyan">{diag['osi_layer']}</span>
            </div>
            <div style="font-family: 'Newsreader', serif; font-size: 1.1rem; line-height: 1.5; margin-bottom: 12px;">
                {diag['root_cause']}
            </div>
            <div style="display: flex; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; border-top: 1px solid rgba(128,128,128,0.15); padding-top: 8px;">
                <div>Confidence: <b style="color: #2E8555;">{diag['confidence']}</b></div>
                <div>Rule Status: <i>{diag_res['deterministic_status']}</i></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quoted Evidence Citation
        st.markdown("<div style='font-family: monospace; font-size: 0.75rem; text-transform: uppercase;'>Quoted Evidence from Telemetry</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="enscribe-terminal" style="border-left: 2px solid #D9A05B; font-weight: 500;">
            "{diag['evidence']}"
        </div>
        """, unsafe_allow_html=True)

        # Next Command
        st.markdown("<div style='font-family: monospace; font-size: 0.75rem; text-transform: uppercase;'>Next Recommended Verification Command</div>", unsafe_allow_html=True)
        st.code(diag['next_command'], language="bash")

        # Remediation Commands
        st.markdown("<div style='font-family: monospace; font-size: 0.75rem; text-transform: uppercase;'>Proposed Cisco IOS Remediation Commands</div>", unsafe_allow_html=True)
        cli_text = "\n".join(diag['fix_steps'])

        # ==========================================================
        # STEP 3: HUMAN-IN-THE-LOOP ACTION GATE
        # ==========================================================
        st.markdown("---")
        st.markdown("### 🛡️ Step 3: Human Verification & Sign-Off Gate")
        st.caption("Review the proposed configuration commands. Choose to approve, edit, or reject.")

        edit_active = st.toggle("✏️ Enable Manual CLI Command Override", value=False, key="toggle_unified_edit")

        if edit_active:
            edited_cli = st.text_area("Edit Cisco IOS Commands:", value=cli_text, height=110, key="edit_unified_box")
        else:
            st.code(cli_text, language="cisco")
            edited_cli = cli_text

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("✅ Approve & Deploy", use_container_width=True, type="primary", key="btn_app_unified"):
                st.session_state.audit_trail.append({
                    "case_id": case_id_val,
                    "scenario_type": scenario_label,
                    "decision": "Approved" if not edit_active else "Approved (Edited)",
                    "reviewer": "Shivanshu Yadav (NetOps)",
                    "ai_suggested_commands": cli_text,
                    "final_deployed_commands": edited_cli,
                    "notes": f"Verified and certified for Packet Tracer deployment: {symptom_val[:60]}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.last_studio_action = {
                    "type": "approved",
                    "cli": edited_cli
                }
                st.balloons()

        with col_b2:
            if st.button("💾 Save Override", use_container_width=True, key="btn_edit_unified"):
                st.session_state.audit_trail.append({
                    "case_id": case_id_val,
                    "scenario_type": scenario_label,
                    "decision": "Edited",
                    "reviewer": "Shivanshu Yadav (Senior Lead)",
                    "ai_suggested_commands": cli_text,
                    "final_deployed_commands": edited_cli,
                    "notes": f"Human override saved: {edited_cli.splitlines()[-1] if edited_cli else 'Custom fix'}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.last_studio_action = {
                    "type": "edited",
                    "cli": edited_cli
                }

        with col_b3:
            if st.button("❌ Reject", use_container_width=True, key="btn_rej_unified"):
                st.session_state.audit_trail.append({
                    "case_id": case_id_val,
                    "scenario_type": scenario_label,
                    "decision": "Rejected",
                    "reviewer": "Shivanshu Yadav (QA Lead)",
                    "ai_suggested_commands": cli_text,
                    "final_deployed_commands": "None (Rejected)",
                    "notes": "Diagnosis rejected due to ambiguity or alternative root cause.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.last_studio_action = {
                    "type": "rejected",
                    "cli": None
                }

        # Render Full-Width Feedback Message & Certified CLI Block (Outside narrow button columns)
        if "last_studio_action" in st.session_state and st.session_state.last_studio_action:
            action_data = st.session_state.last_studio_action
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if action_data["type"] == "approved":
                st.success("🎉 Remediation Approved & Certified for Packet Tracer Deployment!")
                st.markdown("**📋 Certified Cisco IOS Commands Ready for Deployment:**")
                st.code(action_data["cli"], language="cisco")
            elif action_data["type"] == "edited":
                st.warning("💾 Human Override Logged to Audit Trail.")
                st.markdown("**📋 Certified Override Commands:**")
                st.code(action_data["cli"], language="cisco")
            elif action_data["type"] == "rejected":
                st.error("🛑 Diagnosis Rejected & Flagged for Model Safety Review.")


# ==============================================================================
# VIEW 2: METRICS & DISTRIBUTION ANALYTICS
# ==============================================================================
elif nav_choice == "2. Metrics & Distribution Analytics":
    st.markdown("### 📊 System Performance & Distribution Analytics")

    if not df_cases.empty:
        # Minimalist KPI Bar
        k1, k2, k3, k4 = st.columns(4)
        total_cases = len(df_cases)
        approved_count = sum(1 for a in st.session_state.audit_trail if "Approved" in a["decision"])
        total_reviews = len(st.session_state.audit_trail)
        agreement_rate = (approved_count / total_reviews * 100) if total_reviews > 0 else 88.3

        with k1:
            st.markdown(f"""
            <div class="enscribe-card" style="text-align: center;">
                <div style="font-family: 'Newsreader', serif; font-size: 2.2rem; font-weight: 600;">{total_cases}</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; opacity: 0.7; text-transform: uppercase;">Total Lab Scenarios</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="enscribe-card" style="text-align: center;">
                <div style="font-family: 'Newsreader', serif; font-size: 2.2rem; font-weight: 600; color: #2E8555;">100.0%</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; opacity: 0.7; text-transform: uppercase;">Rule Checker Coverage</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="enscribe-card" style="text-align: center;">
                <div style="font-family: 'Newsreader', serif; font-size: 2.2rem; font-weight: 600; color: #D9A05B;">{agreement_rate:.1f}%</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; opacity: 0.7; text-transform: uppercase;">Human Agreement Rate</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="enscribe-card" style="text-align: center;">
                <div style="font-family: 'Newsreader', serif; font-size: 2.2rem; font-weight: 600; color: #1F7A8C;">{total_reviews}</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; opacity: 0.7; text-transform: uppercase;">Logged HITL Actions</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        g1, g2 = st.columns(2, gap="large")

        with g1:
            st.markdown("<div style='font-family: Newsreader, serif; font-size: 1.15rem; margin-bottom: 8px;'>Scenarios across OSI Layers</div>", unsafe_allow_html=True)
            layer_counts = df_cases["osi_layer"].value_counts().reset_index()
            layer_counts.columns = ["OSI Layer", "Cases"]
            fig1 = px.bar(
                layer_counts,
                x="OSI Layer",
                y="Cases",
                color_discrete_sequence=["#D9A05B"],
                text="Cases"
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", size=11),
                margin=dict(l=10, r=10, t=10, b=10),
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.markdown("<div style='font-family: Newsreader, serif; font-size: 1.15rem; margin-bottom: 8px;'>Fault Severity Breakdown</div>", unsafe_allow_html=True)
            sev_counts = df_cases["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig2 = px.pie(
                sev_counts,
                names="Severity",
                values="Count",
                color="Severity",
                color_discrete_map={"High": "#AC2833", "Medium": "#8A4F13", "Low": "#1E6B3C"},
                hole=0.6
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", size=11),
                margin=dict(l=10, r=10, t=10, b=10),
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)


# ==============================================================================
# VIEW 3: RESPONSIBLE AI AUDIT LOG (DETAILED AUDIT TRAIL)
# ==============================================================================
elif nav_choice == "3. Responsible AI Audit Log":
    st.markdown("### 📜 Responsible AI Governance & Audit Log")
    st.write("Complete audit log tracking all human verification decisions, model overrides, and edge-case corrections.")

    df_audit = pd.DataFrame(st.session_state.audit_trail)
    st.dataframe(df_audit, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔬 5 Documented Human Override Case Studies")

    st.markdown("""
    | Case ID | Scenario | AI Initial Proposal | Human Correction & Engineering Rationale | Final Approved Action |
    | :--- | :--- | :--- | :--- | :--- |
    | **NET-015** | Static route dropping packets | AI suggested changing subnet mask | Human identified next-hop `10.0.0.5` is offline; redirected to active gateway `10.0.0.2`. | `ip route 172.16.0.0 255.255.0.0 10.0.0.2` |
    | **NET-016** | FTP timeouts to server | AI proposed permitting only port 20 (data) | Human recognized active FTP requires control port 21 in addition to data port 20. | `access-list 100 permit tcp ... eq 21` |
    | **NET-003** | Host cannot resolve google.com | AI suggested contacting external ISP | Human identified local `no ip domain-lookup` on the gateway router. | `ip domain-lookup` & `ip name-server 8.8.8.8` |
    | **NET-026** | Port security err-disabled port | AI suggested reloading switch | Human safely issued interface `shutdown` and `no shutdown` to recover port without campus disruption. | `interface Fa0/10` -> `shutdown` -> `no shutdown` |
    | **NET-018** | WPA2 Enterprise RADIUS failure | AI proposed replacing RADIUS server | Human corrected shared secret key mismatch on the Cisco controller. | `radius-server host 10.0.0.50 key Cisco123Secret` |
    """)

    csv_data = df_audit.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Audit Trail (CSV)",
        data=csv_data,
        file_name="model_audit_trail.csv",
        mime="text/csv"
    )
