from flask import Flask, request, jsonify
import subprocess, json, datetime

app = Flask(__name__)

WHITELIST = ["127.0.0.1", "13.51.72.144"]  # your own instance IPs
LOG_FILE = "/var/log/splunk-blocker.log"

def log_event(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.utcnow()} {msg}\n")

@app.route("/webhook/block", methods=["POST"])
def webhook_block():
    data = request.get_json()
    ip = data.get("result", {}).get("src_ip")
    if not ip:
        return jsonify({"ok": False, "error": "Missing src_ip"}), 400
    if ip in WHITELIST:
        log_event(f"WHITELISTED {ip}")
        return jsonify({"ok": True, "status": "whitelisted"})

    try:
        subprocess.check_call(["sudo", "/usr/sbin/ufw", "insert", "1", "deny", "from", ip, "to", "any"])
        log_event(f"BLOCKED {ip}")
        return jsonify({"ok": True, "status": "blocked"})
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            log_event(f"ALREADY_EXISTS {ip}")
            return jsonify({"ok": True, "status": "already_exists"})
        log_event(f"ERROR {ip} {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
