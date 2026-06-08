import os
def check_and_block(data):
    # Fallback to check multiple possible keys from Shuffle
    src_ip = data.get("src_ip") or data.get("ip") 
    vector = data.get("attack_vector") or "Detected Threat"
    
    if not src_ip or src_ip in ["127.0.0.1", "None", None, "unknown"]:
        return "Internal or Unknown IP - No block required."
    
    # In a real production SOAR, this would call an API or SSH
    # For your demo, we will generate the specific command you would run
    block_command = f"sudo ufw insert 1 deny from {src_ip} to any"
    
    return {
        "status": "Success",
        "action": "IP Blocked",
        "command_executed": block_command,
        "target_ip": src_ip,
        "reason": f"Automated response to {vector}"
    }