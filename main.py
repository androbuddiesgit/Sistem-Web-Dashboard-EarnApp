import json
import os
import asyncio
import paramiko
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import re

app = FastAPI(title="EarnApp Dashboard Master")

NODES_FILE = "nodes.json"

class Node(BaseModel):
    ip: str
    username: str
    password: str
    port: int = 22

class ActionReq(BaseModel):
    ip: str
    action: str
    container_name: str

class DeployReq(BaseModel):
    ip: str

def load_nodes():
    if not os.path.exists(NODES_FILE):
        return []
    with open(NODES_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_nodes(nodes):
    with open(NODES_FILE, 'w') as f:
        json.dump(nodes, f, indent=4)

def execute_ssh(ip, username, password, port, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=port, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        client.close()
        return True, out, err
    except Exception as e:
        return False, str(e), ""

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/api/nodes")
def get_nodes():
    nodes = load_nodes()
    # Mask passwords
    for n in nodes:
        n['password'] = "***"
    return nodes

@app.post("/api/nodes")
def add_node(node: Node):
    nodes = load_nodes()
    for n in nodes:
        if n['ip'] == node.ip:
            raise HTTPException(status_code=400, detail="Node already exists")
    nodes.append(node.dict())
    save_nodes(nodes)
    return {"message": "Node added successfully"}

@app.delete("/api/nodes/{ip}")
def remove_node(ip: str):
    nodes = load_nodes()
    nodes = [n for n in nodes if n['ip'] != ip]
    save_nodes(nodes)
    return {"message": "Node removed"}

async def fetch_bots_from_node(node):
    cmd = """docker ps -a --format '{"id":"{{.ID}}", "name":"{{.Names}}", "status":"{{.Status}}", "state":"{{.State}}"}' | grep 'earnapp_' || true"""
    loop = asyncio.get_event_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], cmd)
    bots = []
    if success and out:
        for line in out.splitlines():
            try:
                b = json.loads(line)
                b['node_ip'] = node['ip']
                bots.append(b)
            except:
                pass
    return node['ip'], success, bots, out or err

@app.get("/api/bots")
async def get_bots():
    nodes = load_nodes()
    tasks = [fetch_bots_from_node(n) for n in nodes]
    results = await asyncio.gather(*tasks)
    
    response = []
    for ip, success, bots, err in results:
        response.append({
            "ip": ip,
            "connected": success,
            "error": err if not success else None,
            "bots": bots
        })
    return response

@app.post("/api/bots/action")
async def bot_action(req: ActionReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    allowed_actions = ["start", "stop", "restart", "rm -f"]
    if req.action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    # Prevent shell injection
    if not re.match(r'^earnapp_[0-9]+$', req.container_name):
        raise HTTPException(status_code=400, detail="Invalid container name")

    loop = asyncio.get_event_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], cmd)
    
    if success:
        return {"message": f"Action {req.action} successful", "output": out}
    else:
        raise HTTPException(status_code=500, detail=f"Action failed: {out or err}")

@app.post("/api/bots/deploy")
async def deploy_bot(req: DeployReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Generate UUID and Serial
    rand_hex = uuid.uuid4().hex
    uid = f"sdk-node-{rand_hex}"
    serial = f"{rand_hex}a1b2c3d4"

    # API Registration Command
    reg_cmd = f"curl -s -X POST 'https://client.earnapp.com/install_device?uuid={uid}&version=1.651.510&arch=arm64&appid=node_earnapp.com&os=DBAI-2K25+24.5.1+focal' -H 'Content-Type: application/json' -d '{{\"serial\":\"{serial}\"}}'"
    
    loop = asyncio.get_event_loop()
    succ, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], reg_cmd)
    
    if "ok" not in out.lower():
        raise HTTPException(status_code=500, detail=f"Registration failed: {out} {err}")

    # Determine next container name
    find_cmd = "docker ps -a --format '{{.Names}}' | grep '^earnapp_' | sed 's/earnapp_//' | sort -n | tail -1"
    succ2, out2, err2 = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], find_cmd)
    
    next_id = 1
    if succ2 and out2.strip().isdigit():
        next_id = int(out2.strip()) + 1
        
    container_name = f"earnapp_{next_id}"

    # Run Docker Container
    run_cmd = f"docker run -d --restart always --network host -e EARNAPP_UUID={uid} --name {container_name} fazalfarhan01/earnapp:lite"
    succ3, out3, err3 = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], run_cmd)

    if succ3:
        return {
            "message": "Bot deployed successfully!",
            "uuid": uid,
            "container": container_name,
            "link": f"https://earnapp.com/r/{uid}"
        }
    else:
        raise HTTPException(status_code=500, detail=f"Docker run failed: {out3} {err3}")

@app.get("/api/bots/logs")
async def get_logs(ip: str, container_name: str):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    if not re.match(r'^earnapp_[0-9]+$', container_name):
        raise HTTPException(status_code=400, detail="Invalid container name")
        
    cmd = f"docker logs --tail 50 {container_name}"
    loop = asyncio.get_event_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], node['password'], node['port'], cmd)
    
    if success:
        return {"logs": out or err}
    else:
        raise HTTPException(status_code=500, detail=f"Log fetch failed: {out or err}")

app.mount("/static", StaticFiles(directory="static"), name="static")
