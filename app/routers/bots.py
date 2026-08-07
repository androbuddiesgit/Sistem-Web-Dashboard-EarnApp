import asyncio
import json
import re
from fastapi import APIRouter, HTTPException
from app.models import ActionReq, RestartAllReq, RenameReq
from app.core.db import load_nodes
from app.core.ssh import execute_ssh
from app.core.crypto import decrypt_value
from app.core.logger import log_action

router = APIRouter()

async def fetch_bots_from_node(node):
    cmd = """docker ps -a --format '{"id":"{{.ID}}", "name":"{{.Names}}", "status":"{{.Status}}", "state":"{{.State}}"}' --filter "ancestor=fazalfarhan01/earnapp:lite" """
    loop = asyncio.get_running_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    bots = []
    if success and out:
        for line in out.splitlines():
            try:
                b = json.loads(line)
                b['node_ip'] = node['ip']
                bots.append(b)
            except (json.JSONDecodeError, ValueError):
                pass
    return node['ip'], success, bots, out or err, node.get('name', '')

@router.get("")
async def get_bots():
    nodes = load_nodes()
    tasks = [fetch_bots_from_node(n) for n in nodes]
    results = await asyncio.gather(*tasks)
    
    response = []
    for ip, success, bots, err, name in results:
        response.append({
            "ip": ip,
            "name": name,
            "connected": success,
            "error": err if not success else None,
            "bots": bots
        })
    return response

@router.post("/action")
async def bot_action(req: ActionReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    allowed_actions = ["start", "stop", "restart", "rm -f"]
    if req.action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    if not re.match(r'^[a-zA-Z0-9_-]+$', req.container_name):
        raise HTTPException(status_code=400, detail="Invalid container name")

    loop = asyncio.get_running_loop()
    cmd = f"docker {req.action} {req.container_name}"
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    
    if success:
        log_action('BOT_ACTION', f'{req.action} on {req.container_name}', req.ip)
        return {"message": f"Action {req.action} successful", "output": out}
    else:
        raise HTTPException(status_code=500, detail=f"Action failed: {out or err}")

@router.post("/restart_all")
async def restart_all_bots(req: RestartAllReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    cmd = "docker restart $(docker ps -a -q --filter 'ancestor=fazalfarhan01/earnapp:lite') || true"
    loop = asyncio.get_running_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    log_action('RESTART_ALL_BOTS', 'Restarted all bots', req.ip)
    return {"message": "Restart all initiated", "output": out or err}

@router.post("/rename")
async def rename_bot(req: RenameReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    if not re.match(r'^[a-zA-Z0-9_-]+$', req.old_name) or not re.match(r'^[a-zA-Z0-9_-]+$', req.new_name):
        raise HTTPException(status_code=400, detail="Invalid container name format")
        
    cmd = f"docker rename {req.old_name} {req.new_name}"
    loop = asyncio.get_running_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    
    if success:
        log_action('RENAME_BOT', f'Renamed {req.old_name} to {req.new_name}', req.ip)
        return {"message": "Rename successful"}
    else:
        raise HTTPException(status_code=500, detail=f"Rename failed: {out or err}")

@router.get("/logs")
async def get_logs(ip: str, container_name: str):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    if not re.match(r'^[a-zA-Z0-9_-]+$', container_name):
        raise HTTPException(status_code=400, detail="Invalid container name")
        
    cmd = f"docker logs --tail 50 {container_name}"
    loop = asyncio.get_running_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    
    if success:
        return {"logs": out or err}
    else:
        raise HTTPException(status_code=500, detail=f"Log fetch failed: {out or err}")

@router.get("/ip")
async def get_bot_ip(ip: str, container_name: str):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    if not re.match(r'^[a-zA-Z0-9_-]+$', container_name):
        raise HTTPException(status_code=400, detail="Invalid container name")
        
    loop = asyncio.get_running_loop()
    
    cmd1 = f"docker exec {container_name} wget -qO- -T 5 ifconfig.me/ip"
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd1)
    if success and out and ("." in out or ":" in out) and "<html" not in out.lower():
        return {"public_ip": out.strip()}

    cmd2 = f"docker exec {container_name} curl -s -m 5 ifconfig.me/ip"
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd2)
    if success and out and ("." in out or ":" in out) and "<html" not in out.lower():
        return {"public_ip": out.strip()}

    cmd3 = "curl -s -m 5 ifconfig.me/ip || wget -qO- -T 5 ifconfig.me/ip"
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd3)
    if success and out and ("." in out or ":" in out) and "<html" not in out.lower():
        return {"public_ip": out.strip() + " (Host IP)"}
            
    raise HTTPException(status_code=500, detail="Semua metode gagal. Kemungkinan jaringan terputus.")
