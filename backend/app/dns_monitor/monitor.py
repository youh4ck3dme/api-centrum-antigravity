# backend/app/dns_monitor/monitor.py

import asyncio
import heapq
import json
import logging
import time
from typing import List, Dict, Any, Set
from datetime import datetime, timezone

import dns.resolver
from fastapi import WebSocket

from ..websupport import WebsupportService
from ..config import settings
from .persistence import save_threat

logger = logging.getLogger(__name__)

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
            "ttl": r.get("ttl"),
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
                results.append({
                    "type": rtype,
                    "name": domain,
                    "content": a.to_text(),
                    "ttl": answers.rrset.ttl if answers.rrset else None,
                })
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


def _records_by_type(records: List[Dict]) -> Dict[str, List[Dict]]:
    """Group full records (with TTL) by type."""
    d: Dict[str, List[Dict]] = {}
    for r in records:
        if r.get("type"):
            d.setdefault(r["type"], []).append(r)
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

    # ── A record changed ─────────────────────────────────────────────────
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

    # ── MX changed ───────────────────────────────────────────────────────
    pm, cm = pb.get("MX", set()), cb.get("MX", set())
    if pm and cm and pm != cm:
        threats.append(_threat("HIGH", "MX",
            f"MX record zmenený: {', '.join(sorted(pm))} → {', '.join(sorted(cm))}",
            ", ".join(sorted(pm)), ", ".join(sorted(cm))))

    # ── NS changed ───────────────────────────────────────────────────────
    pn, cn = pb.get("NS", set()), cb.get("NS", set())
    if pn and cn and pn != cn:
        threats.append(_threat("CRITICAL", "NS",
            f"NS record zmenený: {', '.join(sorted(pn))} → {', '.join(sorted(cn))}",
            ", ".join(sorted(pn)), ", ".join(sorted(cn))))

    # ── Risky new CNAME (subdomain takeover) ─────────────────────────────
    for cname in cb.get("CNAME", set()) - pb.get("CNAME", set()):
        if any(r in cname for r in _RISKY_CNAME):
            threats.append(_threat("HIGH", "CNAME",
                f"Nový CNAME → {cname} (možný subdomain takeover)", new=cname))

    # ── TTL change detection for A, MX, NS ───────────────────────────────
    prev_by_type = _records_by_type(prev)
    curr_by_type = _records_by_type(curr)

    for rtype in ("A", "MX", "NS"):
        prev_recs = prev_by_type.get(rtype, [])
        curr_recs = curr_by_type.get(rtype, [])
        for cur_rec in curr_recs:
            # Match by content
            match = None
            for p in prev_recs:
                if p.get("content") == cur_rec.get("content"):
                    match = p
                    break
            if match:
                prev_ttl = match.get("ttl")
                cur_ttl = cur_rec.get("ttl")
                if prev_ttl is not None and cur_ttl is not None and prev_ttl != cur_ttl:
                    severity = "MEDIUM"
                    # Significantly lowered TTL is higher risk
                    if cur_ttl < prev_ttl and cur_ttl < 300:
                        severity = "HIGH"
                    threats.append(_threat(severity, rtype,
                        f"TTL zmenené pre {rtype} z {prev_ttl} na {cur_ttl}",
                        str(prev_ttl), str(cur_ttl)))

    # ── TXT / SPF change detection ───────────────────────────────────────
    prev_txt = sorted([r.get("content", "") for r in prev_by_type.get("TXT", [])])
    curr_txt = sorted([r.get("content", "") for r in curr_by_type.get("TXT", [])])

    if prev_txt != curr_txt:
        # SPF-specific heuristic
        p_spf = next((t for t in prev_txt if "v=spf1" in t.lower()), None)
        c_spf = next((t for t in curr_txt if "v=spf1" in t.lower()), None)

        if p_spf and c_spf and p_spf != c_spf:
            import re
            p_includes = set(re.findall(r"include:([^\s]+)", p_spf.lower()))
            c_includes = set(re.findall(r"include:([^\s]+)", c_spf.lower()))
            
            new_includes = c_includes - p_includes
            if new_includes:
                threats.append(_threat("HIGH", "TXT",
                    f"SPF pridané include ({', '.join(sorted(new_includes))}) — môže povoliť nové odosielateľské servery",
                    p_spf, c_spf))
            elif "all" in c_spf and "all" in p_spf and p_spf != c_spf:
                threats.append(_threat("HIGH", "TXT",
                    "SPF politika sa zmenila", p_spf, c_spf))
            else:
                threats.append(_threat("MEDIUM", "TXT",
                    "TXT/SPF zmenené", p_spf, c_spf))

        # TXT records completely disappeared
        if prev_txt and not curr_txt:
            threats.append(_threat("HIGH", "TXT",
                "TXT záznamy zmizli",
                ", ".join(prev_txt), None))

    return threats


# ── Per-domain polling scheduler ──────────────────────────────────────────────
def _get_poll_intervals() -> Dict[str, int]:
    """Parse DOMAIN_POLL_INTERVALS from config (JSON string)."""
    raw = getattr(settings, "DOMAIN_POLL_INTERVALS", "")
    if not raw:
        return {"default": 60}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return {"default": 60}


class DomainJob:
    """Represents a scheduled DNS poll for a single domain."""

    def __init__(self, domain: str, interval: int, fetch_fn, is_forpsi: bool):
        self.domain = domain
        self.interval = interval
        self.fetch_fn = fetch_fn
        self.is_forpsi = is_forpsi
        self.next_run = time.time()

    def __lt__(self, other):
        return self.next_run < other.next_run


# ── Background polling loop ───────────────────────────────────────────────────
async def dns_poll_loop():
    global last_scan_ts

    intervals = _get_poll_intervals()
    default_interval = intervals.get("default", 60)

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

    # Build per-domain job queue
    jobs: List[DomainJob] = []
    for d in domain_names:
        interval = intervals.get(d, default_interval)
        is_forpsi = d in forpsi_set
        fetch_fn = _get_external_dns if is_forpsi else _get_ws_dns
        job = DomainJob(d, interval, fetch_fn, is_forpsi)
        job.next_run = time.time() + interval  # first real check after interval
        jobs.append(job)
    heapq.heapify(jobs)

    refresh_cycle = 0

    while True:
        if not jobs:
            await asyncio.sleep(60)
            continue

        # Wait until next job is due
        job = heapq.heappop(jobs)
        now = time.time()
        wait = job.next_run - now
        if wait > 0:
            await asyncio.sleep(min(wait, 60))  # cap sleep to allow graceful handling
            # If we woke early, re-check timing
            if time.time() < job.next_run:
                heapq.heappush(jobs, job)
                continue

        # Run the fetch for this domain
        try:
            current = await job.fetch_fn(job.domain)
        except Exception:
            current = []

        previous = dns_snapshot.get(job.domain, [])
        new_threats = detect_threats(job.domain, previous, current)

        # Persist and broadcast threats
        for t in new_threats:
            recent_threats.insert(0, t)
            await manager.broadcast(t)
            # Persist to DB via executor (sync call)
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, save_threat, t)
            except Exception as e:
                logger.error("Threat persistence error: %s", e)

        dns_snapshot[job.domain] = current

        # Trim in-memory list
        del recent_threats[MAX_RECENT:]

        last_scan_ts = int(time.time())

        # Schedule next run for this domain
        job.next_run = time.time() + job.interval
        heapq.heappush(jobs, job)

        # Periodic heartbeat (every domain check emits a heartbeat)
        today = datetime.now(timezone.utc).date()
        threats_today = sum(
            1 for t in recent_threats
            if datetime.fromtimestamp(t["timestamp"], tz=timezone.utc).date() == today
        )
        await manager.broadcast({
            "type": "heartbeat",
            "domains_checked": len(dns_snapshot),
            "threats_today": threats_today,
            "timestamp": last_scan_ts,
        })

        # Refresh domain list every ~10 minutes (rough cycles)
        refresh_cycle += 1
        if refresh_cycle % 10 == 0:
            domain_names, forpsi_set = await _fetch_domain_list()
            existing_domains = {j.domain for j in jobs}
            existing_domains.add(job.domain)
            for d in domain_names:
                if d not in existing_domains:
                    interval = intervals.get(d, default_interval)
                    is_forpsi = d in forpsi_set
                    fetch_fn = _get_external_dns if is_forpsi else _get_ws_dns
                    new_job = DomainJob(d, interval, fetch_fn, is_forpsi)
                    new_job.next_run = time.time()
                    heapq.heappush(jobs, new_job)
