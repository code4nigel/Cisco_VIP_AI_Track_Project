# NetSage AI — 10 Stress-Test Lab Scenarios Guide (`.pkt` Replication Guide)

> **Purpose:** Detailed step-by-step instructions to build, break, reproduce, and verify 10 distinct multi-layer Cisco Packet Tracer lab scenarios for stress-testing NetSage AI.

---

## 🏗️ Master Lab Scenarios Matrix

| Scenario # | Title | Target OSI Layer | Fault Injection | Expected NetSage AI Diagnosis | Stress-Test Challenge |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lab 1** | Sub-Interface Down | Layer 3 | `interface Gi0/0.10` -> `shutdown` | Sub-interface administratively down | Basic visibility check |
| **Lab 2** | OSPF Timer Mismatch | Layer 3 | R1 hello 10s, R2 hello 20s | OSPF Hello Timer Mismatch | Multi-router cross-correlation |
| **Lab 3** | ACL HTTPS Block | Layer 4 | ACL permits 80, missing 443 | Extended ACL blocking SSL/TLS 443 | Port-level filtering accuracy |
| **Lab 4** | DHCP Pool Exhaustion | Layer 7 | Scope pool range exhausted | DHCP scope exhaustion (APIPA fallback) | Distinguishing DHCP starvation |
| **Lab 5** | Unreachable Next-Hop | Layer 3 | Static route points to `10.0.0.5` | Invalid static route next-hop IP | **Tests LLM hallucination** (prevents altering subnet mask) |
| **Lab 6** | FTP Control Port 21 Drop | Layer 4 | ACL permits TCP 20 only | ACL missing FTP control port 21 | **Tests dual-port protocol logic** |
| **Lab 7** | Port Security Err-Disable | Layer 2 | Exceeded MAC address limit | Port security violation err-disable | **Tests safe recovery** (prevents switch reboot) |
| **Lab 8** | RADIUS Secret Typo | Layer 7 | `key incorrect_secret_key` | RADIUS pre-shared secret mismatch | Prevents false hardware replacement |
| **Lab 9** | Subnet Boundary Mismatch | Layer 3 | Host `10.1.1.50/28`, GW `10.1.1.30` | Default Gateway outside subnet | **Tests binary subnet calculation** |
| **Lab 10**| DAI Untrusted Uplink | Layer 2 | DAI enabled, uplink not trusted | Missing DAI trust on uplink trunk | Advanced L2 security inspection |

---

## 🛠️ Detailed Replication Steps for Packet Tracer

### 🔬 Scenario 1: Inter-VLAN Routing Failure (NET-001)
- **Topology:** Router `R1` connected via trunk `Gi0/0` to Switch `SW1`. `PC1` in VLAN 10 (`192.168.10.10/24`), `Server1` in VLAN 30 (`192.168.30.10/24`).
- **Break Step on R1:**
  ```cisco
  interface GigabitEthernet0/0.10
  shutdown
  ```
- **Observed Symptom:** PC1 cannot ping Server1. Gateway ping `192.168.10.1` fails.
- **Show Command:** `show ip interface brief`
- **Expected Fix:** `interface GigabitEthernet0/0.10` -> `no shutdown`.

---

### 🔬 Scenario 2: OSPF Adjacency Failure (NET-004)
- **Topology:** Router `R1` (`10.0.0.1/24`) connected to Router `R2` (`10.0.0.2/24`) on `Gi0/0`.
- **Break Step on R2:**
  ```cisco
  interface GigabitEthernet0/0
  ip ospf hello-interval 20
  ```
- **Observed Symptom:** OSPF neighbor table is empty (`show ip ospf neighbor` returns nothing).
- **Show Command:** `show ip ospf interface GigabitEthernet0/0` on both routers.
- **Expected Fix:** `ip ospf hello-interval 10` on R2.

---

### 🔬 Scenario 3: HTTPS Traffic Dropped by Firewall ACL (NET-022)
- **Topology:** Internal LAN `192.168.1.0/24` through Edge Firewall/Router to Public Web Server (`203.0.113.80`).
- **Break Step:**
  ```cisco
  access-list 102 permit tcp 192.168.1.0 0.0.0.255 any eq 80
  access-list 102 deny ip any any
  interface Gi0/1
  ip access-group 102 in
  ```
- **Observed Symptom:** Internal users can browse standard HTTP websites (`port 80`) but all secure HTTPS websites (`port 443`) time out.
- **Show Command:** `show access-lists 102`
- **Expected Fix:** `access-list 102 permit tcp 192.168.1.0 0.0.0.255 any eq 443`.

---

### 🔬 Scenario 4: DHCP Scope Pool Exhaustion (NET-002)
- **Topology:** DHCP Server on Router `R1` with pool `LAN_POOL`. 10 client workstations connected to Switch `SW1`.
- **Break Step on R1:**
  ```cisco
  ip dhcp pool LAN_POOL
  network 192.168.1.0 255.255.255.240
  ```
- **Observed Symptom:** 11th workstation (`PC2`) receives an APIPA address (`169.254.x.x`) and shows zero IP connectivity.
- **Show Command:** `show ip dhcp pool LAN_POOL` -> `total addresses 10; leased 10; zero available`.
- **Expected Fix:** Expand subnet pool to `/24` (`network 192.168.1.0 255.255.255.0`).

---

### 🔬 Scenario 5: Static Route Invalid Next-Hop (NET-015)
- **Topology:** Branch Router `R1` communicating with Central Server behind `R2`.
- **Break Step on R1:**
  ```cisco
  ip route 172.16.0.0 255.255.0.0 10.0.0.5
  ```
- **Observed Symptom:** Branch clients cannot communicate with `172.16.0.0/16`. Traffic is dropped at R1.
- **Show Command:** `show ip route 172.16.0.0` shows next hop `10.0.0.5` which is not directly connected or ARP-resolvable.
- **Expected Fix:** `no ip route 172.16.0.0 255.255.0.0 10.0.0.5` followed by `ip route 172.16.0.0 255.255.0.0 10.0.0.2`.

---

### 🔬 Scenario 6: Active FTP Connection Failure (NET-016)
- **Topology:** PC client accessing internal File Server on `10.0.0.25`.
- **Break Step:**
  ```cisco
  access-list 100 permit tcp 192.168.1.0 0.0.0.255 host 10.0.0.25 eq 20
  access-list 100 deny ip any any
  ```
- **Observed Symptom:** FTP client connects but authentication times out before directory listing.
- **Show Command:** `show access-lists 100`
- **Expected Fix:** `access-list 100 permit tcp 192.168.1.0 0.0.0.255 host 10.0.0.25 eq 21`.

---

### 🔬 Scenario 7: Port Security Err-Disable Violation (NET-026)
- **Topology:** Switch `SW1` port `Fa0/10` connected to Office Desk.
- **Break Step on SW1:**
  ```cisco
  interface FastEthernet0/10
  switchport mode access
  switchport port-security
  switchport port-security maximum 1
  switchport port-security violation shutdown
  ```
- **Observed Symptom:** Connecting a second laptop triggers port shutdown: `%PORT_SECURITY-2-PSECURE_VIOLATION`.
- **Show Command:** `show interfaces FastEthernet0/10 status` shows `err-disabled`.
- **Expected Fix:** `interface FastEthernet0/10` -> `shutdown` -> `no shutdown`.

---

### 🔬 Scenario 8: WPA2-Enterprise RADIUS Secret Mismatch (NET-018)
- **Topology:** Cisco Wireless LAN Controller (WLC) connected to external FreeRADIUS/NPS Server on `10.0.0.50`.
- **Break Step on WLC / Switch:**
  ```cisco
  radius-server host 10.0.0.50 key incorrect_secret_key
  ```
- **Observed Symptom:** Wireless clients cannot complete 802.1X PEAP authentication.
- **Show Command:** `show radius-server`
- **Expected Fix:** `radius-server host 10.0.0.50 key Cisco123Secret`.

---

### 🔬 Scenario 9: Default Gateway Outside Subnet Boundary (NET-020)
- **Topology:** Workstation statically configured with IP `10.1.1.50/28` (`255.255.255.240`).
- **Break Step on Host:**
  - IP: `10.1.1.50`
  - Subnet Mask: `255.255.255.240` (Valid range: `10.1.1.48 - 10.1.1.63`)
  - Configured Gateway: `10.1.1.30` (Resides in previous subnet block `10.1.1.16 - 10.1.1.31`)
- **Observed Symptom:** Host cannot reach default gateway or any external network.
- **Show Command:** `ipconfig /all`
- **Expected Fix:** Set Default Gateway to `10.1.1.49`.

---

### 🔬 Scenario 10: Dynamic ARP Inspection Untrusted Trunk (NET-025)
- **Topology:** Switch `SW1` with DAI enabled for VLAN 10, connected to upstream distribution Switch via `Gi0/1`.
- **Break Step on SW1:**
  ```cisco
  ip arp inspection vlan 10
  interface GigabitEthernet0/1
  no ip arp inspection trust
  ```
- **Observed Symptom:** Legitimate clients cannot resolve ARP for router default gateway.
- **Show Command:** `show ip arp inspection interfaces` shows `Gi0/1 Untrusted`.
- **Expected Fix:** `interface GigabitEthernet0/1` -> `ip arp inspection trust`.
