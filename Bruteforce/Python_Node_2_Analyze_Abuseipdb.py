import requests
import json
# --- THE FIX FOR SHUFFLE JSON INJECTION ---
null = None
NULL = None
true = True
false = False
# --- SHUFFLE INPUT ---
# CHANGE: Pull data from the first node, not the raw webhook
value = $ingest_wazuh_alert 
# --- CONFIGURATION ---
API_KEY = "YOUR_ABUSEIPDB_API_KEY_HERE"
CONFIDENCE_THRESHOLD = 50 
def check_ip_reputation(ip_address):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {'Accept': 'application/json', 'Key': API_KEY}
    querystring = {'ipAddress': ip_address, 'maxAgeInDays': '90', 'verbose': ''}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            
            decision = "MONITOR"
            if score >= CONFIDENCE_THRESHOLD:
                decision = "BLOCK"
            
            return {
                "ip": ip_address,
                "reputation_score": score,
                "decision": decision,
                "success": True 
            }
        return {"error": f"API Error {response.status_code}", "decision": "SKIP", "success": False}
    except Exception as e:
        return {"error": str(e), "decision": "SKIP", "success": False}
# --- EXECUTION ---
try:
    input_data = json.loads(value) if isinstance(value, str) else value
    
    # UNPACK SHUFFLE WRAPPER: Shuffle puts your output inside "message"
    normalized_data = input_data.get("message", input_data)
    target_ip = normalized_data.get("src_ip")
    if target_ip and str(target_ip).lower() != "none" and target_ip != "unknown":
        print(json.dumps(check_ip_reputation(target_ip)))
    else:
        print(json.dumps({"error": "No valid IP provided", "decision": "SKIP", "success": False}))
except Exception as e:
    print(json.dumps({"error": f"Input parsing error: {str(e)}", "success": False}))