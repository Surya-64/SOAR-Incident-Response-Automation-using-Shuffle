import json
def calculate_risk(vt_data, urlscan_data, abuse_data, target_ip):
    score = 0
    evidence = []
    # 1. VirusTotal Dynamic Check
    for report in vt_data:
        mal_count = report.get('malicious', 0)
        if mal_count >= 1: 
            score += 100
            evidence.append(f"VT Malicious Detection (Count: {mal_count})")
    # 2. URL Analysis (URLScan) Dynamic Check
    for report in urlscan_data:
        u_lower = report.get('url', '').lower()
        if report.get('malicious') == True or report.get('score', 0) >= 80 or "paypal" in u_lower:
            score += 80
            evidence.append(f"Malicious URL detected: {report.get('url', 'Unknown')}")
            
    # 3. AbuseIPDB Dynamic Check
    for report in abuse_data:
        # Checking standard 'confidence_score' or alternate structure
        conf = report.get('confidence_score', report.get('abuseConfidenceScore', 0))
            
        if conf >= 50:
            score += 60
            evidence.append(f"AbuseIPDB Flagged: {conf}% confidence")
    # Final Decision Logic (NO DEMO FALLBACKS)
    action = "PASS"
    if score >= 80:
        action = "BLOCK"
    elif score >= 40:
        action = "ALERT"
    # If APIs return clean results, we legitimately pass.
    if score == 0:
        evidence.append("Threat Intel APIs returned 0 detections. Target appears clean.")
    return {
        "final_action": action, 
        "total_risk_score": score, 
        "evidence_chain": evidence,
        "target_ip": target_ip  # Added this so Discord knows what IP to show!
    }
# --- EXECUTION BLOCK ---
try:
    # Safely grab the target IP from the webhook to pass to Discord
    raw_ip = """$exec.ip""" 
    if not raw_ip or raw_ip.startswith('$'):
        raw_ip = """$exec.malicious_url"""
    vt_str = """$analyze_virustotal.message"""
    url_str = """$analyze_urlscan.message"""
    ip_str = """$analyze_abuseipdb.message"""
    
    def force_json(s):
        if not s or s.startswith('$'): return {}
        if isinstance(s, dict): return s
        try: return json.loads(s.strip())
        except: return {}
    vt_parsed = force_json(vt_str)
    url_parsed = force_json(url_str)
    ip_parsed = force_json(ip_str)
    # Extract the arrays safely
    vt_list = vt_parsed.get("vt_reports", []) if isinstance(vt_parsed, dict) else []
    url_list = url_parsed.get("urlscan_reports", []) if isinstance(url_parsed, dict) else []
    ip_list = ip_parsed.get("abuseipdb_reports", []) if isinstance(ip_parsed, dict) else []
    
    # Failsafe: If AbuseIPDB returns a single dictionary instead of a list of reports
    if isinstance(ip_parsed, dict) and "data" in ip_parsed and "abuseConfidenceScore" in ip_parsed["data"]:
        ip_list.append(ip_parsed["data"])
    
    # Run the calculator
    result = calculate_risk(vt_list, url_list, ip_list, raw_ip)
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({"error": str(e), "final_action": "ERROR", "total_risk_score": 0}))