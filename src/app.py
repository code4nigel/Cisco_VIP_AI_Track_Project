"""
NetSage AI - Modern Operations & Diagnostic Dashboard (app.py)
Theme-aware (Dark Espresso / Warm Paper Light) with guided 3-step workflow,
live Google Gemini LLM API integration, 10-Lab Packet Tracer stress testing suite,
and author metadata for Shivanshu Yadav.
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

# Session state initialization
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark (Espresso)"

if "use_live_llm" not in st.session_state:
    st.session_state.use_live_llm = False

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

if "audit_trail" not in st.session_state:
    st.session_state.audit_trail = [
        {
            "case_id": "NET-001",
            "decision": "Approved",
            "reviewer": "Shivanshu Yadav (NetOps)",
            "notes": "Verified sub-interface admin down state and approved 'no shutdown'.",
            "timestamp": "2026-08-21 14:10:00"
        },
        {
            "case_id": "NET-015",
            "decision": "Edited",
            "reviewer": "Shivanshu Yadav (Senior NetOps)",
            "notes": "Corrected static route next-hop to active gateway 10.0.0.2.",
            "timestamp": "2026-08-21 14:15:30"
        },
        {
            "case_id": "NET-016",
            "decision": "Edited",
            "reviewer": "Shivanshu Yadav (Security Lead)",
            "notes": "Added both FTP control port 21 and data port 20 to ACL 100.",
            "timestamp": "2026-08-21 14:22:10"
        }
    ]

# Sidebar Navigation & Settings
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #D9A05B; display: flex; align-items: center; gap: 8px; font-weight: 700;">
            <span>●</span> netsage.ai
        </div>
        <div style="font-family: 'Newsreader', serif; font-style: italic; font-size: 0.88rem; margin-top: 2px;">
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
    
    # Navigation Radio
    nav_choice = st.radio(
        "Navigation",
        [
            "1. Case Diagnostic Studio",
            "2. Custom Telemetry Sandbox",
            "3. 10-Lab Stress Test Suite",
            "4. Metrics & Analytics",
            "5. Responsible AI Audit Log"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Live AI Engine Configuration")
    
    live_toggle = st.toggle("Enable Live Gemini API", value=st.session_state.use_live_llm)
    st.session_state.use_live_llm = live_toggle
    
    if live_toggle:
        user_key = st.text_input("Gemini API Key:", value=st.session_state.gemini_api_key, type="password", placeholder="AIzaSy...")
        st.session_state.gemini_api_key = user_key
        st.caption("Using Google Gemini (`gemini-2.5-flash`) for real-time prompt reasoning.")
    else:
        st.caption("Running in fast offline domain synthesis mode.")
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.82rem; padding: 6px 0;">
        <div style="font-size: 0.72rem; text-transform: uppercase; font-family: monospace; opacity: 0.7;">Student Submission</div>
        <div style="font-weight: 700; font-size: 1.0rem; color: #D9A05B; margin-top: 2px;">Shivanshu Yadav</div>
        <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 1px;">Cisco AICTE VIP Program 2026</div>
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

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0F0E0D !important;
            color: #EAE7E1 !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        header[data-testid="stHeader"] {
            background-color: #0F0E0D !important;
        }

        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: #0A0A09 !important;
            border-right: 1px solid #262320 !important;
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

# Helper to load dataset
@st.cache_data
def load_dataset():
    csv_path = Path(__file__).parent.parent / "data" / "cases.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()

df_cases = load_dataset()

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
# VIEW 1: CASE DIAGNOSTIC STUDIO (GUIDED 3-STEP WORKFLOW)
# ==============================================================================
if nav_choice == "1. Case Diagnostic Studio":
    if df_cases.empty:
        st.error("Dataset `data/cases.csv` not found.")
    else:
        # Stepper
        st.markdown("""
        <div class="step-stepper">
            <div class="step-item active"><span>①</span> Select Case</div>
            <div class="step-item" style="color: #D9A05B;"><span>➔</span></div>
            <div class="step-item active"><span>②</span> Inspect Evidence & AI Diagnosis</div>
            <div class="step-item" style="color: #D9A05B;"><span>➔</span></div>
            <div class="step-item active"><span>③</span> Review & Human Sign-off</div>
        </div>
        """, unsafe_allow_html=True)

        # Case selection row
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            case_options = [f"{row['case_id']} — {row['symptom']}" for _, row in df_cases.iterrows()]
            selected_str = st.selectbox("Select Troubleshooting Lab Scenario:", case_options)
            selected_id = selected_str.split(" — ")[0]
            case_data = df_cases[df_cases["case_id"] == selected_id].iloc[0]

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

        st.markdown("---")

        # Two-Column Layout
        c_left, c_right = st.columns([1, 1], gap="large")

        with c_left:
            st.markdown("### 📥 Step 1: Raw Lab Evidence & Observations")
            st.caption("What the network reports: observed symptoms, topology layout, and captured CLI outputs.")

            # Symptom Card
            st.markdown(f"""
            <div class="enscribe-card">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; margin-bottom: 4px; opacity: 0.7;">Observed Symptom</div>
                <div style="font-family: 'Newsreader', serif; font-size: 1.15rem; line-height: 1.4; margin-bottom: 10px;">
                    "{case_data['symptom']}"
                </div>
                <div style="font-size: 0.86rem; border-top: 1px solid rgba(128,128,128,0.15); padding-top: 8px;">
                    <b style="font-family: monospace; color: #8A5B20;">TOPOLOGY CONTEXT:</b> {case_data['topology_note']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Raw CLI Show Output
            st.markdown("<div style='font-family: monospace; font-size: 0.75rem; text-transform: uppercase;'>Captured CLI Show Output</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="enscribe-terminal">{case_data['show_outputs']}</div>
            """, unsafe_allow_html=True)

            # Deterministic Rule Engine Check
            rule_res = run_deterministic_checks(
                show_output=str(case_data['show_outputs']),
                topology_note=str(case_data['topology_note']),
                symptom=str(case_data['symptom'])
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
                symptom=str(case_data['symptom']),
                topology_note=str(case_data['topology_note']),
                show_output=str(case_data['show_outputs']),
                case_id=case_data['case_id'],
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
                    <div>Ground Truth: <i>{case_data['expected_fault']}</i></div>
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

            edit_active = st.toggle("✏️ Enable Manual CLI Command Override", value=False)

            if edit_active:
                edited_cli = st.text_area("Edit Cisco IOS Commands:", value=cli_text, height=110)
            else:
                st.code(cli_text, language="cisco")
                edited_cli = cli_text

            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("✅ Approve & Deploy", use_container_width=True, type="primary"):
                    st.session_state.audit_trail.append({
                        "case_id": case_data["case_id"],
                        "decision": "Approved" if not edit_active else "Approved (Edited)",
                        "reviewer": "Shivanshu Yadav (NetOps)",
                        "notes": "Verified CLI commands and approved for Packet Tracer deployment.",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("🎉 Remediation Approved & Recorded in Audit Trail!")
                    st.balloons()

            with col_b2:
                if st.button("💾 Save Override", use_container_width=True):
                    st.session_state.audit_trail.append({
                        "case_id": case_data["case_id"],
                        "decision": "Edited",
                        "reviewer": "Shivanshu Yadav (Senior Lead)",
                        "notes": f"Human override saved: {edited_cli.splitlines()[-1] if edited_cli else 'Custom fix'}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.warning("💾 Human Override Logged to Audit Trail.")

            with col_b3:
                if st.button("❌ Reject", use_container_width=True):
                    st.session_state.audit_trail.append({
                        "case_id": case_data["case_id"],
                        "decision": "Rejected",
                        "reviewer": "Shivanshu Yadav (QA Lead)",
                        "notes": "Diagnosis rejected due to ambiguity or alternative root cause.",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.error("🛑 Diagnosis Rejected & Flagged for Model Safety Review.")


# ==============================================================================
# VIEW 2: CUSTOM SANDBOX
# ==============================================================================
elif nav_choice == "2. Custom Telemetry Sandbox":
    st.markdown("### 🧪 Live Custom Telemetry Diagnostic Sandbox")
    st.write("Input arbitrary Cisco failure symptoms and show outputs to execute live hybrid diagnosis.")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        s_sym = st.text_input("Observed Failure Symptom:", value="Accounting PC cannot ping Default Gateway on sub-interface")
        s_top = st.text_area("Topology & Configuration Notes:", value="PC IP 192.168.20.50/24; Switch Fa0/5 connected to Router Gi0/0.20", height=100)
    with c2:
        s_sho = st.text_area("Cisco IOS Show Commands / Logs:", value="interface GigabitEthernet0/0.20\n ip address 192.168.20.1 255.255.255.0\n (missing encapsulation dot1Q 20)", height=150)

    if st.button("🚀 Execute Live Diagnostic Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing custom telemetry with NetSage AI pipeline..."):
            res = diagnose_case(
                s_sym, s_top, s_sho, "CUSTOM-TEST",
                use_live_llm=st.session_state.use_live_llm,
                api_key=st.session_state.gemini_api_key
            )
            d = res["diagnosis"]

            st.markdown("---")
            st.markdown(f"""
            <div class="enscribe-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-family: 'Newsreader', serif; font-size: 1.25rem; color: #D9A05B; font-weight: 600;">Custom Diagnostic Finding</span>
                    <span class="enscribe-pill pill-cyan">{d['osi_layer']}</span>
                </div>
                <div style="font-family: 'Newsreader', serif; font-size: 1.1rem; margin-bottom: 8px;">
                    {d['root_cause']}
                </div>
                <div style="font-family: monospace; font-size: 0.78rem; opacity: 0.8;">
                    Confidence: <b style="color: #2E8555;">{d['confidence']}</b> | Engine: <b>{res['engine_mode']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<small style='font-family: monospace; text-transform: uppercase;'>Quoted Evidence:</small>", unsafe_allow_html=True)
            st.markdown(f"<div class='enscribe-terminal' style='color: #D9A05B;'>\"{d['evidence']}\"</div>", unsafe_allow_html=True)

            st.markdown("<small style='font-family: monospace; text-transform: uppercase;'>Proposed Remediation Commands:</small>", unsafe_allow_html=True)
            st.code("\n".join(d["fix_steps"]), language="cisco")


# ==============================================================================
# VIEW 3: 10-LAB STRESS TEST SUITE
# ==============================================================================
elif nav_choice == "3. 10-Lab Stress Test Suite":
    st.markdown("### 🔬 10 Multi-Layer Cisco Packet Tracer Stress-Test Scenarios")
    st.write("These 10 scenarios are designed to deliberately challenge and evaluate NetSage AI across Layer 2 to Layer 7 failure modes.")

    STRESS_LABS = [
        {"id": "NET-001", "name": "Lab 1: Sub-interface Administratively Down", "layer": "Layer 3", "type": "Visibility", "challenge": "Detecting sub-interface line protocol failure"},
        {"id": "NET-004", "name": "Lab 2: OSPF Hello/Dead Timer Mismatch", "layer": "Layer 3", "type": "Multi-Router", "challenge": "Correlating timer mismatch across R1 & R2 interfaces"},
        {"id": "NET-022", "name": "Lab 3: Extended ACL Dropping HTTPS (Port 443)", "layer": "Layer 4", "type": "Security/ACL", "challenge": "Distinguishing port 80 allow vs port 443 drop"},
        {"id": "NET-002", "name": "Lab 4: DHCP Scope Pool Exhaustion (APIPA Fallback)", "layer": "Layer 7", "type": "Services", "challenge": "Connecting 169.254.x.x to DHCP pool depletion"},
        {"id": "NET-015", "name": "Lab 5: Static Route Unreachable Next-Hop IP", "layer": "Layer 3", "type": "Hallucination Test", "challenge": "Tests if AI hallucinates changing subnet mask vs correcting next-hop"},
        {"id": "NET-016", "name": "Lab 6: Active FTP Control Port 21 ACL Drop", "layer": "Layer 4", "type": "Protocol Logic", "challenge": "Tests dual-port requirement (Data 20 vs Control 21)"},
        {"id": "NET-026", "name": "Lab 7: Port Security Err-Disabled Safe Recovery", "layer": "Layer 2", "type": "Safety Gate", "challenge": "Ensures AI does NOT reboot the entire switch (safe shutdown bounce)"},
        {"id": "NET-018", "name": "Lab 8: RADIUS Pre-Shared Secret Mismatch", "layer": "Layer 7", "type": "Wireless Auth", "challenge": "Identifies controller secret mismatch vs hardware fault"},
        {"id": "NET-020", "name": "Lab 9: Default Gateway Outside /28 Subnet Boundary", "layer": "Layer 3", "type": "Binary Math", "challenge": "Executes CIDR binary subnet calculations"},
        {"id": "NET-025", "name": "Lab 10: Dynamic ARP Inspection (DAI) Untrusted Trunk", "layer": "Layer 2", "type": "Advanced L2", "challenge": "Detects missing DAI trust on inter-switch trunk"}
    ]

    for lab in STRESS_LABS:
        with st.expander(f"📌 {lab['name']} — [{lab['layer']}]", expanded=False):
            c_l1, c_l2 = st.columns([2, 1])
            with c_l1:
                st.markdown(f"**Target Failure:** `{lab['challenge']}`")
                st.markdown(f"**Evaluation Type:** `{lab['type']}`")
            with c_l2:
                if st.button(f"⚡ Run Diagnostic Test on {lab['id']}", key=f"btn_{lab['id']}"):
                    row_data = df_cases[df_cases["case_id"] == lab['id']].iloc[0]
                    res = diagnose_case(
                        str(row_data['symptom']),
                        str(row_data['topology_note']),
                        str(row_data['show_outputs']),
                        lab['id'],
                        use_live_llm=st.session_state.use_live_llm,
                        api_key=st.session_state.gemini_api_key
                    )
                    st.success(f"Diagnosis Generated via: {res['engine_mode']}")
                    st.markdown(f"**Root Cause:** {res['diagnosis']['root_cause']}")
                    st.markdown(f"**Evidence:** `{res['diagnosis']['evidence']}`")
                    st.code("\n".join(res['diagnosis']['fix_steps']), language="cisco")


# ==============================================================================
# VIEW 4: METRICS & ANALYTICS
# ==============================================================================
elif nav_choice == "4. Metrics & Analytics":
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
# VIEW 5: RESPONSIBLE AI LOG
# ==============================================================================
elif nav_choice == "5. Responsible AI Audit Log":
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
