import asyncio
import uuid
from fastapi import APIRouter, HTTPException
from app.models import DeployBulkReq
from app.core.db import load_nodes
from app.core.ssh import execute_ssh
from app.core.crypto import decrypt_value
from app.core.logger import log_action

router = APIRouter()

@router.post("")
async def deploy_bot_bulk(req: DeployBulkReq):
    nodes = load_nodes()
    node = next((n for n in nodes if n['ip'] == req.ip), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    loop = asyncio.get_running_loop()
    
    # Parse proxies
    proxy_list = [p.strip() for p in req.proxies.splitlines() if p.strip()]
    if proxy_list and len(proxy_list) < req.count:
        # Pad proxies if not enough
        proxy_list = proxy_list * (req.count // len(proxy_list) + 1)
        
    results = []
    
    # Prepare Fake HW Script if spoofing
    fake_hw_base = "/tmp/earnapp_fake_hw"
    if req.spoof_hw:
        hw_setup_cmd = f"mkdir -p {fake_hw_base}"
        await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], hw_setup_cmd)

    for i in range(req.count):
        # Generate UUID and Serial
        rand_hex = uuid.uuid4().hex
        uid = f"sdk-node-{rand_hex}"
        serial = f"{rand_hex}a1b2c3d4"

        # Determine OS version for API registration randomly or sequentially to spoof device
        # For simplicity, we just use standard Ubuntu focal, but we can randomize slightly
        os_version = "DBAI-2K25+24.5.1+focal"

        # API Registration Command
        reg_cmd = f"curl -s -X POST 'https://client.earnapp.com/install_device?uuid={uid}&version=1.651.510&arch=arm64&appid=node_earnapp.com&os={os_version}' -H 'Content-Type: application/json' -d '{{\"serial\":\"{serial}\"}}'"
        succ, out, err = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], reg_cmd)
        
        if not succ or "ok" not in out.lower():
            results.append({"status": "failed", "error": f"Registration failed: {out} {err}"})
            continue

        container_name = f"earnapp_{rand_hex[:6]}"
        
        docker_run_args = ["-d", "--restart always", f"-e EARNAPP_UUID={uid}", f"--name {container_name}"]
        
        # Inject Proxy
        if proxy_list:
            proxy = proxy_list[i]
            docker_run_args.append("--network bridge")
            docker_run_args.append(f"-e HTTP_PROXY={proxy}")
            docker_run_args.append(f"-e HTTPS_PROXY={proxy}")
        else:
            docker_run_args.append("--network host")
            
        # Inject Fake HW
        if req.spoof_hw:
            cpu_file = f"{fake_hw_base}/cpuinfo_{rand_hex[:6]}"
            mem_file = f"{fake_hw_base}/meminfo_{rand_hex[:6]}"
            # Generate fake files
            fake_cpu = f"printf 'processor\\t: 0\\nmodel name\\t: ARM Cortex-A72 r0p3\\nBogoMIPS\\t: {100 + i}.00\\nFeatures\\t: fp asimd evtstrm crc32 cpuid\\n' > {cpu_file}"
            fake_mem = f"printf 'MemTotal:\\t4048576 kB\\nMemFree:\\t1024000 kB\\n' > {mem_file}"
            await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], f"{fake_cpu} && {fake_mem}")
            docker_run_args.append(f"-v {cpu_file}:/proc/cpuinfo")
            docker_run_args.append(f"-v {mem_file}:/proc/meminfo")
            
        run_cmd = f"docker run {' '.join(docker_run_args)} fazalfarhan01/earnapp:lite"
        succ3, out3, err3 = await loop.run_in_executor(None, execute_ssh, node['ip'], node['username'], decrypt_value(node['password']), node['port'], run_cmd)

        if succ3:
            log_action('DEPLOY_BOT', f'Deployed {container_name} successfully', req.ip)
            results.append({
                "status": "success",
                "uuid": uid,
                "container": container_name,
                "link": f"https://earnapp.com/r/{uid}"
            })
        else:
            results.append({"status": "failed", "error": f"Docker run failed: {out3} {err3}"})

    return {"message": "Bulk deploy finished", "results": results}
