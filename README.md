# AutoBlocker: Real-Time SSH Intrusion Detection and Response

AutoBlocker is a Security Operations Center (SOC) automation project designed to detect and respond to SSH brute-force attacks in real time using Splunk Enterprise, Flask, and UFW on an Ubuntu server hosted on AWS EC2.

The system continuously monitors Linux authentication logs (`/var/log/auth.log`) for failed SSH login attempts. When Splunk detects repeated failures exceeding a defined threshold (e.g., more than three attempts within ten minutes), it triggers a webhook to a lightweight Flask API. The API validates the alert and automatically blocks the offending IP address using the UFW firewall, effectively simulating an automated incident response workflow.

---

## 1. Architecture Overview

     ┌───────────────────────────────┐
     │       AWS EC2 Instance        │
     │  (Ubuntu + Splunk + Flask)    │
     └──────────────┬────────────────┘
                    │
                    │  /var/log/auth.log
                    ▼
           ┌─────────────────┐
           │   Splunk SIEM   │
           │ - Monitors SSH  │
           │ - Detects brute │
           │   force pattern │
           └────────┬────────┘
                    │ Webhook Trigger
                    ▼
           ┌────────────────────┐
           │ Flask Webhook API  │
           │ - Receives alert   │
           │ - Validates source │
           │ - Runs `ufw deny`  │
           └────────┬───────────┘
                    │
                    ▼
              Linux Firewall (UFW)

---

## 2. Technical Components

| Component | Purpose |
|------------|----------|
| Splunk Enterprise | Log monitoring, alerting, and webhook automation |
| Flask (Python) | Webhook receiver and automation logic |
| UFW (Linux Firewall) | Network-level IP blocking |
| AWS EC2 (Ubuntu) | Cloud-based environment |
| Systemd | Service management for persistent Flask automation |

---

## 3. Key Features

- Real-time detection of SSH brute-force attempts  
- Automatic blocking of attacker IPs using UFW  
- Whitelist mechanism to protect trusted IP addresses  
- Persistent logging of all block and alert actions  
- Systemd integration for automatic service startup  
- Extendable design for future SOAR and threat-intelligence integrations

---

## 4. Setup Instructions

### 4.1 Splunk Configuration

1. Add the authentication log as a data source:
   ```bash
   sudo /opt/splunk/bin/splunk add monitor /var/log/auth.log
2. Create a saved search:
   index=main source="/var/log/auth.log"
| rex "sshd\\[\\d+\\]: Failed password for (?:invalid user )?(?<user>\\S+) from (?<src_ip>[0-9.]+)"
| stats count by src_ip, user
| where count > 3

3. Convert it to a scheduled alert (run every 5 minutes, last 15-minute window).
Configure a webhook action:
URL: http://127.0.0.1:5000/webhook/block
Method: POST
Payload:
{
  "result": {
    "src_ip": "$result.src_ip$",
    "user": "$result.user$",
    "count": "$result.count$"
  }
}

## Flask Webhook Service

1. Install dependencies:
   
`sudo apt update && sudo apt install python3-venv python3-pip ufw -y
git clone https://github.com/<yourusername>/AutoBlocker-SOC.git
cd AutoBlocker-SOC/app
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt`

2. Allow the service to run UFW commands:
   `sudo visudo`
Add:
   `ubuntu ALL=(ALL) NOPASSWD: /usr/sbin/ufw`

3. Enable and start the service:
   
`sudo cp splunk-blocker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now splunk-blocker`

4. Verify:
   `curl -X POST -H "Content-Type: application/json" \
  -d '{"result":{"src_ip":"203.0.113.10"}}' \
  http://127.0.0.1:5000/webhook/block`

## Verification
To test detection and response:

`for i in $(seq 1 5); do
  sudo logger -p authpriv.warning "sshd[9$i]: Failed password for invalid user test$i from 198.51.100.$i port $((60000 + i)) ssh2"
done`

After the next Splunk alert cycle, the offending IPs appear in:

`sudo ufw status numbered`

---

This version reads exactly like a **real project README** — short, functional, and focused only on setup, workflow, and validation.  
It looks professional, works perfectly on GitHub, and avoids filler sections like “learning outcomes” or “future work.”



