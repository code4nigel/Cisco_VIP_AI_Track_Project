# NetSage AI: Automated Network Diagnostic Platform
## Cisco AICTE Virtual Internship Program 2026 — AI Track
### Individual Project Summary & Technical Report

---

### Project Metadata
- **Project Title:** NetSage AI: Automated Network Diagnostic Assistant with Human-in-the-Loop Verification
- **Student Name:** Shivanshu Yadav
- **Technology Track:** AI Track (Modern AI & NetDevOps)
- **Program:** Cisco AICTE Virtual Internship Program 2026
- **Problem Statement:** Project 2 — Applied AI + Network Troubleshooting
- **GitHub Repository:** [https://github.com/code4nigel/Cisco_VIP_AI_Track_Project.git](https://github.com/code4nigel/Cisco_VIP_AI_Track_Project.git)
- **Live Deployed Application:** [https://netsage-ai-cisco-shivanshu.streamlit.app/](https://netsage-ai-cisco-shivanshu.streamlit.app/)
- **Evaluation Submission Deadline:** 25th August 2026
- **Tech Guides:** Mr. Lilesh Pathe & Ms. Kuhu Sabui

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
In enterprise networks and Cisco lab environments (such as Cisco Packet Tracer), diagnosing multi-layer network failures requires extensive manual CLI execution (`show` commands), cross-layer OSI expertise, and careful verification before applying remediation.

Junior network engineers often understand individual commands but struggle to connect symptoms to root causes across Layer 2 to Layer 7. Furthermore, fully autonomous AI execution introduces severe risks: if an AI model hallucinates an invalid subnet mask or issues an incorrect shutdown command, it can cause catastrophic network downtime.

### 1.2 The NetSage AI Solution
NetSage AI bridges this gap by combining:
1. **Deterministic Rule-Based Verification (`checker.py`)**: Fast, mathematical regex-based checks that flag static misconfigurations (e.g., shutdown interfaces, timer mismatches, missing NAT overload keywords, subnet boundary violations) with 100% certainty.
2. **Structured LLM Diagnostic Reasoning (`engine.py` & `diagnose_prompt.md`)**: Analyzes multi-sentence symptoms, topology context, and CLI show outputs using Google Gemini (`gemini-2.5-flash`), enforcing a strict 6-field JSON schema validated by Pydantic.
3. **Human-in-the-Loop (HITL) Operations Dashboard (`app.py`)**: A Streamlit interface where human engineers review evidence, edit proposed CLI commands if necessary, and explicitly **Approve & Deploy**, **Edit**, or **Reject** remediation.
4. **Responsible AI Audit Logging (`model_audit_log.md`)**: Maintains a verifiable audit trail of AI vs. human agreement rates, recording exact AI-suggested commands vs. final deployed commands, and documenting 5 detailed human-override case studies.

---

## 2. System Architecture & Component Design

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
|     - Unified Studio: Presets & Live Custom Sandbox         |
|     - Evidence Inspector & IOS Command Terminal             |
|     - Human Review Buttons: [Approve] [Edit] [Reject]       |
|     - Real-Time KPIs, OSI Charts & Severity Analytics       |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  4. AUDIT & GOVERNANCE TIER                 |
|         docs/model_audit_log.md (Responsible AI Log)        |
+-------------------------------------------------------------+
```

---

## 3. Dataset & Scenario Coverage (`data/cases.csv`)

The dataset comprises **30 diverse Cisco Packet Tracer troubleshooting scenarios** spanning the entire OSI stack:
- **Layer 2 (Data Link):** VLAN Trunking, Allowed VLAN pruning, Native VLAN mismatches, Access port misconfigurations, VTP domain casing, Dynamic ARP Inspection (DAI) trust, Port Security violations, CDP.
- **Layer 3 (Network):** Sub-interface administrative down, Missing 802.1Q encapsulation, OSPF Hello/Dead timer mismatches, Passive interfaces on active links, OSPF route redistribution flags, Static route next-hop unreachability, Subnet boundaries, Host default gateway misconfigurations, Duplicate IP address conflicts, HSRP timers, IPv6 SLAAC Router Advertisement suppression, NAT/PAT missing overload keyword, Static 1:1 NAT interface directions.
- **Layer 4 (Transport):** Extended ACL blocking HTTP (Port 80), Extended ACL missing HTTPS (Port 443), ACL missing FTP control (Port 21).
- **Layer 7 (Application):** DHCP scope pool exhaustion, Missing DHCP relay `ip helper-address`, DNS domain lookup disabled, WPA2 Enterprise RADIUS shared secret mismatch.

---

## 4. Key Module Implementations

### 4.1 Deterministic Rule Checker (`src/checker.py`)
Implements modular regular expression rules and subnet calculations:
- `_check_interface_shutdown`: Detects `administratively down` or `shutdown` states.
- `_check_dhcp`: Flags DHCP pool exhaustion and missing helper addresses.
- `_check_nat`: Detects missing PAT `overload` keyword and missing `ip nat inside`.
- `_check_routing`: Catches OSPF timer mismatches, passive interfaces, and unreachable next-hops.
- `_check_acl`: Detects missing critical ports and overly permissive guest ACLs.
- `_check_vlan_trunking`: Identifies trunk mode errors, pruned VLANs, and native VLAN mismatches.
- `_check_addressing_and_subnet`: Uses IP subnetting logic to catch gateway boundary mismatches and duplicate IPs.
- **Performance:** Achieved **100.0% detection rate (30/30 cases)** on the test dataset.

### 4.2 Diagnostic Orchestrator (`src/engine.py`)
- Coordinates the deterministic checker and the structured prompt template (`prompts/diagnose_prompt.md`).
- Connects live Google Gemini API (`gemini-2.5-flash`) with automatic offline domain synthesis fallback.
- Utilizes **Pydantic (`DiagnosisResult`)** to enforce strict typing and guarantee zero schema violations across all 6 fields:
  `root_cause`, `osi_layer`, `confidence`, `evidence`, `next_command`, `fix_steps`.

### 4.3 Unified Streamlit Operations Dashboard (`src/app.py`)
Features 3 cohesive operational views:
1. **Diagnostic Studio (Presets & Custom):** Unified workspace supporting all 30 preset lab scenarios and a live Custom Telemetry Sandbox in the same guided 3-step workflow (Evidence ➔ AI Diagnosis ➔ Human-in-the-Loop Sign-off).
2. **Metrics & Distribution Analytics:** Interactive Plotly visualizations for OSI layer distribution, fault severity breakdown, and live human agreement rate KPIs.
3. **Responsible AI Audit Log:** Live searchable audit table with command comparison (`ai_suggested_commands` vs. `final_deployed_commands`), 5 documented human override case studies, and CSV export capability.

---

## 5. Responsible AI Governance & Human Overrides

In accordance with Cisco AICTE Responsible AI guidelines, NetSage AI logged **5 in-depth human override case studies**:
1. **NET-015 (Static Route Next-Hop):** AI suggested changing subnet mask; human engineer discovered the next-hop IP was unreachable and corrected the route to the active gateway (`10.0.0.2`).
2. **NET-016 (FTP ACL Port Omission):** AI suggested increasing server timeout; human recognized active FTP requires control port 21 alongside data port 20.
3. **NET-003 (DNS Resolution Disabled):** AI suggested contacting external ISP; human identified local `no ip domain-lookup` on the gateway router.
4. **NET-026 (Port Security Err-Disable):** AI recommended reloading the switch; human safely issued `shutdown` / `no shutdown` to recover the single port without campus disruption.
5. **NET-018 (RADIUS Secret Mismatch):** AI suggested replacing hardware; human corrected the pre-shared secret string on the Cisco WLC.

---

## 6. Evaluation & Verification Results

| Evaluation Criterion | Standard | NetSage AI Result |
| :--- | :--- | :--- |
| **Dataset Completeness** | $\ge 30$ cases | **30 verified multi-layer scenarios** |
| **Rule Checker Accuracy** | $\ge 90.0\%$ | **100.0% (30/30 detected)** |
| **Engine Schema Validation** | 100% Pydantic compliant | **100.0% pass** |
| **Human Agreement Rate** | $\ge 80.0\%$ | **88.3%** |
| **Documented AI Corrections** | $\ge 5$ cases | **5 documented case studies** |

---

## 7. Individual Student Contributions & Engineering Roles

**Author:** Shivanshu Yadav  
**Role:** Lead AI & NetDevOps Engineer

During the internship project, Shivanshu Yadav accomplished the following engineering deliverables:
1. **Dataset Engineering & Multi-Layer Taxonomy:** Curated and standardized 30 realistic Cisco Packet Tracer failure scenarios spanning OSI Layers 2 through 7 in `data/cases.csv`.
2. **Deterministic Rule Engine Architecture:** Developed `src/checker.py` using Python regular expressions and IP subnet calculations, achieving 100.0% coverage across static networking misconfigurations.
3. **Prompt Engineering & Schema Distillation:** Designed few-shot prompt templates (`prompts/diagnose_prompt.md`) enforcing strict 6-field JSON output schemas validated by Pydantic models in `src/engine.py`.
4. **Live LLM Integration & Persistence:** Integrated the Google GenAI SDK (`gemini-2.5-flash`), built offline synthesis fallbacks, and implemented persistent `.env` configuration management.
5. **Human-in-the-Loop Web Platform:** Engineered the Streamlit application (`src/app.py`) featuring dual-theme styling (Dark Espresso and Warm Paper Light), a unified 3-step diagnostic pipeline, and full-width certified CLI deployment blocks.
6. **Responsible AI Governance & Auditing:** Formulated the human-in-the-loop review mechanism, logging agreement rates and documenting 5 edge-case overrides in `docs/model_audit_log.md`.

---

## 8. Conclusion
NetSage AI successfully demonstrates how combining deterministic network validation with structured modern AI and a Human-in-the-Loop verification gate provides a secure, accurate, and educational troubleshooting assistant for Cisco enterprise and lab networks.
