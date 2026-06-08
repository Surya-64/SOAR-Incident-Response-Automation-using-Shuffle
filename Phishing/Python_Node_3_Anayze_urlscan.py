import requests
import time
import json
import re
# --- SHUFFLE BOOLEAN FIX ---
true = True
false = False
null = None
# --- CONFIGURATION ---
URLSCAN_API_KEY = "YOUR_URLSCAN_API_KEY_HERE"
def submit_and_poll(target_url):
    headers = {
        'API-Key': URLSCAN_API_KEY,
        'Content-Type': 'application/json'
    }
    submit_url = 'https://urlscan.io/api/v1/scan/'
    payload = {"url": target_url, "visibility": "public"}
    
    try:
        req = requests.post(submit_url, headers=headers, json=payload)
        if req.status_code == 429:
            return {"url": target_url, "error": "Rate limited by URLScan"}
        if req.status_code != 200:
            return {"url": target_url, "error": f"Submission failed: {req.status_code}"}
            
        uuid = req.json().get('uuid')
        if not uuid:
            return {"url": target_url, "error": "No UUID returned"}
    except Exception as e:
        return {"url": target_url, "error": str(e)}
    # Polling for results (URLScan can take 10-30 seconds to finish a scan)
    result_url = f"https://urlscan.io/api/v1/result/{uuid}/"
    for attempt in range(12): # Increased slightly to prevent timeout failure
        time.sleep(5)
        poll_req = requests.get(result_url, headers=headers)
        if poll_req.status_code == 200:
            data = poll_req.json()
            verdicts = data.get('verdicts', {})
            overall = verdicts.get('overall', {})
            return {
                "url": target_url,
                "malicious": overall.get('malicious', False),
                "score": overall.get('score', 0),
                "categories": verdicts.get('urlscan', {}).get('categories', []),
                "scan_uuid": uuid
            }
        elif poll_req.status_code == 404:
            continue
        else:
            return {"url": target_url, "error": f"Polling error: {poll_req.status_code}"}
            
    return {"url": target_url, "error": "Scan Timeout - Took too long"}
# --- EXECUTION ---
try:
    # 1. Grab the URL or IP directly from the webhook trigger
    target_url = """$exec.malicious_url"""
    target_ip = """$exec.ip"""
    # 2. Format it properly if malicious_url wasn't provided directly
    if not target_url or target_url.startswith('$'):
        if target_ip and not target_ip.startswith('$'):
            target_url = f"http://{target_ip}"
        else:
            # Fallback: find any URL in the raw webhook
            raw_exec = """$exec"""
            match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_exec)
            if match:
                target_url = match.group(0)
    results = []
    
    # 3. If we successfully found a URL, run the scan!
    if target_url and not target_url.startswith('$'):
        res = submit_and_poll(target_url)
        results.append(res)
        
    print(json.dumps({"urlscan_reports": results}))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))