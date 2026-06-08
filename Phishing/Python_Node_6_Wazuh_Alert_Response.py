import requests
import json
import urllib3
# Disable self-signed cert warnings for internal Wazuh
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# --- SHUFFLE BOOLEAN FIX ---
true = True
false = False
null = None
# --- CONFIGURATION ---
WAZUH_URL = "https://YOUR_WAZUH_SERVER_IP:55000" # Your Ubuntu VM IP
API_USER = "wazuh-wui" # Your Wazuh API user
API_PASS = "YOUR_WAZUH_API_PASSWORD_HERE" # Your Wazuh API password
def execute_block(agent_id, target_ip):
    # 1. AUTHENTICATION (Get Token)
    auth_url = f"{WAZUH_URL}/security/user/authenticate"
    try:
        auth_resp = requests.get(auth_url, auth=(API_USER, API_PASS), verify=False)
        if auth_resp.status_code != 200:
            return {"status": "Auth Failed", "code": auth_resp.status_code}
        
        token = auth_resp.json()['data']['token']
        
        # 2. TRIGGER ACTIVE RESPONSE
        ar_url = f"{WAZUH_URL}/active-response?agents_list={agent_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Payload Structure to trigger firewall-drop
        payload = {
            "command": "firewall-drop",
            "alert": {
                "data": {
                    "srcip": target_ip,
                    "description": "Blocked by Shuffle SOAR Phishing Playbook"
                }
            }
        }
        
        resp = requests.put(ar_url, headers=headers, json=payload, verify=False)
        return resp.json()
        
    except Exception as e:
        return {"status": "Execution Error", "details": str(e)}
# --- EXECUTION BLOCK ---
try:
    # 1. Grab the REAL IP directly from the Decision Engine!
    decision_ip = """$decision_engine.message.target_ip"""
    
    # Fallback directly to the webhook just in case
    if not decision_ip or decision_ip.startswith('$'):
        decision_ip = """$exec.ip"""
    # 2. Grab Agent ID (Defaulting to "000" which is the Wazuh Manager itself)
    exec_string = """$exec"""
    def safe_parse(data_string):
        if not data_string or data_string.startswith('$'): return {}
        try: return json.loads(data_string)
        except Exception: return {}
    
    exec_data = safe_parse(exec_string)
    agent_id = exec_data.get("agent", {}).get("id", "000")
    
    # 3. Execute the Block!
    if decision_ip and not decision_ip.startswith('$'):
        result = execute_block(agent_id, decision_ip)
        print(json.dumps({"wazuh_response": result, "blocked_ip": decision_ip}))
    else:
        print(json.dumps({"status": "skipped", "reason": "No valid external IP extracted to block"}))
except Exception as e:
    print(json.dumps({"error": f"Active Response Execution Failed: {str(e)}"}))