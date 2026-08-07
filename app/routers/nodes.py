from fastapi import APIRouter, HTTPException
from app.models import Node, NodeUpdate
from app.core.db import load_nodes, save_nodes

router = APIRouter()

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
    nodes.append(node.dict())
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
