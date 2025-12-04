# ucs-threshold-monitor

Monitors Cisco UCS threshold-crossed events and alerts via email.

Since `threshold-crossed` events do [not trigger call-home alerts](https://bst.cisco.com/quickview/bug/CSCwf25809), this will do it for you.

## Install

Get it
```bash
git clone https://github.com/lwarnt/ucs-threshold-monitor.git
cd ucs-threshold-monitor
```

Install requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the service file

```bash
wd=$(pwd)
cat >/etc/systemd/system/ucs_threshold_monitor.service <<EOF
[Unit]
Description=UCS Threshold Crossed Monitor
After=network.target

[Service]
Type=simple
WorkingDirectory=$wd
ExecStart=$wd/venv/bin/python $wd/monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

chmod +x monitor.py

systemctl daemon-reload
systemctl enable ucs_threshold_monitor.service
systemctl start ucs_threshold_monitor.service
```

## UCS configuration example

```
Servers > Policies > root > Threshold Policies > thr-policy-default 
    Add > Create Threshold Class
        Choose Statistics Class
            > processor
            > Cpu Env Stats
    Next >
        Threshold Definitions
            Add > Cpu Env Stats Temperature Avg
                > Major: UP=75,DOWN=70
```
