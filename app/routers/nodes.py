from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models import Node, NodeUpdate
from app.core.db import load_nodes, save_nodes
from app.core.ssh import run_ssh_command

router = APIRouter()

class NodeAction(BaseModel):
    ip: str

@router.get("")
def get_nodes():
    nodes = load_nodes()
    for n in nodes:
        n['password'] = "***"
    return nodes

@router.post("")
def add_node(node: Node):
    nodes = load_nodes()
    for n in nodes:
        if n['ip'] == node.ip:
            raise HTTPException(status_code=400, detail="Node already exists")
    node_dict = node.dict()
    
    # Test SSH connection
    success, out, err = run_ssh_command(node_dict, "echo 'SSH Connection Successful'")
    if not success:
        raise HTTPException(status_code=400, detail=f"Koneksi SSH Gagal: {err}")
        
    # Auto-Fix Network Configuration for Docker (Silent)
    fix_cmd = "sudo sysctl -w net.ipv4.ip_forward=1 && sudo iptables -P FORWARD ACCEPT"
    run_ssh_command(node_dict, fix_cmd)

    nodes.append(node_dict)
    save_nodes(nodes)
    return {"message": "Node added successfully"}

@router.delete("/{ip}")
def remove_node(ip: str):
    nodes = load_nodes()
    nodes = [n for n in nodes if n['ip'] != ip]
    save_nodes(nodes)
    return {"message": "Node removed"}

@router.put("/{ip}")
def update_node(ip: str, update: NodeUpdate):
    nodes = load_nodes()
    for n in nodes:
        if n['ip'] == ip:
            n['name'] = update.name
            save_nodes(nodes)
            return {"message": "Node updated"}
    raise HTTPException(status_code=404, detail="Node not found")

@router.post("/fix_network")
def fix_network(req: NodeAction):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    cmd = "sudo sysctl -w net.ipv4.ip_forward=1 && sudo iptables -P FORWARD ACCEPT"
    success, out, err = run_ssh_command(node, cmd)
    if not success:
        raise HTTPException(status_code=500, detail=f"Gagal fix network: {err}")
    return {"status": "success", "detail": "Network (IP Forward & iptables) berhasil diperbaiki!"}
