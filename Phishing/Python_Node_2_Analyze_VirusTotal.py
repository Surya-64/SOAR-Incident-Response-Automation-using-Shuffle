import requests
import time
import json
import re
# --- SHUFFLE BOOLEAN FIX ---
true = True
false = False
null = None
# --- CONFIGURATION ---
VT_API_KEY = "YOUR_VIRUSTOTAL_API_KEY_HERE"
VT_BASE_URL = "https://www.virustotal.com/api/v3"
def query_ip_reputation(ip):
    """Queries VirusTotal v3 for an IP address reputation."""
    # CHANGED: Endpoint from /files/ to /ip_addresses/
    url = f"{VT_BASE_URL}/ip_addresses/{ip}"
    headers = {"x-apikey": VT_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        
        # RATE LIMIT HANDLING
        if response.status_code == 429:
            time.sleep(16) 
            response = requests.get(url, headers=headers)
            
        if response.status_code == 200:
            data = response.json()
            # Navigate the specific V3 JSON hierarchy
            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            return {
                "ip": ip,
                "malicious": stats.get('malicious', 0),
                "suspicious": stats.get('suspicious', 0),
                "harmless": stats.get('harmless', 0),
                "status": "found"
            }
        elif response.status_code == 404:
            return {"ip": ip, "status": "unknown", "malicious": 0}
        else:
            return {"ip": ip, "error": response.status_code}
    except Exception as e:
        return {"ip": ip, "error": str(e)}
# --- EXECUTION BLOCK ---
try:
    # 1. Grab the IP directly from the webhook trigger
    target_ip = """$exec.ip"""
    
    # Fallback: If exec.ip is empty, use Regex to find the IP in the raw webhook
    if not target_ip or target_ip.startswith('$'):
        raw_exec = """$exec"""
        match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', raw_exec)
        if match:
            target_ip = match.group(0)
    vt_results = []
    
    # 2. If we found an IP, perform the REAL VT scan
    if target_ip and not target_ip.startswith('$'):
        result = query_ip_reputation(target_ip)
        vt_results.append(result)
        
    print(json.dumps({"vt_reports": vt_results}))
    
except Exception as e:
    print(json.dumps({"error": f"VT Execution Failed: {str(e)}"}))