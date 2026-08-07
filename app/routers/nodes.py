from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models import Node, NodeUpdate
from app.core.db import load_nodes, save_nodes
from app.core.ssh import execute_ssh
from app.core.crypto import encrypt_value, decrypt_value
from app.core.logger import log_action

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
    node_dict = node.model_dump() if hasattr(node, 'model_dump') else node.dict()
    
    # Test SSH connection
    success, out, err = execute_ssh(node_dict['ip'], node_dict['username'], node_dict['password'], node_dict['port'], "echo 'SSH Connection Successful'")
    if not success:
        raise HTTPException(status_code=400, detail=f"Koneksi SSH Gagal: {out}")
        
    # Auto-Fix Network Configuration for Docker (Silent)
    fix_cmd = "sudo sysctl -w net.ipv4.ip_forward=1 && sudo iptables -P FORWARD ACCEPT"
    execute_ssh(node_dict['ip'], node_dict['username'], node_dict['password'], node_dict['port'], fix_cmd)
    
    node_dict['password'] = encrypt_value(node_dict['password'])
    log_action('ADD_NODE', f'Added node {node_dict["ip"]}', node_dict['ip'])

    nodes.append(node_dict)
    save_nodes(nodes)
    return {"message": "Node added successfully"}

@router.delete("/{ip}")
def remove_node(ip: str):
    nodes = load_nodes()
    nodes = [n for n in nodes if n['ip'] != ip]
    save_nodes(nodes)
    log_action('REMOVE_NODE', f'Removed node {ip}', ip)
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
    decrypted_pw = decrypt_value(node['password'])
    success, out, err = execute_ssh(node['ip'], node['username'], decrypted_pw, node['port'], cmd)
    if not success:
        raise HTTPException(status_code=500, detail=f"Gagal fix network: {err}")
    return {"status": "success", "detail": "Network (IP Forward & iptables) berhasil diperbaiki!"}
