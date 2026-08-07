#!/bin/bash
set -e
clear
echo "=========================================================="
echo "    EARNAPP CLUSTER DASHBOARD - AUTO INSTALLER (STB)      "
echo "=========================================================="
echo ""

# 1. Update and Install Python/Pip
echo "[*] Menginstal dependensi sistem (Python & Pip)..."
apt-get update -y
apt-get install -y python3 python3-pip git

# 2. Clone the repository
cd /opt
if [ -f /opt/earnapp-dashboard/nodes.json ]; then
    cp /opt/earnapp-dashboard/nodes.json /tmp/earnapp_nodes_backup.json
    echo '📦 Backup nodes.json berhasil'
fi

if [ -d "/opt/earnapp-dashboard" ]; then
    echo "[*] Menghapus instalasi lama..."
    rm -rf /opt/earnapp-dashboard
fi

echo "[*] Mengunduh source code Dashboard..."
git clone https://github.com/androbuddiesgit/Sistem-Web-Dashboard-EarnApp.git earnapp-dashboard
cd /opt/earnapp-dashboard || exit 1

if [ -f /tmp/earnapp_nodes_backup.json ]; then
    cp /tmp/earnapp_nodes_backup.json /opt/earnapp-dashboard/nodes.json
    echo '📦 Restore nodes.json berhasil'
fi

# 3. Install Python Dependencies
echo "[*] Menginstal Python Library (FastAPI, Uvicorn, Paramiko)..."
pip3 install -r requirements.txt

# 4. Create Systemd Service
echo "[*] Membuat Systemd Service agar Auto-Run saat STB nyala..."
cat << 'EOF' > /etc/systemd/system/earnapp-dashboard.service
[Unit]
Description=EarnApp Cluster Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/earnapp-dashboard
ExecStart=/usr/bin/python3 /opt/earnapp-dashboard/main.py --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 5. Enable and Start Service
systemctl daemon-reload
systemctl enable earnapp-dashboard
systemctl restart earnapp-dashboard

echo ""
echo "=========================================================="
echo " INSTALASI DASHBOARD SELESAI!"
echo "=========================================================="
echo " Buka browser di PC/HP Anda dan ketikkan alamat IP STB ini"
echo " beserta port 8080. Contoh:"
echo " -> http://$(hostname -I | awk '{print $1}'):8080"
echo "=========================================================="
