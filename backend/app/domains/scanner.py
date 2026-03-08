"""
DNS Scanner module for the AI DNS Sentinel feature.
Analyzes DNS records to determine security health (SPF, DKIM, DMARC) and generates scores.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AISentinel:
    """Proactive DNS security analyzer."""

    @staticmethod
    def audit_domain(domain_name: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans a list of DNS records for a domain and generates a security score.
        """
        has_spf = False
        has_dmarc = False
        has_dkim = False # Difficult to ascertain without knowing the exact selector, but we can look for generic '_domainkey' TXT/CNAME records.

        spf_record = None
        dmarc_record = None

        fixes_needed = []

        for record in records:
            if record.get("type", "").upper() == "TXT":
                content = record.get("content", "").lower()
                name = record.get("name", "").lower()

                # Check SPF
                if name == "" or name == "@":
                    if "v=spf1" in content:
                        has_spf = True
                        spf_record = record

                # Check DMARC
                if name == "_dmarc":
                    if "v=dmarc1" in content:
                        has_dmarc = True
                        dmarc_record = record
            
            # Basic DKIM heuristic
            if record.get("type", "").upper() in ["TXT", "CNAME"]:
                name = record.get("name", "").lower()
                if "_domainkey" in name:
                    has_dkim = True

        # Calculate Score
        score = 10
        if has_spf:
            score += 40
        if has_dmarc:
            score += 30
        if has_dkim:
            score += 20

        # Determine needed fixes
        if not has_spf:
            fixes_needed.append({
                "type": "TXT",
                "name": "",  # Root domain
                "content": "v=spf1 include:_spf.websupport.sk ~all",
                "ttl": 3600,
                "note": "Standard Websupport SPF record"
            })
        
        if not has_dmarc:
            fixes_needed.append({
                "type": "TXT",
                "name": "_dmarc",
                "content": "v=DMARC1; p=none; sp=none; aspf=r; adkim=r;",
                "ttl": 3600,
                "note": "Basic monitoring DMARC record"
            })

        # Provide a human-readable health status
        if score == 100:
            status = "Excellent"
            color = "green"
            message = "Your domain is fully protected against email spoofing."
        elif score >= 50:
            status = "Good"
            color = "orange"
            message = "Baseline protection is active, but strongly consider enabling DMARC or DKIM."
        else:
            status = "Critical"
            color = "red"
            message = "Your domain is highly vulnerable to email spoofing and spam classification."

        return {
            "domain": domain_name,
            "security_score": score,
            "status": status,
            "color": color,
            "message": message,
            "details": {
                "spf_active": has_spf,
                "dmarc_active": has_dmarc,
                "dkim_active": has_dkim
            },
            "fixes_available": fixes_needed
        }
