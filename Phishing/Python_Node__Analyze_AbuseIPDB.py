Code : import requests
import json
# --- SHUFFLE BOOLEAN FIX ---
true = True
false = False
null = None
# --- CONFIGURATION ---
# Your free AbuseIPDB API Key
ABUSE_API_KEY = "YOUR_ABUSEIPDB_API_KEY_HERE"
def check_ip_reputation(ip):
    """Queries AbuseIPDB for sender IP reputation over the last 90 days."""
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        'Accept': 'application/json',
        'Key': ABUSE_API_KEY
    }
    params = {
        'ipAddress': ip,
        'maxAgeInDays': '90' 
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        decoded = response.json()
        
        if 'data' in decoded:
            return {
                "ip": ip,
                "confidence_score": decoded['data'].get('abuseConfidenceScore', 0),
                "total_reports": decoded['data'].get('totalReports', 0),
                "usage_type": decoded['data'].get('usageType', 'Unknown')
            }
        return {"ip": ip, "error": "No data"}
        
    except Exception as e:
        return {"ip": ip, "error": str(e)}
# --- EXECUTION ---
try:
    # 1. Grab the IP directly from the webhook trigger, NOT the broken parser!
    target_ip = """$exec.ip"""
    
    # Fallback: If exec.ip is empty, use Regex to find the IP in the raw webhook
    if not target_ip or target_ip.startswith('$'):
        raw_exec = """$exec"""
        match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', raw_exec)
        if match:
            target_ip = match.group(0)
    results = []
    
    # 2. If we found an IP, perform the REAL API scan
    if target_ip and not target_ip.startswith('$'):
        res = check_ip_reputation(target_ip)
        results.append(res)
        
    print(json.dumps({"abuseipdb_reports": results}))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))