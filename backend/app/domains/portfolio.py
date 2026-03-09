# backend/app/domains/portfolio.py
"""Domain Portfolio Intelligence — expiry tracking, cost estimation, competitor watch."""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from functools import lru_cache
from datetime import datetime

import dns.resolver

from ..websupport import WebsupportService
from ..config import settings

logger = logging.getLogger(__name__)

PRICE_PER_DOMAIN_EUR = 15  # Estimated annual cost per domain


def _days_until(expire_ts: Optional[int]) -> Optional[int]:
    if not expire_ts:
        return None
    return max(0, int((expire_ts - time.time()) / 86400))


def _risk(days: Optional[int]) -> str:
    if days is None:
        return "unknown"
    if days < 30:
        return "critical"
    if days < 90:
        return "warning"
    return "safe"


def _typo_variants(domain: str) -> List[str]:
    """Generate likely competitor/typo variants of a domain."""
    name, _, tld = domain.rpartition(".")
    variants = [
        f"{name}s.{tld}",                      # pluralized
        f"{name}.sk",                           # .sk
        f"{name}.com",                          # .com
        f"{name}.eu",                           # .eu
        f"{name.replace('-', '')}.{tld}",       # hyphen removed
    ]
    return [v for v in variants if v != domain][:5]


def _dns_resolves(domain: str) -> bool:
    """Returns True if domain has an A record (is registered and live)."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["8.8.8.8"]
        resolver.timeout = 2
        resolver.lifetime = 2
        resolver.resolve(domain, "A")
        return True
    except Exception:
        return False


def _check_competitors(ws_domains: List[dict]) -> List[Dict[str, str]]:
    """DNS-check typo variants in parallel. Returns list of registered hits."""
    tasks: List[tuple] = []
    for d in ws_domains[:8]:  # limit to 8 domains to keep runtime reasonable
        for variant in _typo_variants(d["name"]):
            tasks.append((d["name"], variant))

    hits: List[Dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_dns_resolves, variant): (original, variant)
                   for original, variant in tasks}
        for future in as_completed(futures, timeout=10):
            original, variant = futures[future]
            try:
                if future.result():
                    hits.append({"original": original, "variant": variant})
            except Exception:
                pass
    return hits[:20]


# Cache portfolio for 15 minutes max
_portfolio_cache = {"timestamp": 0, "data": None}

def get_portfolio() -> Dict[str, Any]:
    global _portfolio_cache
    
    current_time = time.time()
    # If cache is valid (less than 15 mins old), return it
    if _portfolio_cache["data"] is not None and (current_time - _portfolio_cache["timestamp"] < 900):
        return _portfolio_cache["data"]

    # ── Fetch Websupport domains ──────────────────────────────────────────────
    result = WebsupportService.get_domains()
    items = result.get("items", [])
    ws_domains = [x for x in items if x.get("serviceName") == "domain" and x.get("name")]

    # ── Append Forpsi domains ─────────────────────────────────────────────────
    ws_names = {d["name"] for d in ws_domains}
    forpsi_list: List[dict] = []
    if settings.FORPSI_DOMAINS:
        for name in [n.strip() for n in settings.FORPSI_DOMAINS.split(",") if n.strip()]:
            if name not in ws_names:
                forpsi_list.append({"name": name})

    # ── Build enriched domain list ────────────────────────────────────────────
    all_domains: List[Dict[str, Any]] = []

    for d in ws_domains:
        days = _days_until(d.get("expireTime"))
        all_domains.append({
            "name": d["name"],
            "expireTime": d.get("expireTime"),
            "days_until_expiry": days,
            "risk": _risk(days),
            "autoExtend": d.get("autoExtend"),
            "status": d.get("status", "active"),
            "registrar": "websupport",
        })

    for d in forpsi_list:
        all_domains.append({
            "name": d["name"],
            "expireTime": None,
            "days_until_expiry": None,
            "risk": "unknown",
            "autoExtend": None,
            "status": "active",
            "registrar": "forpsi",
        })

    # Sort: critical first, then by days, then unknown last
    def _sort_key(d):
        if d["days_until_expiry"] is None:
            return 99999
        return d["days_until_expiry"]

    all_domains.sort(key=_sort_key)

    # ── Stats ─────────────────────────────────────────────────────────────────
    critical = sum(1 for d in all_domains if d["risk"] == "critical")
    warning = sum(1 for d in all_domains if d["risk"] == "warning")
    no_autoextend = sum(1 for d in all_domains if d["autoExtend"] is False)
    annual_cost = len(ws_domains) * PRICE_PER_DOMAIN_EUR

    # ── Competitor watch ──────────────────────────────────────────────────────
    try:
        competitor_hits = _check_competitors(ws_domains)
    except Exception as e:
        logger.warning("Competitor check failed: %s", e)
        competitor_hits = []

    result = {
        "domains": all_domains,
        "total": len(all_domains),
        "critical": critical,
        "warning": warning,
        "no_autoextend": no_autoextend,
        "annual_cost_eur": annual_cost,
        "competitor_watch": competitor_hits,
    }
    
    _portfolio_cache["data"] = result
    _portfolio_cache["timestamp"] = time.time()
    
    return result