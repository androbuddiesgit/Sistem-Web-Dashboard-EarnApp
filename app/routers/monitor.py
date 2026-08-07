import asyncio
from fastapi import APIRouter, HTTPException
from app.core.db import load_nodes
from app.core.ssh import execute_ssh

router = APIRouter()

@router.get("")
async def get_system_monitor():
    nodes = load_nodes()
    
    async def fetch_monitor(node):
        # 1. CPU Usage (from top)
        # 2. RAM Usage (from free -m)
        # 3. Temp (from /sys/class/thermal/thermal_zone0/temp)
        cmd = """
        echo "CPU: $(top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}')"
        echo "RAM: $(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')"
        if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
            echo "TEMP: $(awk '{print $1/1000}' /sys/class/thermal/thermal_zone0/temp)"
        else
            echo "TEMP: N/A"
        fi
        """
        loop = asyncio.get_event_loop()
        success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], cmd)
        
        data = {"cpu": "0", "ram": "0", "temp": "N/A"}
        if success and out:
            for line in out.splitlines():
                if line.startswith("CPU:"): data["cpu"] = line.split(":", 1)[1].strip()
                elif line.startswith("RAM:"): data["ram"] = line.split(":", 1)[1].strip()
                elif line.startswith("TEMP:"): data["temp"] = line.split(":", 1)[1].strip()
                
        return {"ip": node["ip"], "success": success, "data": data}

    tasks = [fetch_monitor(n) for n in nodes]
    results = await asyncio.gather(*tasks)
    return results
