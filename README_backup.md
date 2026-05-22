# SOAR Incident Response Automation using Shuffle

This repository contains the advanced Security Orchestration, Automation, and Response (SOAR) playbooks and integration scripts developed for my MCA final semester project.

The playbooks are designed to automate incident response workflows using **Shuffle SOAR**, integrating with tools like **Wazuh XDR**, **Active Directory**, **VirusTotal**, and **Discord** for real-time alerting.

## 🚀 Features & Playbooks

The repository is organized by attack vector, providing automated containment and intelligence gathering for each scenario:

### 1. Malware & Lateral Movement Defense (`/Malware`)
- **Endpoint Isolation:** Automated script (`isolate-host`) to instruct Wazuh API to cut off infected Windows endpoints from the network when critical ransomware or execution rules trigger.
- **Identity Containment:** Python script (`disable_ad_account`) using `ldap3` to automatically disable compromised Active Directory users to prevent lateral movement (e.g., Impacket/PsExec attacks).

### 2. Phishing Analysis (`/Phishing`)
- Automatically extracts URLs and File Hashes from reported phishing emails.
- Integrates with VirusTotal and URLHaus to analyze extracted IoCs.

### 3. Brute Force Mitigation (`/Bruteforce`)
- Automated parsers for SSH, RDP, and SMB failed login attempts.
- Automatically pushes malicious source IPs to the Wazuh Active-Response firewall drop list.

### 4. Advanced SOC Alerting (`/Alerts_and_Notifications`)
- Professionally formatted Discord Webhook templates using JSON Embeds.
- Routes actionable threat intelligence (Rule IDs, Target IPs, Risk Scores) directly to SOC analysts.

## 🛠️ Technology Stack
- **SOAR:** Shuffle (Open Source)
- **XDR/SIEM:** Wazuh
- **Identity:** Microsoft Active Directory (LDAP)
- **Scripting:** Python 3 (Requests, LDAP3)
- **Simulations:** Atomic Red Team, Bash/Powershell

## 📝 Setup & Usage
1. Import the provided Python scripts into your Shuffle Python nodes.
2. Ensure dependencies (e.g., `ldap3`, `requests`) are defined in the node configuration.
3. Replace the placeholder environment variables (`WAZUH_API_URL`, `AD_DOMAIN_CONTROLLER`, `DISCORD_WEBHOOK_URL`) with your actual lab infrastructure IPs and credentials.

---
*Created for an MCA Academic Project focusing on modern Cybersecurity Orchestration.*
