# NetSage AI: Automated Network Diagnostic Assistant

**Cisco AICTE Virtual Internship Program 2026 — AI Track (Project 2)**  
**Student Submission:** Shivanshu Yadav  
**Repository:** [https://github.com/code4nigel/Cisco_VIP_AI_Track_Project.git](https://github.com/code4nigel/Cisco_VIP_AI_Track_Project.git)

---

## 1. Project Overview

NetSage AI is an AI-assisted network diagnostic and troubleshooting platform tailored for Cisco lab environments (such as Cisco Packet Tracer). It connects network symptoms and Cisco IOS CLI `show` command outputs to root causes across the OSI 7-layer model, suggests the next diagnostic verification commands, and generates exact remediation CLI commands.

To mitigate hallucinations and prevent dangerous autonomous commands on network infrastructure, NetSage AI employs a **Hybrid Pipeline Architecture**:
1. **Deterministic Rule Checker (`src/checker.py`)**: Fast, regular-expression-based engine that flags static configuration errors (such as administratively shutdown interfaces, missing NAT overload keywords, OSPF timer mismatches, and subnet boundary errors) with 100% mathematical certainty.
2. **Structured LLM Diagnostic Reasoning (`src/engine.py` & `prompts/diagnose_prompt.md`)**: Synthesizes complex multi-sentence symptoms and verbose CLI outputs using Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`), enforcing a strict 6-field JSON output schema validated by Pydantic.
3. **Human-in-the-Loop (HITL) Verification Gate (`src/app.py`)**: A Streamlit operations dashboard where network engineers inspect evidence, edit proposed CLI commands, and explicitly approve or reject remediation before deployment.
4. **Responsible AI Governance (`docs/model_audit_log.md`)**: A verifiable audit log documenting human review decisions, agreement metrics, and 5 detailed human-override case studies.

---

## 2. System Architecture

```
+-------------------------------------------------------------+
|                        1. DATA TIER                         |
|   data/cases.csv (30 Multi-Layer Cisco Packet Tracer Cases) |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  2. DIAGNOSTIC CORE ENGINE                  |
|   +--------------------------+   +----------------------+   |
|   |      src/checker.py      |   | prompts/diagnose_... |   |
|   |  (Deterministic Regex)   |   | (Few-Shot Prompts)   |   |
|   +------------+-------------+   +----------+-----------+   |
|                |                            |               |
|                +-------------+--------------+               |
|                              v                              |
|                       src/engine.py                         |
|         (Hybrid Gemini API + Pydantic Schema Validator)     |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|             3. HUMAN-IN-THE-LOOP (HITL) GATEWAY             |
|          src/app.py (Streamlit Operations Dashboard)        |
|     - Case Studio & Custom Telemetry Sandbox                |
|     - 10-Lab Packet Tracer Stress Testing Suite             |
|     - Human Review Gate: [Approve] [Edit] [Reject]          |
|     - Real-Time KPIs, OSI Layer & Severity Visualizations   |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  4. AUDIT & GOVERNANCE TIER                 |
|         docs/model_audit_log.md (Responsible AI Log)        |
+-------------------------------------------------------------+
```

---

## 3. Repository Structure

```
.
|-- .gitignore                               # Git ignore configuration (.venv, .env, seabed)
|-- README.md                                # Project documentation and user guide
|-- requirements.txt                         # Python dependencies
|
|-- data/
|   `-- cases.csv                            # 30 structured Cisco Packet Tracer test cases (L2-L7)
|
|-- prompts/
|   `-- diagnose_prompt.md                   # System prompt, few-shot examples, and strict JSON schema
|
|-- src/
|   |-- __init__.py                          # Python package marker
|   |-- checker.py                           # Deterministic regex and logic rule checker
|   |-- engine.py                            # Diagnostic orchestrator (Google Gemini API & offline engine)
|   `-- app.py                               # Streamlit operations dashboard (Dark & Light themes)
|
|-- tests/
|   `-- test_checker.py                      # Automated test suite evaluating checker accuracy
|
`-- docs/
    |-- model_audit_log.md                   # Responsible AI log with 5 documented human overrides
    |-- Project_Summary_Document.md          # Technical summary and evaluation report
    |-- NetSage_AI_Project_Summary_Document.docx # Formatted Word submission report
    `-- Packet_Tracer_10_Lab_Scenarios.md    # 10-Lab replication and stress-test guide
```

---

## 4. Key Performance Metrics

| Evaluation Metric | Target Requirement | NetSage AI Measured Result |
| :--- | :--- | :--- |
| **Dataset Completeness** | At least 30 cases | **30 Scenarios** (Layer 2 through Layer 7) |
| **Rule Checker Coverage** | >= 80.0% | **100.0% (30/30 test cases detected)** |
| **JSON Schema Compliance** | 100% | **100.0% (Pydantic validated)** |
| **Human Agreement Rate** | >= 80.0% | **88.3% Agreement** |
| **Responsible AI Overrides** | At least 5 cases | **5 Documented Case Studies** |

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/code4nigel/Cisco_VIP_AI_Track_Project.git
cd Cisco_VIP_AI_Track_Project
```

### Step 2: Create and Activate a Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Running the Application

### Launch the Streamlit Dashboard
```bash
streamlit run src/app.py
```
Open your browser and navigate to `http://localhost:8501`.

### Running Automated Tests
To run the automated verification suite against all 30 cases:
```bash
python tests/test_checker.py
```

---

## 7. Operational Workflow

1. **Case Selection & Telemetry Inspection**:
   Select any of the 30 Cisco Packet Tracer scenarios. The dashboard displays the observed symptom, network topology layout, and captured CLI `show` output.
2. **Deterministic & AI Diagnosis**:
   The rule checker scans for static syntax errors, while the diagnostic engine deduces the root cause, quotes evidence, and suggests remediation commands.
3. **Human-in-the-Loop Sign-Off**:
   The operator reviews the proposed Cisco IOS commands and chooses to **Approve & Deploy**, **Edit Commands** (manual override), or **Reject Diagnosis**.
4. **Audit Trail**:
   All operator decisions are recorded in `docs/model_audit_log.md` and can be exported as CSV from the dashboard.

---

## 8. Responsible AI & Governance

In compliance with Cisco AICTE Responsible AI guidelines, NetSage AI documents 5 concrete human-override scenarios where engineers corrected initial AI proposals:
1. **NET-015 (Static Route Next-Hop)**: Redirected invalid next-hop `10.0.0.5` to active gateway `10.0.0.2`.
2. **NET-016 (FTP Access-List)**: Added missing FTP control port 21 alongside data port 20.
3. **NET-003 (DNS Resolution)**: Re-enabled `ip domain-lookup` on local gateway instead of escalating to external ISP.
4. **NET-026 (Port Security Err-Disable)**: Issued interface `shutdown` / `no shutdown` to safely recover the port without rebooting the switch.
5. **NET-018 (RADIUS Secret Mismatch)**: Corrected pre-shared secret string on the Cisco controller instead of replacing authentication hardware.

---

## 9. Author Information

- **Student Name:** Shivanshu Yadav
- **Program:** Cisco AICTE Virtual Internship Program 2026
- **Track:** AI Track (Project 2: Applied AI + Network Troubleshooting)
- **Submission Date:** August 2026
