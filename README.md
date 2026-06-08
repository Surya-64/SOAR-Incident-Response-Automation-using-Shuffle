<div align="center">

# 🛡️ SOAR Incident Response Automation using Shuffle

---

![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)
![Platform](https://img.shields.io/badge/SOAR-Shuffle-blue?style=for-the-badge)
![SIEM](https://img.shields.io/badge/SIEM-Wazuh-red?style=for-the-badge)
![Containerization](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![Language](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python)
![MTTR Reduction](https://img.shields.io/badge/MTTR%20Reduction-90%25-success?style=for-the-badge)

</div>

---

## 📖 Abstract

In the contemporary cybersecurity landscape, Security Operations Centers (SOCs) are consistently overwhelmed by an exponential volume of security alerts — a phenomenon termed **"alert fatigue"**. This forces analysts to spend disproportionate time on manual triage, enrichment, and repetitive tasks, dangerously prolonging the **Mean Time to Respond (MTTR)** to genuine threats.

This project proposes and implements a **Security Orchestration, Automation, and Response (SOAR)** framework using **Shuffle** — a robust, open-source automation platform — integrated with **Wazuh SIEM**. The system automates the incident response lifecycle for three high-frequency attack vectors:

- 🔐 **Brute-Force Authentication Attacks** (SSH, RDP/SMB, Web SQLi)
- ☣️ **Malware Infections** (File Drop, Identity Compromise)
- 🎣 **Phishing Campaigns** (URL/IP extraction, email analysis)

> **Key Result:** Automated MTTR reduced from **~35 minutes (manual)** to **~3.5 minutes (automated)** — a **90% reduction**.

---

## 🏗️ System Architecture

The architecture follows a **centralized, API-driven hub-and-spoke model** across four logical layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: DETECTION & INGESTION               │
│         Wazuh SIEM (Windows Endpoint + Ubuntu Linux Agent)       │
│              Monitors: SSH, RDP/SMB, Web Logs, File Hashes       │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/HTTPS Webhook (JSON Payload)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 LAYER 2: ORCHESTRATION (Shuffle SOAR)           │
│         Parses JSON → Triggers Playbook → Executes Logic         │
│   Components: Frontend (React) | Backend (Go) | Orborus (Worker) │
└──────────┬──────────────────────────────────┬───────────────────┘
           │ REST API Queries                  │ Enriched Decision
           ▼                                  ▼
┌─────────────────────┐           ┌───────────────────────────────┐
│  LAYER 3: INTEL &   │           │   LAYER 4: RESPONSE &         │
│  ENRICHMENT         │           │   NOTIFICATION                │
│                     │           │                               │
│  • VirusTotal API   │           │  • Wazuh Active Response      │
│  • AbuseIPDB API    │           │    (firewall-drop command)    │
│  • URLScan.io API   │           │  • Endpoint Isolation         │
│                     │           │  • AD Account Lockout (LDAP)  │
│  Returns risk scores│           │  • Discord SOC Alert Webhook  │
└─────────────────────┘           └───────────────────────────────┘
```

### Deployment Environment

| Node | OS | Role | Resources |
|---|---|---|---|
| **Node 1 (Ubuntu VM)** | Ubuntu 22.04 LTS | Docker Host: Wazuh Manager + Shuffle SOAR | 4 CPU, 10GB RAM |
| **Node 2 (Windows VM)** | Windows 10/11 | Target Endpoint with Wazuh Agent | 2 CPU, 4GB RAM |

Both VMs run inside **Oracle VirtualBox** using a **Bridged Adapter** network for external API access.

---

## 🎯 Project Objectives

| # | Objective | Status |
|---|---|---|
| 1 | Centralize security orchestration using Shuffle as an automated hub | ✅ |
| 2 | Automate threat intelligence enrichment via VirusTotal and AbuseIPDB APIs | ✅ |
| 3 | Develop automated playbooks for Phishing, Brute-Force, and Malware | ✅ |
| 4 | Reduce Mean Time to Respond (MTTR) by 90%+ | ✅ |
| 5 | Mitigate operational alert fatigue with automated filtering | ✅ |
| 6 | Establish standardized, codified security operating procedures | ✅ |

---

## 📂 Repository Structure

```
SOAR-Incident-Response-Automation-using-Shuffle/
│
├── 📄 README.md                        ← Project overview & documentation
├── 📄 SETUP.md                         ← Step-by-step environment setup guide
│
├── 📁 Bruteforce/                      ← Brute-Force Attack Playbook Nodes
│   ├── Python_Node_1_Ingest_Wazuh_Alert.py      # Parses Wazuh alert JSON, extracts IPs
│   ├── Python_Node_2_Analyze_Abuseipdb.py       # Queries AbuseIPDB for IP reputation
│   ├── Python_Node3_Respond_Wazuh_Block.py      # Triggers Wazuh firewall-drop via API
│   ├── Python_Node_4_Respond_Network_Defence.py # Dynamic agent resolution + block
│   ├── Python_Node_5_Firewall_Block.py          # UFW firewall block generator
│   ├── Discord_Node_4_Discord_Alert(SMB).json   # RDP/SMB attack alert payload
│   ├── Discord_Node_5_Discord_Alert_(Web).json  # Web Application attack alert payload
│   └── Discord_Node_6_Discord_Alert(SSH).json   # SSH brute-force alert payload
│
├── 📁 Malware/                         ← Malware Attack Playbook Nodes
│   ├── Python_Node_1_Ingest_Wazuh_Alert.py      # Parses Wazuh alert, detects malware rules
│   ├── Python_Node_2Isolate_Endpoint.py         # Wazuh Active Response: restart-ossec0
│   ├── Python_Node_3_Contain_Identity.py        # LDAP3: disables AD user account
│   └── Discord_Node_1_Malware_Alert.json        # Critical malware Discord embed
│
└── 📁 Phishing/                        ← Phishing Response Playbook Nodes
    ├── Python_Node_1_Email_Parser.py            # Extracts URLs, IPs, domains from email
    ├── Python_Node_2_Analyze_VirusTotal.py      # Queries VirusTotal v3 IP reputation
    ├── Python_Node_3_Anayze_urlscan.py          # Submits URLs to URLScan.io for analysis
    ├── Python_Node__Analyze_AbuseIPDB.py        # AbuseIPDB cross-check for phishing IPs
    ├── Python_Node_5_Decision_Engine.py         # Aggregates scores → final BLOCK/MONITOR
    ├── Python_Node_6_Wazuh_Alert_Response.py    # Fires Wazuh firewall-drop for phishing
    └── Python_Node_7_Client_Discord_Node.json   # Rich SOC Autobot Discord embed
```

---

## ⚙️ Environment Setup & Installation

### Prerequisites

| Software | Version | Purpose |
|---|---|---|
| Oracle VirtualBox | Latest | Hypervisor for VMs |
| Ubuntu Linux | 22.04 LTS | Host for Docker containers |
| Windows 10/11 | 64-bit | Simulated target endpoint |
| Docker Engine | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.9+ | Shuffle node execution engine |

### Hardware Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU Cores | 4 Cores | 8 Cores |
| RAM | 8 GB | 16 GB |
| Storage | 100 GB SSD | 400 GB SSD |
| Network | Stable Broadband | Stable Broadband |

### Step 1 — Install Docker on Ubuntu VM

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

### Step 2 — Deploy Wazuh SIEM (Docker)

```bash
git clone https://github.com/wazuh/wazuh-docker.git
cd wazuh-docker/single-node
docker-compose -f generate-indexer-certs.yml run --rm generator
docker-compose up -d
```

> Wazuh Dashboard accessible at `https://<Ubuntu_VM_IP>:443`
> Default credentials: `admin / SecretPassword`

### Step 3 — Deploy Shuffle SOAR (Docker)

```bash
git clone https://github.com/Shuffle/Shuffle
cd Shuffle
mkdir shuffle-database
sudo chown -R 1000:1000 shuffle-database
docker-compose up -d
```

> Shuffle UI accessible at `https://<Ubuntu_VM_IP>:3443`

### Step 4 — Install Wazuh Agent on Windows Endpoint

Run the following in an **elevated PowerShell** on the Windows VM:

```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.x.msi -OutFile wazuh-agent.msi
msiexec.exe /I wazuh-agent.msi /q WAZUH_MANAGER="<Ubuntu_VM_IP>" WAZUH_REGISTRATION_SERVER="<Ubuntu_VM_IP>"
NET START WazuhSvc
```

### Step 5 — Configure Wazuh → Shuffle Webhook

Add the following block to `/var/ossec/etc/ossec.conf` on the Ubuntu VM:

```xml
<integration>
  <name>shuffle</name>
  <hook_url>http://<Shuffle_IP>:3001/api/v1/hooks/<YOUR_WEBHOOK_ID></hook_url>
  <level>3</level>
  <alert_format>json</alert_format>
  <rule_id>5712,60122,31101,31103,60204,92652,60109</rule_id>
</integration>
```

```bash
sudo systemctl restart wazuh-manager
```

### Step 6 — Configure Discord Notifications

1. In your Discord server, create a channel `#soc-alerts`.
2. Go to **Channel Settings → Integrations → Webhooks → New Webhook**.
3. Copy the Webhook URL and paste it into the Discord nodes within each Shuffle playbook.

---

## 🔁 Playbook Workflows

### 1. 🔐 Brute-Force Authentication Playbook

**Trigger:** Wazuh detects repeated failed logins (Rule IDs: `5716`, `5710`, `60122`, `4625`, `31103`)

```
Webhook (Wazuh Alert)
    │
    ▼
[Node 1] Ingest Wazuh Alert
    │  Extract: rule_id, src_ip, attack_vector, target_user
    ▼
[Node 2] Analyze AbuseIPDB
    │  Query IP reputation → abuseConfidenceScore ≥ 50 → BLOCK
    ▼
[Node 3] Respond Wazuh Block
    │  POST /active-response → firewall-drop command on Wazuh Manager
    ▼
[Node 4] Respond Network Defence
    │  Resolve agent_id → trigger targeted block on specific endpoint
    ▼
[Node 5] Firewall Block
    │  Generate: sudo ufw insert 1 deny from <IP> to any
    ▼
[Discord] SOC Alert (SMB / Web / SSH variants)
    └  Sends formatted embed to #soc-alerts channel
```

**Wazuh Rule IDs Covered:**
| Rule ID | Attack Type |
|---|---|
| 5760, 5763, 5716, 5710–5712 | SSH Brute Force (Linux) |
| 60122, 4625, 60204 | RDP/SMB Brute Force (Windows) |
| 31103, 31101 | Web Application SQLi Brute Force |

---

### 2. ☣️ Malware Containment Playbook

**Trigger:** Wazuh detects malware signatures (Rule IDs: `92652`, `60109`, `60204`)

```
Webhook (Wazuh Alert)
    │
    ▼
[Node 1] Ingest Wazuh Alert
    │  Detect: Malware - File Drop / Identity (SHA256 hash, SysmonSimulator)
    ▼
[Node 2] Isolate Endpoint
    │  POST /active-response?agents_list=<agent_id>
    │  Command: restart-ossec0 (triggers isolation on host)
    ▼
[Node 3] Contain Identity
    │  LDAP3 connection → disables compromised AD user account
    │  Sets userAccountControl flag (bit 2 = disabled)
    ▼
[Discord] Critical Malware Alert
    └  Embeds: Rule ID, Target User, Machine, Containment Status
```

---

### 3. 🎣 Phishing Response Playbook

**Trigger:** Webhook from email gateway or Wazuh with phishing indicators

```
Webhook (Email/Wazuh Alert)
    │
    ▼
[Node 1] Email Parser
    │  Regex extract: URLs, IPs, domains from email body
    ▼
    ├──[Node 2] Analyze VirusTotal → IP reputation (malicious/suspicious count)
    ├──[Node 3] Analyze URLScan.io → Submit URL scan, poll for verdict
    └──[Node 4] Analyze AbuseIPDB → abuseConfidenceScore for extracted IPs
    │
    ▼
[Node 5] Decision Engine (Python)
    │  Aggregate: VT malicious score + URL verdict + AbuseIPDB score
    │  total_risk_score → BLOCK (>threshold) or MONITOR
    ▼
[Node 6] Wazuh Alert Response
    │  If BLOCK: POST firewall-drop to specific Wazuh Agent
    ▼
[Node 7] Client Discord Node (SOC Autobot)
    └  Rich embed: Sender, Subject, URL, Risk Score, Containment Status, Evidence Chain
```

---

## 📊 Performance Metrics & Results

### Playbook Execution Time Breakdown

| Phase | Component | Average Duration |
|---|---|---|
| Detection & Forwarding | Wazuh SIEM | 10 – 15 seconds |
| Ingestion & Parsing | Shuffle Orchestrator | 05 – 10 seconds |
| Intelligence Enrichment | VirusTotal / AbuseIPDB | 2.5 – 3.0 minutes |
| Evaluation & Containment | Shuffle Worker + Firewall | 15 – 20 seconds |
| Notification Delivery | Discord Webhook | 05 seconds |
| **Total MTTR** | **End-to-End Pipeline** | **~3.5 minutes** |

### MTTR Comparison: Manual vs. Automated

| Incident Response Phase | Manual (Human Analyst) | Automated (Shuffle SOAR) |
|---|---|---|
| Alert Acknowledgment | ~03 Minutes | ~05 Seconds |
| Data Extraction (IOCs) | ~02 Minutes | ~05 Seconds |
| Context Gathering (API Queries) | ~15 Minutes | ~2.5 Minutes |
| Remediation (Firewall Block) | ~10 Minutes | ~15 Seconds |
| Incident Reporting & Alerting | ~05 Minutes | ~05 Seconds |
| **Total MTTR** | **~35 Minutes** | **~3.5 Minutes** |

> ### 🏆 90% Reduction in Mean Time to Respond (MTTR)

---

## ✅ Test Case Results

| Test Case | Scenario | Result |
|---|---|---|
| TC-01 | Wazuh Webhook Ingestion | ✅ PASS |
| TC-02 | IOC Data Extraction (JSONPath) | ✅ PASS |
| TC-03 | API Data Enrichment (VirusTotal) | ✅ PASS |
| TC-04 | Conditional Branching — Malicious IP (Score ≥ 2) | ✅ PASS |
| TC-05 | Conditional Branching — Benign/Internal IP (Score = 0) | ✅ PASS |
| TC-06 | Discord Alert Generation with Dynamic Variables | ✅ PASS |

---

## 🔧 Integrations & API Configuration

### Required API Keys

| Service | Purpose | Free Tier | Config Location |
|---|---|---|---|
| [AbuseIPDB](https://www.abuseipdb.com/) | IP reputation scoring | ✅ Yes | `Bruteforce/Python_Node_2_Analyze_Abuseipdb.py` |
| [VirusTotal](https://www.virustotal.com/) | IP/URL/Hash reputation | ✅ Yes (4 req/min) | `Phishing/Python_Node_2_Analyze_VirusTotal.py` |
| [URLScan.io](https://urlscan.io/) | URL sandbox analysis | ✅ Yes | `Phishing/Python_Node_3_Anayze_urlscan.py` |
| [Discord Webhook](https://discord.com/developers/docs/resources/webhook) | SOC alerting | ✅ Free | Discord Nodes (JSON files) |

### Wazuh API Configuration

Update the following in Python nodes where applicable:

```python
WAZUH_URL = "https://<Your_Ubuntu_VM_IP>:55000"
API_USER = "wazuh-wui"
API_PASS = "YOUR_WAZUH_API_PASSWORD_HERE"   # Change this in production!
```

### Conditional Logic (Shuffle Transition Filter)

In the Brute-Force playbook, the remediation path is gated by:

```
#VirusTotal_IP_Check.attributes.last_analysis_stats.malicious >= 2
```

For AbuseIPDB:

```
#analyze_abuseipdb.message.reputation_score >= 50
```

### Variable Mapping (JSONPath Syntax)

Data is passed dynamically between nodes using Shuffle's variable syntax:

```
$exec.text.data.srcip          ← Source IP from Wazuh webhook
$ingest_wazuh_alert.message    ← Parsed output from Node 1
$analyze_abuseipdb.message     ← Enrichment result from AbuseIPDB node
```

---

## 🧠 Technical Design Summary

### Software Development Model
The project followed **Agile Methodology** across 4 sprints:

| Sprint | Focus | Deliverable |
|---|---|---|
| Sprint 1 | Infrastructure | Docker + Wazuh + Shuffle deployed and running |
| Sprint 2 | Ingestion Pipeline | Wazuh ossec.conf webhook forwarding active |
| Sprint 3 | Intelligence Routing | IOC extraction + AbuseIPDB integration working |
| Sprint 4 | Remediation & Notification | Firewall block + Discord alerts functional |

### Shuffle Architecture Components

| Component | Technology | Role |
|---|---|---|
| Frontend (UI Canvas) | React.js | Visual drag-and-drop playbook builder |
| Backend Orchestrator | Golang | Manages playbook state, routes webhooks |
| Orborus (Worker Nodes) | Python (Docker) | Executes API calls and Python scripts |
| Database | OpenSearch | Stores execution logs and incident history |

---

## ⚠️ Known Limitations

1. **API Rate Limiting:** Free-tier VirusTotal (4 req/min) and AbuseIPDB APIs add ~2.5 min to enrichment phase. Upgrade to premium keys for sub-second enrichment.
2. **Virtualization Bottleneck:** All services run on a single VirtualBox host. Production deployments should use distributed bare-metal or cloud servers.
3. **Playbook Scope:** Currently handles 3 attack vectors. Complex APTs, DDoS, and zero-days require manual analysis.
4. **No Automated Rollback:** False-positive firewall blocks require manual reversal by an analyst.

---

## 🚀 Future Enhancements

- [ ] **AI/LLM Integration:** Use LLMs to dynamically generate remediation scripts for zero-day threats and auto-draft forensic reports.
- [ ] **Cloud Expansion:** Extend detection to AWS, Azure, GCP — automate IAM credential revocation and cloud storage isolation.
- [ ] **EDR Integration:** Deep integration with CrowdStrike/SentinelOne for host-level process termination and memory forensics.
- [ ] **Proactive Threat Hunting:** Scheduled playbooks that pull daily IOCs from CISA feeds and proactively hunt in Wazuh logs.
- [ ] **Automated Rollback:** Implement time-based automatic unblock for quarantined IPs after analyst review.

---

## 📚 Key References

- [NIST SP 800-61r2 — Computer Security Incident Handling Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)
- [Shuffle SOAR Official Docs](https://shuffler.io/docs/about)
- [Wazuh Documentation](https://documentation.wazuh.com/current/index.html)
- [VirusTotal API v3](https://docs.virustotal.com/reference/overview)
- [AbuseIPDB API v2](https://docs.abuseipdb.com/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [IBM Cost of a Data Breach Report 2024](https://www.ibm.com/reports/data-breach)

---

## 👤 Author

This project was developed as a Final Year Major Project for the award of the degree of **Master of Computer Applications**.

[![GitHub](https://img.shields.io/badge/GitHub-Surya--64-181717?style=flat&logo=github)](https://github.com/Surya-64)

---

<div align="center">

*Built with ❤️ for the cybersecurity community — automating defense at machine speed.*

</div>
