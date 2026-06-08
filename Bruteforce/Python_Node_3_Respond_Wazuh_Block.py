import requests
import json
import urllib3
# Suppress self-signed certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# --- THE FIX FOR SHUFFLE JSON INJECTION ---
null = None
NULL = None
true = True
false = False
# --- SHUFFLE INPUT ---
value = $analyze_abuseipdb 
# --- CONFIGURATION ---
WAZUH_MANAGER = "https://YOUR_WAZUH_SERVER_IP:55000"  # e.g. https://192.168.x.x:55000
USER = "wazuh-wui"
PASSWORD = "YOUR_WAZUH_API_PASSWORD_HERE"
def get_wazuh_token():
    url = f"{WAZUH_MANAGER}/security/user/authenticate"
    try:
        response = requests.get(url, auth=(USER, PASSWORD), verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['token']
        return f"Error_{response.status_code}"
    except Exception as e:
        return f"Conn_Error_{str(e)}"
def trigger_active_response(token, ip_to_block):
    url = f"{WAZUH_MANAGER}/active-response?agents_list=000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "command": "firewall-drop", 
        "alert": {"data": {"srcip": ip_to_block}}
    }
    try:
        response = requests.put(url, headers=headers, json=payload, verify=False, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
# --- EXECUTION ---
try:
    input_data = json.loads(value) if isinstance(value, str) else value
    message = input_data.get("message", input_data)
    target_ip = message.get("ip")
    if target_ip and target_ip != "unknown":
        jwt = get_wazuh_token()
        
        if jwt and not jwt.startswith("Error_") and not jwt.startswith("Conn_Error_"):
            result = trigger_active_response(jwt, target_ip)
            
            # --- UPDATED: Explicitly adding 'reason' for Discord ---
            print(json.dumps({
                "status": "success", 
                "reason": f"IP {target_ip} successfully blocked via firewall-drop on Wazuh Manager",
                "wazuh_response": result
            }))
        else:
            print(json.dumps({
                "status": "failed", 
                "reason": f"Wazuh Auth Failed: {jwt}"
            }))
    else:
        print(json.dumps({
            "status": "skipped", 
            "reason": "No valid IP found in AbuseIPDB data to block"
        }))
        
except Exception as e:
    print(json.dumps({"error": f"Execution failed: {str(e)}"}))
