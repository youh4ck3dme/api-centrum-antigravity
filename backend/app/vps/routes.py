"""
VPS Monitor — pings all domains (Websupport API + Forpsi manual list) and checks SSL expiry.
"""

import ssl
import socket
import requests
from datetime import datetime
from fastapi import APIRouter

from ..websupport import WebsupportService
from ..metrics import performance_metrics
from ..config import settings

router = APIRouter(tags=["VPS"])

VPS_IP = "194.182.87.6"


def get_ssl_expiry_days(hostname: str):
    try:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
        s.settimeout(5)
        s.connect((hostname, 443))
        cert = s.getpeercert()
        s.close()
        expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        return max(0, (expiry - datetime.utcnow()).days)
    except Exception:
        return None


def ping_domain(domain: str):
    """Returns (http_status_code, https_reachable)."""
    try:
        r = requests.get(f"https://{domain}", timeout=5, allow_redirects=True)
        return r.status_code, True
    except requests.exceptions.SSLError:
        try:
            r = requests.get(f"http://{domain}", timeout=5)
            return r.status_code, False
        except Exception:
            return None, False
    except Exception:
        return None, False


@router.get("/vps/status")
def vps_status():
    """Return VPS server info + status of all domains (Websupport + Forpsi)."""
    domain_names: list[str] = []

    # --- Websupport (REST API) ---
    ws_names: set[str] = set()
    try:
        ws_result = WebsupportService.get_domains()
        items = ws_result.get("items", [])
        ws_names = {
            x.get("name")
            for x in items
            if x.get("serviceName") == "domain" and x.get("name")
        }
        domain_names += list(ws_names)
    except Exception:
        pass

    # --- Forpsi (manual list from FORPSI_DOMAINS env var) ---
    forpsi_names: set[str] = set()
    if settings.FORPSI_DOMAINS:
        forpsi_names = {d.strip() for d in settings.FORPSI_DOMAINS.split(",") if d.strip()}
        domain_names += [d for d in forpsi_names if d not in ws_names]

    now = datetime.utcnow().timestamp()
    api_calls_24h = sum(1 for m in performance_metrics if now - m["timestamp"] < 86400)

    domains_data = []
    for name in domain_names:
        status_code, https_ok = ping_domain(name)
        ssl_days = get_ssl_expiry_days(name) if https_ok else None
        registrar = "Forpsi" if name in forpsi_names else "Websupport"
        domains_data.append(
            {
                "name": name,
                "registrar": registrar,
                "http_status": status_code,
                "https_reachable": https_ok,
                "ssl_expiry_days": ssl_days,
            }
        )

    return {
        "server": {"ip": VPS_IP, "hostname": "nexify-studio.tech"},
        "domains": domains_data,
        "total": len(domains_data),
        "api_calls_24h": api_calls_24h,
    }
