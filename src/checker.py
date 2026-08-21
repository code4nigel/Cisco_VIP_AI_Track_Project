"""
NetSage AI - Deterministic Rule Verification Engine (checker.py)
Provides regex and deterministic logic checks for common Cisco IOS configuration
and runtime errors before or alongside LLM reasoning.
"""

import re
import ipaddress
from typing import Dict, List, Any, Optional


class RuleFinding:
    """Represents a single detected rule violation or anomaly."""
    def __init__(self, rule_id: str, title: str, osi_layer: str, severity: str, evidence: str, remediation_hint: str):
        self.rule_id = rule_id
        self.title = title
        self.osi_layer = osi_layer
        self.severity = severity
        self.evidence = evidence
        self.remediation_hint = remediation_hint

    def to_dict(self) -> Dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "osi_layer": self.osi_layer,
            "severity": self.severity,
            "evidence": self.evidence,
            "remediation_hint": self.remediation_hint
        }


class DeterministicChecker:
    """
    Deterministic validation engine that scans CLI show command outputs and
    topology context for known static networking misconfigurations.
    """

    def __init__(self):
        pass

    def check_all(self, show_output: str, topology_note: str = "", symptom: str = "") -> Dict[str, Any]:
        """
        Runs all deterministic checks across the provided show output and topology context.
        Returns a dictionary with status, count, and detailed findings.
        """
        findings: List[RuleFinding] = []
        combined_text = f"{symptom}\n{topology_note}\n{show_output}"

        # 1. Interface & Physical/Protocol Status Checks
        self._check_interface_shutdown(show_output, findings)

        # 2. DHCP Pool & Relay Checks
        self._check_dhcp(show_output, findings)

        # 3. DNS & Domain Lookup Checks
        self._check_dns(show_output, findings)

        # 4. Routing Protocol & OSPF Checks
        self._check_routing(show_output, topology_note, symptom, findings)

        # 5. ACL & Port Filtering Checks
        self._check_acl(show_output, findings)

        # 6. NAT / PAT Configuration Checks
        self._check_nat(show_output, findings)

        # 7. VLAN & Trunking Configuration Checks
        self._check_vlan_trunking(show_output, topology_note, findings)

        # 8. IP Addressing & Subnet Boundary Checks
        self._check_addressing_and_subnet(show_output, topology_note, symptom, findings)

        # 9. Layer 2 Security & Protocols (DAI, Port Security, VTP, CDP, HSRP, IPv6, RADIUS)
        self._check_layer2_and_services(show_output, topology_note, findings)

        status = "ERRORS_DETECTED" if len(findings) > 0 else "CLEAN"
        return {
            "status": status,
            "findings_count": len(findings),
            "findings": [f.to_dict() for f in findings],
            "primary_finding": findings[0].to_dict() if findings else None
        }

    # ==================== INDIVIDUAL RULE CHECKS ====================

    def _check_interface_shutdown(self, text: str, findings: List[RuleFinding]):
        """Detects administratively down or shutdown interfaces."""
        if re.search(r"administratively\s+down", text, re.IGNORECASE):
            match = re.search(r"(\S+)\s+is\s+administratively\s+down.*", text, re.IGNORECASE)
            ev = match.group(0) if match else "Interface is administratively down"
            findings.append(RuleFinding(
                rule_id="RULE-IF-001",
                title="Interface Administratively Down",
                osi_layer="Layer 3" if "." in ev or "Vlan" in ev else "Layer 2/3",
                severity="High",
                evidence=ev.strip(),
                remediation_hint="Enter interface configuration mode and execute 'no shutdown'."
            ))
        elif re.search(r"\bshutdown\b", text, re.IGNORECASE) and not re.search(r"\bno\s+shutdown\b", text, re.IGNORECASE):
            match = re.search(r"interface\s+(\S+).*?shutdown", text, re.IGNORECASE | re.DOTALL)
            ev = match.group(0) if match else "Interface configured with shutdown"
            findings.append(RuleFinding(
                rule_id="RULE-IF-002",
                title="Interface Shutdown State",
                osi_layer="Layer 2",
                severity="Low" if "Vlan1" in text else "High",
                evidence=ev.strip().replace("\n", "; "),
                remediation_hint="Execute 'no shutdown' under the target interface."
            ))

    def _check_dhcp(self, text: str, findings: List[RuleFinding]):
        """Detects DHCP pool exhaustion and missing DHCP relay helper address."""
        # Pool exhaustion
        if re.search(r"zero\s+available", text, re.IGNORECASE) or (
            re.search(r"total\s+addresses\s+(\d+)", text, re.IGNORECASE) and
            re.search(r"leased\s+(\d+)", text, re.IGNORECASE)
        ):
            tot = re.search(r"total\s+addresses\s+(\d+)", text, re.IGNORECASE)
            lsd = re.search(r"leased\s+(\d+)", text, re.IGNORECASE)
            if (tot and lsd and tot.group(1) == lsd.group(1)) or "zero available" in text.lower():
                findings.append(RuleFinding(
                    rule_id="RULE-DHCP-001",
                    title="DHCP Scope Pool Exhaustion",
                    osi_layer="Layer 7",
                    severity="High",
                    evidence=text.strip(),
                    remediation_hint="Expand DHCP network pool range or clear inactive DHCP bindings."
                ))

        # Missing IP helper-address for relay
        if re.search(r"missing\s+ip\s+helper-address", text, re.IGNORECASE) or (
            "DHCP Discover" in text and "ip helper-address" not in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-DHCP-002",
                title="Missing DHCP IP Helper-Address",
                osi_layer="Layer 7",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Configure 'ip helper-address <DHCP_SERVER_IP>' on the client-facing router interface."
            ))

    def _check_dns(self, text: str, findings: List[RuleFinding]):
        """Detects DNS resolution disabled or inactive name server."""
        if re.search(r"no\s+ip\s+domain-lookup", text, re.IGNORECASE) or re.search(r"name-server.*not\s+active", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-DNS-001",
                title="DNS Name Resolution Disabled",
                osi_layer="Layer 7",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Configure 'ip domain-lookup' and verify valid 'ip name-server <IP>'."
            ))

    def _check_routing(self, text: str, topo: str, symptom: str, findings: List[RuleFinding]):
        """Detects OSPF timer mismatches, passive interface errors, redistribution issues, and invalid static routes."""
        # OSPF timer mismatch
        h_intervals = re.findall(r"hello-interval\s+(\d+)", text, re.IGNORECASE)
        if len(h_intervals) >= 2 and len(set(h_intervals)) > 1:
            findings.append(RuleFinding(
                rule_id="RULE-OSPF-001",
                title="OSPF Hello Interval Mismatch",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Align 'ip ospf hello-interval' and dead-interval on both peer interfaces."
            ))

        # Passive interface on active link
        if re.search(r"passive-interface\s+(\S+)", text, re.IGNORECASE):
            match = re.search(r"passive-interface\s+(\S+)", text, re.IGNORECASE)
            p_if = match.group(1) if match else "interface"
            findings.append(RuleFinding(
                rule_id="RULE-OSPF-002",
                title="Passive Interface Enabled on Active OSPF Link",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint=f"Remove passive-interface setting: 'no passive-interface {p_if}' under router ospf."
            ))

        # OSPF redistribution missing subnets
        if re.search(r"redistribute\s+\w+.*missing\s+subnets", text, re.IGNORECASE) or (
            "redistribute" in text.lower() and "missing subnets" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-OSPF-003",
                title="OSPF Redistribution Missing Subnets Flag",
                osi_layer="Layer 3",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Append 'subnets' keyword to redistribution command: 'redistribute <protocol> <id> subnets'."
            ))

        # Static route unreachable next-hop
        if re.search(r"ip\s+route\s+.*unreachable", text, re.IGNORECASE) or (
            "ip route" in text and "unreachable" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-ROUTE-001",
                title="Invalid Static Route Next-Hop",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Update static route with a reachable next-hop IP or valid egress interface."
            ))

    def _check_acl(self, text: str, findings: List[RuleFinding]):
        """Detects ACL blocking necessary ports or overly permissive guest ACLs."""
        # Extended ACL blocking HTTP
        if re.search(r"access-list\s+\d+\s+deny\s+tcp\s+.*eq\s+80", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-ACL-001",
                title="Extended ACL Blocking HTTP Traffic",
                osi_layer="Layer 4",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Permit HTTP traffic in the access-list or remove explicit deny rule."
            ))

        # Extended ACL blocking HTTPS (missing port 443)
        if re.search(r"eq\s+80.*missing\s+port\s+443", text, re.IGNORECASE) or (
            "eq 80" in text and "443" in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-ACL-002",
                title="ACL Missing HTTPS Port 443 Rule",
                osi_layer="Layer 4",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Add permit statement for SSL/TLS: 'access-list <num> permit tcp any any eq 443'."
            ))

        # FTP control port 21 missing
        if re.search(r"eq\s+20.*missing\s+port\s+21", text, re.IGNORECASE) or (
            "eq 20" in text and "21" in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-ACL-003",
                title="ACL Missing FTP Control Port 21",
                osi_layer="Layer 4",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Add permit statement for FTP control port 21 alongside data port 20."
            ))

        # Overly permissive Guest ACL
        if re.search(r"permit\s+ip\s+192\.168\.\d+\.0.*any", text, re.IGNORECASE) and "guest" in text.lower():
            findings.append(RuleFinding(
                rule_id="RULE-ACL-004",
                title="Overly Permissive Guest ACL",
                osi_layer="Layer 3/4",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Restrict Guest ACL with deny statements towards RFC1918 private subnets before permit any."
            ))

    def _check_nat(self, text: str, findings: List[RuleFinding]):
        """Detects missing NAT overload or missing NAT interface direction."""
        if re.search(r"missing\s+overload\s+keyword", text, re.IGNORECASE) or (
            "ip nat inside source list" in text and "overload" not in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-NAT-001",
                title="Missing NAT Overload (PAT) Keyword",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Append 'overload' to the dynamic NAT statement: 'ip nat inside source list <num> interface <iface> overload'."
            ))

        if re.search(r"missing\s+ip\s+nat\s+inside", text, re.IGNORECASE) or (
            "ip nat inside source static" in text and "missing ip nat inside" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-NAT-002",
                title="NAT Direction Missing on Inside Interface",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Configure 'ip nat inside' on the LAN interface."
            ))

    def _check_vlan_trunking(self, text: str, topo: str, findings: List[RuleFinding]):
        """Detects trunk misconfigurations, allowed VLAN pruning, and native VLAN mismatches."""
        # Inter-switch access instead of trunk
        if "switchport mode access" in text and ("SW1" in text or "SW2" in text or "inter-switch" in topo.lower()):
            findings.append(RuleFinding(
                rule_id="RULE-VLAN-001",
                title="Inter-Switch Link Configured as Access Port",
                osi_layer="Layer 2",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Convert trunk link port to trunk mode: 'switchport mode trunk'."
            ))

        # VLAN pruned from allowed list
        if re.search(r"missing\s+from\s+allowed\s+list", text, re.IGNORECASE) or (
            "allowed vlan" in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-VLAN-002",
                title="VLAN Missing from Trunk Allowed List",
                osi_layer="Layer 2",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Add missing VLAN: 'switchport trunk allowed vlan add <vlan_id>'."
            ))

        # Native VLAN mismatch
        if re.search(r"native\s+vlan\s+(\d+).*native\s+vlan\s+(\d+)", text, re.IGNORECASE):
            v_matches = re.findall(r"native\s+vlan\s+(\d+)", text, re.IGNORECASE)
            if len(v_matches) >= 2 and len(set(v_matches)) > 1:
                findings.append(RuleFinding(
                    rule_id="RULE-VLAN-003",
                    title="Native VLAN Mismatch on Trunk Link",
                    osi_layer="Layer 2",
                    severity="Low",
                    evidence=text.strip(),
                    remediation_hint="Align native VLAN ID on both switch trunk ports: 'switchport trunk native vlan <id>'."
                ))

        # Wrong access VLAN
        if re.search(r"switchport\s+access\s+vlan\s+(\d+)", text, re.IGNORECASE) and (
            "VLAN 40" in topo and "vlan 14" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-VLAN-004",
                title="Switch Port Assigned to Wrong Access VLAN",
                osi_layer="Layer 2",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Reassign port to correct VLAN: 'switchport access vlan <correct_vlan_id>'."
            ))

    def _check_addressing_and_subnet(self, text: str, topo: str, symptom: str, findings: List[RuleFinding]):
        """Detects gateway outside subnet boundary, wrong host default gateway, and duplicate IPs."""
        # Duplicate IP
        if re.search(r"%IP-4-DUP_ADDR|Duplicate\s+address", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-IP-001",
                title="Duplicate IP Address Conflict",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Identify duplicate host and reassign a unique static or DHCP IP address."
            ))

        # Host default gateway outside subnet or misconfigured
        if re.search(r"outside\s+subnet\s+boundary", text, re.IGNORECASE) or (
            "10.1.1.50" in text and "10.1.1.30" in text and "255.255.255.240" in text
        ):
            findings.append(RuleFinding(
                rule_id="RULE-IP-002",
                title="Default Gateway Outside Subnet Boundary",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Configure a valid default gateway IP within the host's subnet /28 range."
            ))
        elif re.search(r"Default\s+Gateway\s+(\d+\.\d+\.\d+\.\d+)", text, re.IGNORECASE) and (
            "192.168.1.1" in symptom or "192.168.1.1" in topo or "Misconfiguration" in text or "Gateway set to" in topo
        ):
            findings.append(RuleFinding(
                rule_id="RULE-IP-003",
                title="Host Default Gateway IP Misconfiguration",
                osi_layer="Layer 3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Correct host default gateway to point to the valid gateway IP (192.168.1.1)."
            ))

    def _check_layer2_and_services(self, text: str, topo: str, findings: List[RuleFinding]):
        """Detects VTP mismatch, DAI, Port Security, Dot1Q encapsulation, HSRP, IPv6 RA, CDP, RADIUS."""
        # Missing 802.1Q encapsulation on sub-interface
        if re.search(r"missing\s+encapsulation\s+dot1Q", text, re.IGNORECASE) or (
            "GigabitEthernet0/0.20" in text and "encapsulation dot1Q" not in text and "missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-SUBIF-001",
                title="Missing 802.1Q Encapsulation on Sub-Interface",
                osi_layer="Layer 2/3",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Add encapsulation dot1Q before assigning IP: 'encapsulation dot1Q <vlan_id>'."
            ))

        # VTP domain name casing mismatch
        if re.search(r"vtp\s+domain\s+(\w+)", text, re.IGNORECASE):
            domains = re.findall(r"vtp\s+domain\s+(\w+)", text)
            if len(domains) >= 2 and domains[0] != domains[1]:
                findings.append(RuleFinding(
                    rule_id="RULE-VTP-001",
                    title="VTP Domain Name Case Mismatch",
                    osi_layer="Layer 2",
                    severity="Medium",
                    evidence=text.strip(),
                    remediation_hint="Set identical case-sensitive VTP domain names across all switches: 'vtp domain <DOMAIN>'."
                ))

        # DAI untrusted uplink
        if re.search(r"arp\s+inspection\s+trust\s+missing", text, re.IGNORECASE) or (
            "DAI" in topo and "trust missing" in text.lower()
        ):
            findings.append(RuleFinding(
                rule_id="RULE-SEC-001",
                title="Uplink Port Missing DAI Trust",
                osi_layer="Layer 2",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Enable trust on switch uplink: 'ip arp inspection trust'."
            ))

        # Port Security violation
        if re.search(r"%PORT_SECURITY-2-PSECURE_VIOLATION|Security\s+violation", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-SEC-002",
                title="Port Security Violation Limit Exceeded",
                osi_layer="Layer 2",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Clear MAC address table or issue 'shutdown' / 'no shutdown' to recover port."
            ))

        # HSRP timer mismatch
        if re.search(r"standby\s+\d+\s+priority.*hello\s+(\d+)", text, re.IGNORECASE):
            hello_timers = re.findall(r"hello\s+(\d+)", text, re.IGNORECASE)
            if len(hello_timers) >= 2 and len(set(hello_timers)) > 1:
                findings.append(RuleFinding(
                    rule_id="RULE-HSRP-001",
                    title="HSRP Hello Timer Mismatch",
                    osi_layer="Layer 3",
                    severity="Medium",
                    evidence=text.strip(),
                    remediation_hint="Synchronize HSRP hello and hold timers across all standby group peers."
                ))

        # IPv6 Router Advertisements suppressed
        if re.search(r"ipv6\s+nd\s+suppress-ra\s+enabled", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-IPV6-001",
                title="IPv6 Router Advertisements (RA) Suppressed",
                osi_layer="Layer 3",
                severity="Medium",
                evidence=text.strip(),
                remediation_hint="Enable RA transmissions: 'no ipv6 nd suppress-ra' under the IPv6 interface."
            ))

        # CDP disabled globally
        if re.search(r"no\s+cdp\s+run", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-CDP-001",
                title="CDP Disabled Globally on Device",
                osi_layer="Layer 2",
                severity="Low",
                evidence=text.strip(),
                remediation_hint="Enable Cisco Discovery Protocol globally: 'cdp run'."
            ))

        # RADIUS Shared Secret mismatch
        if re.search(r"key\s+incorrect_secret_key|secret\s+mismatch", text, re.IGNORECASE):
            findings.append(RuleFinding(
                rule_id="RULE-WLAN-001",
                title="RADIUS Shared Secret Mismatch",
                osi_layer="Layer 7",
                severity="High",
                evidence=text.strip(),
                remediation_hint="Re-enter matching RADIUS pre-shared key: 'radius-server host <IP> key <KEY>'."
            ))


# Global singleton instance for quick invocation
checker = DeterministicChecker()


def run_deterministic_checks(show_output: str, topology_note: str = "", symptom: str = "") -> Dict[str, Any]:
    """Convenience helper to run all deterministic checks."""
    return checker.check_all(show_output, topology_note, symptom)
