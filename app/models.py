from pydantic import BaseModel, Field, validator
from typing import Optional

class Node(BaseModel):
    ip: str
    username: str
    password: str
    port: int = Field(default=22, ge=1, le=65535)
    name: Optional[str] = None

class NodeUpdate(BaseModel):
    name: str

class ActionReq(BaseModel):
    ip: str
    action: str
    container_name: str

class DeployBulkReq(BaseModel):
    ip: str
    count: int = Field(default=1, ge=1, le=50)
    proxies: str = ""
    spoof_hw: bool = False

    @validator('proxies')
    def validate_proxies(cls, v):
        import re
        if not re.match(r'^[\w\.\:\/\@\-]*$', v):
            raise ValueError("Invalid characters in proxies")
        return v

class RestartAllReq(BaseModel):
    ip: str

class RenameReq(BaseModel):
    ip: str
    old_name: str
    new_name: str

class LoginReq(BaseModel):
    password: str

class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

class TelegramConfig(BaseModel):
    bot_token: str = ''
    chat_id: str = ''
