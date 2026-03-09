# backend/app/ai_service.py

import json
import logging
from typing import List, Dict, Any
import httpx
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
    async def dns_chat(query: str, domain_context: str, history: List[Dict[str, str]] = None) -> str:
        """
        Troubleshoot DNS issues via chat.
        """
        system_prompt = (
            "Ste 'API Centrum AI Autopilot'. Pomáhate používateľom riešiť problémy s DNS a SSL. "
            "Komunikujte výhradne v SLOVENČINE. Buďte stručný a profesionálny. "
            "Na odpovede používajte poskytnutý kontext domény. "
            "Ak vás niekto požiada o opravu, vysvetlite, čo by ste zmenili a prečo. "
            "Kontext (Aktuálne DNS pre doménu):\n" + domain_context
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        return await AIService._call_openai(messages)
