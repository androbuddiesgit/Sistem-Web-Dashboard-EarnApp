from pydantic import BaseModel
from typing import Optional, List

class Node(BaseModel):
    ip: str
    username: str
    password: str
    port: int = 22
    name: Optional[str] = None

class NodeUpdate(BaseModel):
    name: str

class ActionReq(BaseModel):
    ip: str
    action: str
    container_name: str

class DeployBulkReq(BaseModel):
    ip: str
    count: int = 1
    proxies: str = ""
    spoof_hw: bool = False

class RestartAllReq(BaseModel):
    ip: str

class RenameReq(BaseModel):
    ip: str
    old_name: str
    new_name: str
