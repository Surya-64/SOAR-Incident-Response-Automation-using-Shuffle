# 🛠️ SETUP GUIDE — SOAR Incident Response Automation using Shuffle

> This guide provides a complete, step-by-step walkthrough to reproduce the project environment from scratch.

---

## 🖥️ Lab Environment Overview

| VM | OS | Role | Specs |
|---|---|---|---|
| Node 1 (Security Hub) | Ubuntu 22.04 LTS | Hosts Docker: Wazuh SIEM + Shuffle SOAR | 4 CPU, 10 GB RAM |
| Node 2 (Target Endpoint) | Windows 10/11 | Simulated corporate endpoint with Wazuh Agent | 2 CPU, 4 GB RAM |

**Network:** Both VMs use **Bridged Adapter** in VirtualBox for internet access (external APIs).

---

## PHASE 1: Infrastructure Setup

### 1.1 — Install VirtualBox
Download from: https://www.virtualbox.org/

- Create VM 1: Ubuntu 22.04 LTS, 4 CPU, 10 GB RAM, 100 GB SSD
- Create VM 2: Windows 10/11, 2 CPU, 4 GB RAM, 50 GB SSD
- Set both NICs to **Bridged Adapter**

---

### 1.2 — Install Docker on Ubuntu VM

SSH into Ubuntu VM and run:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER   # Allow non-root docker usage
```

Verify Docker is running:

```bash
sudo docker ps
```

---

## PHASE 2: Deploy Wazuh SIEM

### 2.1 — Clone and Start Wazuh Docker

```bash
git clone https://github.com/wazuh/wazuh-docker.git
cd wazuh-docker/single-node
docker-compose -f generate-indexer-certs.yml run --rm generator
docker-compose up -d
```

### 2.2 — Verify Wazuh is Running

```bash
sudo docker ps
```

You should see containers for: `wazuh.manager`, `wazuh.indexer`, `wazuh.dashboard`

> **Access Wazuh Dashboard:** `https://<Ubuntu_VM_IP>` (port 443)
> **Default login:** `admin` / `SecretPassword`

---

## PHASE 3: Deploy Shuffle SOAR

### 3.1 — Clone and Start Shuffle

```bash
git clone https://github.com/Shuffle/Shuffle
cd Shuffle
mkdir shuffle-database
sudo chown -R 1000:1000 shuffle-database
docker-compose up -d
```

### 3.2 — Verify Shuffle is Running

```bash
sudo docker ps | grep shuffle
```

> **Access Shuffle UI:** `https://<Ubuntu_VM_IP>:3443`

---

## PHASE 4: Install Wazuh Agent on Windows VM

### 4.1 — Run PowerShell as Administrator on Windows VM

```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.x.msi `
    -OutFile wazuh-agent.msi

msiexec.exe /I wazuh-agent.msi /q `
    WAZUH_MANAGER="<Ubuntu_VM_IP>" `
    WAZUH_REGISTRATION_SERVER="<Ubuntu_VM_IP>"

NET START WazuhSvc
```

### 4.2 — Verify Agent in Wazuh Dashboard
- Open Wazuh Dashboard → **Agents** tab
- Windows VM should appear as **Active**

---

## PHASE 5: Configure Wazuh → Shuffle Webhook

### 5.1 — Create Webhook in Shuffle
1. Open Shuffle → **Workflows** → Create New Workflow
2. Drag **Webhook Trigger** node onto the canvas
3. Click the Webhook node → Copy the generated **Webhook URL**

### 5.2 — Edit Wazuh ossec.conf on Ubuntu VM

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add the following block **before** the closing `</ossec_config>` tag:

```xml
<integration>
  <name>shuffle</name>
  <hook_url>http://<Shuffle_IP>:3001/api/v1/hooks/<YOUR_WEBHOOK_ID></hook_url>
  <level>3</level>
  <alert_format>json</alert_format>
  <rule_id>5712,60122,31101,31103,60204,92652,60109</rule_id>
</integration>
```

### 5.3 — Restart Wazuh Manager

```bash
sudo systemctl restart wazuh-manager
```

---

## PHASE 6: Configure Discord Alerting

### 6.1 — Create Discord Webhook
1. Create a Discord server and add a text channel `#soc-alerts`
2. Go to Channel Settings → **Integrations** → **Webhooks** → **New Webhook**
3. Copy the Webhook URL

### 6.2 — Update Discord Nodes in Shuffle
- In each Discord JSON node (in `Bruteforce/` and `Phishing/` and `Malware/`), replace the `DISCORD_WEBHOOK_URL` constant with your URL.

---

## PHASE 7: Configure API Keys

### 7.1 — AbuseIPDB (Free at abuseipdb.com)

In `Bruteforce/Python_Node_2_Analyze_Abuseipdb.py`:
```python
API_KEY = "YOUR_ABUSEIPDB_KEY_HERE"
```

### 7.2 — VirusTotal (Free at virustotal.com)

In `Phishing/Python_Node_2_Analyze_VirusTotal.py`:
```python
VT_API_KEY = "YOUR_VIRUSTOTAL_API_KEY_HERE"
```

### 7.3 — URLScan.io (Free at urlscan.io)

In `Phishing/Python_Node_3_Anayze_urlscan.py`:
```python
URLSCAN_API_KEY = "YOUR_URLSCAN_API_KEY_HERE"
```

### 7.4 — Wazuh API Credentials

In all response nodes:
```python
WAZUH_URL = "https://<Your_Ubuntu_VM_IP>:55000"
API_USER = "wazuh-wui"
API_PASS = "YOUR_WAZUH_PASSWORD"
```

---

## PHASE 8: Import Playbooks into Shuffle

1. Open Shuffle UI at `https://<Ubuntu_VM_IP>:3443`
2. Go to **Workflows** → Create 3 separate workflows:
   - `Bruteforce Response`
   - `Malware Containment`
   - `Phishing Response`
3. For each workflow, add **Python App** nodes and paste the code from the corresponding files in this repository.
4. Connect nodes with transition arrows and set conditional filters on each transition.

---

## PHASE 9: System Startup (After Reboot)

If the host machine is rebooted, restart containers in this order:

```bash
# Navigate to Wazuh docker directory
cd ~/wazuh-docker/single-node
sudo docker-compose up -d

# Navigate to Shuffle directory
cd ~/Shuffle
sudo docker-compose up -d

# Verify all containers are healthy
sudo docker ps
```

---

## PHASE 10: Daily Operations (SOC Analyst Guide)

| Task | Action |
|---|---|
| Monitor Alerts | Watch the Discord `#soc-alerts` channel passively |
| Review Incident | Click the embedded alert; check IP, hostname, confidence score |
| Close Case | Log event in ticketing system (Jira/ServiceNow); no manual block required |
| Audit Executions | Open Shuffle → Workflows → Executions tab |
| Rotate API Keys | Shuffle → Apps → Edit Authentication → Paste new key |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Wazuh agent not showing as active | Restart WazuhSvc on Windows VM; check firewall allows port 1514 UDP |
| Shuffle webhook not receiving data | Verify Wazuh ossec.conf hook_url is correct; restart wazuh-manager |
| VirusTotal rate limit errors | Free tier allows 4 req/min; add `time.sleep(16)` between requests |
| Discord not receiving alerts | Verify webhook URL is correct; check Shuffle HTTP node method is POST |
| Docker containers not starting | Run `sudo docker ps -a` to check logs; `sudo docker logs <container_name>` |
