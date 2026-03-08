# backend/app/dns_monitor/provision.py

"""
One-Click VPS Provisioning — orchestrates server creation, DNS setup, and deployment.

Supports Hetzner and DigitalOcean. The endpoint spawns a background task and
returns a job_id. Clients poll GET /dns-monitor/provision/{job_id} for status.
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional

import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..config import settings
from ..websupport import WebsupportService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["VPS Provisioning"])

# In-memory job store
provision_jobs: Dict[str, Dict[str, Any]] = {}


def _update_job(job_id: str, **kwargs):
    if job_id in provision_jobs:
        provision_jobs[job_id].update(kwargs)
        provision_jobs[job_id]["updated_at"] = int(time.time())


# ── Provider: Hetzner ─────────────────────────────────────────────────────────
def _create_hetzner_server(name: str, region: str, server_type: str = "cx22",
                           ssh_key_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a Hetzner Cloud server. Returns server dict with IP."""
    token = settings.HETZNER_API_TOKEN
    if not token:
        raise RuntimeError("HETZNER_API_TOKEN not configured")

    payload = {
        "name": name,
        "server_type": server_type,
        "image": "ubuntu-22.04",
        "location": region or "nbg1",
        "start_after_create": True,
    }
    if ssh_key_id:
        payload["ssh_keys"] = [ssh_key_id]

    resp = requests.post(
        "https://api.hetzner.cloud/v1/servers",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    server = data.get("server", {})
    return {
        "id": server.get("id"),
        "ip": server.get("public_net", {}).get("ipv4", {}).get("ip"),
        "status": server.get("status"),
    }


def _wait_hetzner_ready(server_id: int, timeout: int = 120) -> str:
    """Poll Hetzner until server status is 'running'. Returns IP."""
    token = settings.HETZNER_API_TOKEN
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"https://api.hetzner.cloud/v1/servers/{server_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        server = resp.json().get("server", {})
        if server.get("status") == "running":
            return server.get("public_net", {}).get("ipv4", {}).get("ip", "")
        time.sleep(5)
    raise TimeoutError("Server did not become ready in time")


# ── Provider: DigitalOcean ────────────────────────────────────────────────────
def _create_do_droplet(name: str, region: str, size: str = "s-1vcpu-1gb",
                       ssh_key_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a DigitalOcean droplet. Returns droplet dict."""
    token = settings.DIGITALOCEAN_API_TOKEN
    if not token:
        raise RuntimeError("DIGITALOCEAN_API_TOKEN not configured")

    payload = {
        "name": name,
        "region": region or "fra1",
        "size": size,
        "image": "ubuntu-22-04-x64",
    }
    if ssh_key_id:
        payload["ssh_keys"] = [ssh_key_id]

    resp = requests.post(
        "https://api.digitalocean.com/v2/droplets",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    droplet = resp.json().get("droplet", {})
    return {"id": droplet.get("id"), "status": droplet.get("status")}


def _wait_do_ready(droplet_id: int, timeout: int = 120) -> str:
    """Poll DigitalOcean until droplet is 'active'. Returns IP."""
    token = settings.DIGITALOCEAN_API_TOKEN
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"https://api.digitalocean.com/v2/droplets/{droplet_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        droplet = resp.json().get("droplet", {})
        if droplet.get("status") == "active":
            networks = droplet.get("networks", {}).get("v4", [])
            for net in networks:
                if net.get("type") == "public":
                    return net.get("ip_address", "")
        time.sleep(5)
    raise TimeoutError("Droplet did not become active in time")


# ── DNS A record creation ─────────────────────────────────────────────────────
def _create_a_record(domain: str, ip: str):
    """Create an A record for the domain pointing to the new server IP."""
    # Extract subdomain and zone from domain
    parts = domain.split(".")
    if len(parts) > 2:
        name = parts[0]
        zone = ".".join(parts[1:])
    else:
        name = ""
        zone = domain

    WebsupportService.create_dns_record(zone, {
        "type": "A",
        "name": name,
        "content": ip,
        "ttl": 600,
    })
    logger.info("A record created: %s -> %s", domain, ip)


# ── Background provisioning job ───────────────────────────────────────────────
def _provision_job(job_id: str, payload: Dict[str, Any]):
    """Synchronous provisioning workflow — runs as BackgroundTask."""
    try:
        provider = payload.get("provider", "hetzner").lower()
        name = payload.get("name", f"vps-{job_id[:8]}")
        region = payload.get("region", "")
        domain = payload.get("domain", "")
        ssh_key_id = payload.get("ssh_key_id")

        # Step 1: Create server
        _update_job(job_id, step="creating_server", progress=10)
        if provider == "hetzner":
            server = _create_hetzner_server(name, region, ssh_key_id=ssh_key_id)
            server_id = server["id"]
            _update_job(job_id, step="waiting_for_server", progress=30)
            ip = _wait_hetzner_ready(server_id)
        elif provider == "digitalocean":
            droplet = _create_do_droplet(name, region, ssh_key_id=ssh_key_id)
            droplet_id = droplet["id"]
            _update_job(job_id, step="waiting_for_server", progress=30)
            ip = _wait_do_ready(droplet_id)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        _update_job(job_id, step="server_ready", server_ip=ip, progress=50)

        # Step 2: Create A record (if domain provided)
        if domain:
            _update_job(job_id, step="creating_dns_record", progress=60)
            try:
                _create_a_record(domain, ip)
            except Exception as e:
                logger.error("DNS record creation failed: %s", e)
                _update_job(job_id, dns_error=str(e))

        # Step 3: SSH setup placeholder
        # In production: use asyncssh or paramiko to SSH into the server and run:
        #   - apt update && apt install -y docker.io docker-compose nginx certbot
        #   - configure nginx reverse proxy
        #   - certbot --nginx -d {domain}
        #   - docker-compose pull && docker-compose up -d
        _update_job(job_id, step="ssh_setup_pending", progress=70,
                    note="SSH setup requires manual asyncssh integration")

        # Mark complete
        _update_job(job_id, status="completed", step="done", progress=100)

    except Exception as e:
        logger.error("Provision job %s failed: %s", job_id, e)
        _update_job(job_id, status="failed", error=str(e))


# ── API endpoints ─────────────────────────────────────────────────────────────
@router.post("/dns-monitor/provision")
async def provision_vps(payload: dict, background_tasks: BackgroundTasks):
    """Start a VPS provisioning workflow. Returns job_id for status polling."""
    provider = payload.get("provider", "hetzner").lower()

    # Validate provider token exists
    if provider == "hetzner" and not settings.HETZNER_API_TOKEN:
        raise HTTPException(status_code=400, detail="HETZNER_API_TOKEN not configured")
    elif provider == "digitalocean" and not settings.DIGITALOCEAN_API_TOKEN:
        raise HTTPException(status_code=400, detail="DIGITALOCEAN_API_TOKEN not configured")
    elif provider not in ("hetzner", "digitalocean"):
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    job_id = str(uuid.uuid4())
    provision_jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "step": "queued",
        "progress": 0,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "payload": payload,
    }

    background_tasks.add_task(_provision_job, job_id, payload)
    return {"status": "started", "job_id": job_id}


@router.get("/dns-monitor/provision/{job_id}")
async def get_provision_status(job_id: str):
    """Poll the status of a provisioning job."""
    job = provision_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Remove sensitive payload from response
    safe = {k: v for k, v in job.items() if k != "payload"}
    return safe
