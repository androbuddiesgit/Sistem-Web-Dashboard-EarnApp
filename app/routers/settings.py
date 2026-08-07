import asyncio
import urllib.request
import urllib.parse
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models import TelegramConfig
from app.core.auth import get_telegram_config, save_telegram_config
from app.core.db import load_nodes, save_nodes
from app.core.ssh import execute_ssh
from app.core.crypto import decrypt_value
from app.core.logger import get_logs as core_get_logs

router = APIRouter()

@router.get("/telegram")
def get_tg():
    bot_token, chat_id = get_telegram_config()
    return {"bot_token": bot_token, "chat_id": chat_id}

@router.post("/telegram")
def save_tg(config: TelegramConfig):
    save_telegram_config(config.bot_token, config.chat_id)
    return {"message": "Telegram config saved"}

@router.post("/telegram/test")
def test_tg():
    bot_token, chat_id = get_telegram_config()
    if not bot_token or not chat_id:
        raise HTTPException(status_code=400, detail="Telegram config not set")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": "Test message from EarnApp Dashboard V2"}).encode('ascii')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            return {"message": "Test message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test message: {str(e)}")

@router.get("/export")
def export_nodes():
    nodes = load_nodes()
    # Don't decrypt passwords for export, keep them encrypted or however they are stored in DB
    return JSONResponse(content=nodes)

@router.post("/import_config")
async def import_config(request: Request):
    try:
        data = await request.json()
        if not isinstance(data, list):
            raise ValueError("Expected a list of nodes")
        save_nodes(data)
        return {"message": "Config imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config data: {str(e)}")

async def count_active_bots(node):
    cmd = "docker ps -q --filter ancestor=fazalfarhan01/earnapp:lite | wc -l"
    loop = asyncio.get_running_loop()
    success, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], cmd)
    if success and out:
        try:
            return int(out.strip())
        except ValueError:
            return 0
    return 0

@router.get("/earnings")
async def get_earnings():
    nodes = load_nodes()
    tasks = [count_active_bots(n) for n in nodes]
    results = await asyncio.gather(*tasks)
    active_bots = sum(results)
    daily_usd = active_bots * 0.15
    monthly_usd = daily_usd * 30
    return {
        "active_bots": active_bots,
        "daily_usd": round(daily_usd, 2),
        "monthly_usd": round(monthly_usd, 2)
    }

@router.get("/logs")
def get_activity_logs():
    return core_get_logs()
