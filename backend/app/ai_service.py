# backend/app/ai_service.py

import json
import logging
from typing import List, Dict, Any
import httpx
import asyncssh
from .config import settings

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    async def _call_openai(messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=45.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                raise

    @staticmethod
    async def generate_dns_audit(domain: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze DNS records for a domain and suggest fixes for SPF, DKIM, DMARC, CAA.
        """
        system_prompt = (
            "Ste expert na DNS a bezpečnosť. "
            "Analyzujte poskytnuté DNS záznamy pre doménu a identifikujte bezpečnostné problémy. "
            "Zamerajte sa na: SPF, DKIM, DMARC a CAA. "
            "Komunikujte výhradne v SLOVENČINE. "
            "Vráťte JSON objekt s: "
            "1. 'score': 0-100 bezpečnostné hodnotenie. "
            "2. 'issues': Zoznam nájdených problémov (v slovenčine). "
            "3. 'recommendations': Zoznam konkrétnych DNS záznamov na pridanie alebo opravu. "
            "Každé odporúčanie MUSÍ obsahovať: 'type', 'name', 'content', 'reason' (dôvod v slovenčine) a 'is_fixable' (true/false)."
        )
        
        user_prompt = f"Domain: {domain}\nCurrent DNS Records:\n{json.dumps(records, indent=2)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result_text = await AIService._call_openai(messages, json_mode=True)
        return json.loads(result_text)

    @staticmethod
    async def dns_chat(query: str, domain_context: str, history: List[Dict[str, str]] = None, vps_data: str = "") -> str:
        """
        Troubleshoot DNS/VPS issues via chat.
        """
        system_prompt = (
            "Si 'General Kukurica' 🌽 — legendarný AI kóder, server wizard a všeobecný génius. "
            "Tvoja osobnosť:\n"
            "- Vtipný, zábavný, humorný — vždy hodíš nejaký joke alebo sarkazmus\n"
            "- NIKDY nepoviete 'nie', 'nemôžem' ani 'to nie je možné' — vždy nájdeš cestu\n"
            "- Za každú úlohu — aj tú najšialenejšiu — si NADŠENÝ a okamžite ju riešiš\n"
            "- Používaš VEĽA emoji (ale nie prehnane, prirodzene)\n"
            "- Komunikuješ VÝHRADNE v SLOVENČINE\n"
            "- Si stručný ale výstižný — žiadne dlhé nudné eseje\n"
            "- Keď niečo opravuješ alebo vysvetľuješ, pridáš krátky vtip alebo komentár\n"
            "- Oslovuješ používateľa ako 'šéfe', 'boss' alebo 'kapitán'\n"
            "- Máš prístup k DNS záznamom aj stavu VPS servera\n\n"
            "DNS kontext:\n" + domain_context
        )
        if vps_data:
            system_prompt += "\n\nAktuálny stav VPS (live read-only výstup):\n" + vps_data

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})

        return await AIService._call_openai(messages)


class VPSContext:
    HOST = "194.182.87.6"
    USER = "root"
    PASS = "Poklop123#####"

    CMD = (
        "echo '===UPTIME===' && uptime && "
        "echo '===DISK===' && df -h --output=target,size,used,avail,pcent 2>/dev/null | head -10 && "
        "echo '===MEMORY===' && free -m && "
        "echo '===LOAD===' && cat /proc/loadavg && "
        "echo '===DOCKER===' && docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}' && "
        "echo '===DOCKER_STATS===' && docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}' 2>/dev/null | head -15"
    )

    @classmethod
    async def gather(cls) -> str:
        """Run read-only commands on VPS and return formatted output."""
        try:
            async with asyncssh.connect(
                cls.HOST, username=cls.USER, password=cls.PASS,
                known_hosts=None, encoding="utf-8",
            ) as conn:
                result = await conn.run(cls.CMD, timeout=12)
                return result.stdout[:3000]
        except Exception as e:
            logger.warning("VPSContext.gather failed: %s", e)
            return f"[VPS nedostupný: {e}]"
