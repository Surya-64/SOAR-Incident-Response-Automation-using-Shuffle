import requests
import json
import urllib3
import sys
# Suppress self-signed certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# --- SHUFFLE BOOLEAN FIX ---
null = None
NULL = None
true = True
false = False  # Fixed: Removed the invalid "False = False" line
# --- SHUFFLE INPUT ---
try:
    value = $exec
except NameError:
    value = {}
# --- CONFIGURATION ---
WAZUH_MANAGER = "https://YOUR_WAZUH_SERVER_IP:55000" 
USER = "wazuh-wui"
PASSWORD = "YOUR_WAZUH_API_PASSWORD_HERE"
def get_wazuh_token():
    """Authenticates and retrieves a JWT token"""
    url = f"{WAZUH_MANAGER}/security/user/authenticate"
    try:
        response = requests.get(url, auth=(USER, PASSWORD), verify=False, timeout=10)
        if response.status_code != 200:
            response = requests.post(url, auth=(USER, PASSWORD), verify=False, timeout=10)
            
        if response.status_code == 200:
            return response.json()['data']['token']
        return None
    except Exception:
        return None
def get_agent_id(token, agent_name):
    """Converts Agent Name to Agent ID"""
    if not agent_name or agent_name == "unknown" or agent_name == "soar-VirtualBox":
        return "000"  # Fallback to 000 (Wazuh Manager itself) if it's the local host VM
    url = f"{WAZUH_MANAGER}/agents?q=name={agent_name}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        data = response.json()
        
        items = data.get('data', {}).get('affected_items', [])
        if items:
            return items[0]['id']
            
        return "000" 
    except:
        return "000"
def trigger_active_response(token, agent_id, ip_to_block):
    """Triggers the firewall-drop command"""
    url = f"{WAZUH_MANAGER}/active-response?agents_list={agent_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "command": "firewall-drop", 
        "custom": False,  # Strictly True/False native booleans
        "alert": {
            "data": {
                "srcip": ip_to_block
            }
        }
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, verify=False, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
# --- EXECUTION ---
try:
    inputs = json.loads(value) if isinstance(value, str) else value
    if not isinstance(inputs, dict):
        # Unwrap Shuffle inner message wrapper if it passed straight through
        inputs = inputs.get("message", {}) if hasattr(inputs, "get") else {}
    
    # Extract structural variables safely
    target_ip = inputs.get("ip") or inputs.get("src_ip")
    agent_name = inputs.get("target_machine") 
    if target_ip and str(target_ip).lower() != "none" and target_ip != "unknown":
        jwt = get_wazuh_token()
        if jwt:
            agent_id = get_agent_id(jwt, agent_name)
            result = trigger_active_response(jwt, agent_id, target_ip)
            
            # Formulating output
            output_data = {
                "status": "success", 
                "ip": target_ip,
                "agent_id": agent_id,
                "wazuh_response": result
            }
            sys.stdout.write(json.dumps(output_data))
        else:
            sys.stdout.write(json.dumps({"status": "failed", "reason": "Wazuh Auth Failed"}))
    else:
        sys.stdout.write(json.dumps({"status": "skipped", "reason": "No valid IP to block"}))
        
except Exception as e:
    sys.stdout.write(json.dumps({"status": "failed", "error": f"Execution failed: {str(e)}"}))