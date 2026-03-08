# backend/app/dns_monitor/monitor.py

import asyncio
import time
from typing import List, Dict, Any, Set
from datetime import datetime, timezone

import dns.resolver
from fastapi import WebSocket

from ..websupport import WebsupportService
from ..config import settings

# ── In-memory state ──────────────────────────────────────────────────────────
dns_snapshot: Dict[str, List[Dict[str, Any]]] = {}
recent_threats: List[Dict[str, Any]] = []
MAX_RECENT = 100
last_scan_ts: int = 0


# ── WebSocket connection manager ─────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active = [c for c in self.active if c is not ws]

    async def broadcast(self, message: Dict[str, Any]):
        alive = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
                alive.append(ws)
            except Exception:
                pass
        self.active = alive


manager = ConnectionManager()


# ── Domain fetching ───────────────────────────────────────────────────────────
async def _fetch_domain_list() -> tuple[List[str], Set[str]]:
    """Returns (all_names, forpsi_set). Websupport fetched via executor (sync API)."""
    ws_names: List[str] = []
    try:
        loop = asyncio.get_event_loop()
        ws_result = await loop.run_in_executor(None, WebsupportService.get_domains)
        items = ws_result.get("items", [])
        ws_names = [
            x.get("name") for x in items
            if x.get("serviceName") == "domain" and x.get("name")
        ]
    except Exception:
        pass

    forpsi: Set[str] = set()
    if settings.FORPSI_DOMAINS:
        forpsi = {d.strip() for d in settings.FORPSI_DOMAINS.split(",") if d.strip()}

    all_names = ws_names + [d for d in sorted(forpsi) if d not in ws_names]
    return all_names, forpsi


# ── DNS record fetching ───────────────────────────────────────────────────────
def _normalize(raw: List[Dict]) -> List[Dict]:
    return [
        {
            "type": r.get("type") or r.get("record_type"),
            "name": r.get("name") or r.get("host") or r.get("hostname"),
            "content": r.get("content") or r.get("value") or r.get("data"),
        }
        for r in raw
    ]


async def _get_ws_dns(domain: str) -> List[Dict]:
    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, lambda: WebsupportService.get_dns_records(domain))
        return _normalize(raw or [])
    except Exception:
        return []


async def _get_external_dns(domain: str) -> List[Dict]:
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.timeout = 4
    resolver.lifetime = 4
    results = []
    for rtype in ("A", "MX", "NS", "CNAME", "TXT"):
        try:
            answers = await asyncio.get_event_loop().run_in_executor(
                None, lambda t=rtype: resolver.resolve(domain, t)
            )
            for a in answers:
                results.append({"type": rtype, "name": domain, "content": a.to_text()})
        except Exception:
            pass
    return results


# ── Threat detection ──────────────────────────────────────────────────────────
_RISKY_CNAME = ("github.io", "amazonaws.com", "azurewebsites.net", "herokuapp.com",
                "netlify.app", "pages.dev", "vercel.app")


def _by_type(records: List[Dict]) -> Dict[str, Set[str]]:
    d: Dict[str, Set[str]] = {}
    for r in records:
        if r.get("type") and r.get("content"):
            d.setdefault(r["type"], set()).add(r["content"])
    return d


def detect_threats(domain: str, prev: List[Dict], curr: List[Dict]) -> List[Dict]:
    if not prev:
        return []  # no baseline yet — first scan

    threats = []
    ts = int(time.time())
    pb = _by_type(prev)
    cb = _by_type(curr)

    def _threat(severity, record_type, message, old=None, new=None):
        return {
            "type": "threat",
            "severity": severity,
            "domain": domain,
            "record_type": record_type,
            "message": message,
            "old_value": old,
            "new_value": new,
            "timestamp": ts,
        }

    # A record changed
    pa, ca = pb.get("A", set()), cb.get("A", set())
    if pa and ca and pa != ca:
        threats.append(_threat("CRITICAL", "A",
            f"A record zmenený: {', '.join(sorted(pa))} → {', '.join(sorted(ca))}",
            ", ".join(sorted(pa)), ", ".join(sorted(ca))))
    elif pa and not ca:
        threats.append(_threat("HIGH", "A", "A record zmizol", ", ".join(sorted(pa))))
    else:
        for ip in ca - pa:
            threats.append(_threat("MEDIUM", "A", f"Nový A record: {ip}", new=ip))

    # MX changed
    pm, cm = pb.get("MX", set()), cb.get("MX", set())
    if pm and cm and pm != cm:
        threats.append(_threat("HIGH", "MX",
            f"MX record zmenený: {', '.join(sorted(pm))} → {', '.join(sorted(cm))}",
            ", ".join(sorted(pm)), ", ".join(sorted(cm))))

    # NS changed
    pn, cn = pb.get("NS", set()), cb.get("NS", set())
    if pn and cn and pn != cn:
        threats.append(_threat("CRITICAL", "NS",
            f"NS record zmenený: {', '.join(sorted(pn))} → {', '.join(sorted(cn))}",
            ", ".join(sorted(pn)), ", ".join(sorted(cn))))

    # Risky new CNAME (subdomain takeover)
    for cname in cb.get("CNAME", set()) - pb.get("CNAME", set()):
        if any(r in cname for r in _RISKY_CNAME):
            threats.append(_threat("HIGH", "CNAME",
                f"Nový CNAME → {cname} (možný subdomain takeover)", new=cname))

    return threats


# ── Background polling loop ───────────────────────────────────────────────────
async def dns_poll_loop():
    global last_scan_ts

    # Initial fetch — build baseline, no threats emitted
    domain_names, forpsi_set = await _fetch_domain_list()
    tasks = [
        _get_external_dns(d) if d in forpsi_set else _get_ws_dns(d)
        for d in domain_names
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for domain, result in zip(domain_names, results):
        dns_snapshot[domain] = result if not isinstance(result, Exception) else []
    last_scan_ts = int(time.time())

    cycle = 0
    while True:
        await asyncio.sleep(60)
        cycle += 1

        # Refresh domain list every 10 cycles (~10 min) in case new domains added
        if cycle % 10 == 0:
            domain_names, forpsi_set = await _fetch_domain_list()

        tasks = [
            _get_external_dns(d) if d in forpsi_set else _get_ws_dns(d)
            for d in domain_names
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        new_threats = []
        for domain, result in zip(domain_names, results):
            current = result if not isinstance(result, Exception) else []
            previous = dns_snapshot.get(domain, [])
            for t in detect_threats(domain, previous, current):
                new_threats.append(t)
                recent_threats.insert(0, t)
            dns_snapshot[domain] = current

        # Trim
        del recent_threats[MAX_RECENT:]

        last_scan_ts = int(time.time())
        today = datetime.now(timezone.utc).date()
        threats_today = sum(
            1 for t in recent_threats
            if datetime.fromtimestamp(t["timestamp"], tz=timezone.utc).date() == today
        )

        # Broadcast threats
        for t in new_threats:
            await manager.broadcast(t)

        # Heartbeat
        await manager.broadcast({
            "type": "heartbeat",
            "domains_checked": len(domain_names),
            "threats_today": threats_today,
            "timestamp": last_scan_ts,
        })
