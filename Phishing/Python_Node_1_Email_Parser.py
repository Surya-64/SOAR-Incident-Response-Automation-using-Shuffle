import re
import email
import hashlib
import json
from urllib.parse import urlparse
# --- SHUFFLE BOOLEAN FIX ---
true = True
false = False
null = None
# --- SHUFFLE INPUT ---
value = $exec
# --- CONSTANTS & REGEX ---
URL_REGEX = r'(https?://[^\s<>"]+?)(?=[.,;:!?]?(?:[\s<>]|$))'
IP_REGEX = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
def is_internal_ip(ip):
    private_prefixes = ('10.', '172.16.', '192.168.', '127.')
    return ip.startswith(private_prefixes)
def extract_observables(raw_content):
    artifacts = {
        "urls": [],
        "domains": [],
        "ips": [],
        "attachments": [],
        "metadata": {}
    }
    if isinstance(raw_content, dict):
        text_content = json.dumps(raw_content)
    else:
        text_content = str(raw_content)
    found_ips = re.findall(IP_REGEX, text_content)
    for ip in found_ips:
        if not is_internal_ip(ip):
            artifacts['ips'].append(ip)
    found_urls = re.findall(URL_REGEX, text_content)
    artifacts['urls'].extend(found_urls)
    artifacts['urls'] = list(set(artifacts['urls']))
    artifacts['ips'] = list(set(artifacts['ips']))
    for url in artifacts['urls']:
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                artifacts['domains'].append(parsed.netloc)
        except Exception:
            pass
            
    artifacts['domains'] = list(set(artifacts['domains']))
    return artifacts
# --- EXECUTION BLOCK ---
try:
    input_data = json.loads(value) if isinstance(value, str) else value
    full_log = input_data.get("text", "") or input_data.get("full_log", "")
    results = extract_observables(full_log)
    print(json.dumps(results))
except Exception as e:
    print(json.dumps({"error": f"Critical Parsing Failure: {str(e)}"}))