def check_phishtank(url):
    # PhishTank often requires a user-agent to avoid blocks
    headers = {'User-Agent': 'Shuffle-SOAR-Bot/1.0'}
    endpoint = "https://checkurl.phishtank.com/checkurl/"
    payload = {
        "url": url,
        "format": "json"
    }
    
    try:
        # PhishTank uses POST for checks
        req = requests.post(endpoint, data=payload, headers=headers)
        data = req.json()
        
        if 'results' in data:
             # The key in 'results' is the URL itself, sometimes normalized
             # We iterate to find the match
             for key, val in data['results'].items():
                 if val.get('in_database'):
                     return {"url": url, "phishtank_valid": val.get('valid', False)}
        
        return {"url": url, "phishtank_found": False}
    except Exception:
        return {"url": url, "error": "Check failed"}