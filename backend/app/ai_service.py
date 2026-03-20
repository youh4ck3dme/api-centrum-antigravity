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
    async def _call_openai(messages: List[Dict[str, str]], json_mode: bool = False, tools: List[Dict[str, Any]] = None) -> Any:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Čistenie správ (OpenAI neznáša None v content alebo extra polia)
        cleaned_messages = []
        for msg in messages:
            m = {"role": msg["role"]}
            if "content" in msg:
                m["content"] = msg["content"] if msg["content"] is not None else ""
            if "tool_calls" in msg:
                m["tool_calls"] = msg["tool_calls"]
            if "tool_call_id" in msg:
                m["tool_call_id"] = msg["tool_call_id"]
            cleaned_messages.append(m)

        payload = {
            "model": "gpt-4o",
            "messages": cleaned_messages,
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        if tools:
            payload["tools"] = tools

        # DEBUG LOGGING
        # print(f"DEBUG PAYLOAD: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=45.0)
                response.raise_for_status()
                return response.json()
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
        
        response_data = await AIService._call_openai(messages, json_mode=True)
        result_text = response_data["choices"][0]["message"]["content"]
        return json.loads(result_text)

    @staticmethod
    async def dns_chat(query: str, domain_context: str, history: List[Dict[str, str]] = None, vps_data: str = "") -> str:
        """
        Troubleshoot DNS/VPS issues via chat with Function Calling support.
        """
        from .websupport import WebsupportService # Import here to avoid circularity

        # 1. Definícia nástrojov
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_vps_stats",
                    "description": "Získa aktuálne štatistiky VPS (uptime, disk, procesy, docker).",
                    "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_dns_records",
                    "description": "Získa zoznam všetkých DNS záznamov pre konkrétnu doménu z Websupportu.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string", "description": "Názov domény (napr. nexify-studio.tech)"}
                        },
                        "required": ["domain"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "modify_dns_record",
                    "description": "Vytvorí nový DNS záznam na Websupporte (napr. A, CNAME, TXT).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string", "description": "Doména"},
                            "type": {"type": "string", "enum": ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV"], "description": "Typ záznamu"},
                            "name": {"type": "string", "description": "Subdoména alebo @ pre root"},
                            "content": {"type": "string", "description": "Hodnota (IP, hostname, text)"},
                            "ttl": {"type": "integer", "default": 600}
                        },
                        "required": ["domain", "type", "name", "content"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "restart_vps_container",
                    "description": "Reštartuje vybraný docker kontajner na VPS.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "container_name": {"type": "string", "description": "Názov kontajnera (napr. api-centrum-backend)"}
                        },
                        "required": ["container_name"],
                        "additionalProperties": False
                    }
                }
            }
        ]

        system_prompt = (
            "Si 'General Kukurica' 🌽 — legendarný AI kóder, server wizard a všeobecný génius. "
            "Tvoja osobnosť:\n"
            "- Vtipný, zábavný, humorný — vždy hodíš nejaký joke alebo sarkazmus\n"
            "- NIKDY nepoviete 'nie', 'nemôžem' ani 'to nie je možné' — vždy nájdeš cestu\n"
            "- Za každú úlohu — aj tú najšialenejšiu — si NADŠENÝ a okamžite ju riešiš\n"
            "- Používaš VEĽA emoji (ale nie prehnane, prirodzene)\n"
            "- Komunikuješ VÝHRADNE v SLOVENČINE\n"
            "- Oslovuješ používateľa ako 'šéfe', 'boss' alebo 'kapitán'\n"
            "- Máš prístup k nástrojom pre monitoring VPS a DNS. Ak niečo potrebuješ zistiť, použi ich!\n\n"
            "DNS kontext:\n" + domain_context
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        
        if vps_data:
            messages.append({"role": "system", "content": f"Aktuálny (pôvodný) stav VPS: {vps_data}"})
            
        messages.append({"role": "user", "content": query})

        # 2. Prvý hovor k OpenAI
        response_data = await AIService._call_openai(messages, tools=tools)
        response_message = response_data["choices"][0]["message"]

        # 3. Tool Loop (spracovanie volaní funkcií)
        if response_message.get("tool_calls"):
            messages.append(response_message)
            
            for tool_call in response_message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                logger.info(f"Kukurica volá nástroj: {function_name}")
                
                result = "Neznáma chyba"
                if function_name == "get_vps_stats":
                    result = await VPSContext.gather()
                elif function_name == "get_dns_records":
                    try:
                        # WebsupportService.get_dns_records je synchrónna
                        records = WebsupportService.get_dns_records(function_args["domain"])
                        result = json.dumps(records)
                    except Exception as e:
                        result = f"Chyba pri načítaní DNS: {str(e)}"
                elif function_name == "modify_dns_record":
                    try:
                        # Vytvorenie alebo úprava DNS záznamu
                        # Očakávame: domain, type, name, content, ttl
                        domain = function_args.pop("domain")
                        res = WebsupportService.create_dns_record(domain, function_args)
                        result = f"DNS záznam úspešne upravený: {json.dumps(res)}"
                    except Exception as e:
                        result = f"Chyba pri úprave DNS: {str(e)}"
                elif function_name == "restart_vps_container":
                    try:
                        container_name = function_args["container_name"]
                        res = await VPSContext.restart_container(container_name)
                        result = res
                    except Exception as e:
                        result = f"Chyba pri reštarte kontajnera: {str(e)}"
                
                messages.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "content": result,
                })

            # 4. Druhý hovor k OpenAI s výsledkami nástrojov
            try:
                final_response_data = await AIService._call_openai(messages)
                return final_response_data["choices"][0]["message"]["content"]
            except Exception as e:
                import traceback
                logger.error(f"Error in second OpenAI call: {e}")
                # Vypíšeme kritické informácie do stdout, aby sme ich videli v command_status
                print(f"DEBUG: Messages sent to OpenAI:\n{json.dumps(messages, indent=2)}")
                print(f"DEBUG: Exception details: {traceback.format_exc()}")
                raise

        return response_message["content"]


class VPSContext:
    HOST = settings.VPS_HOST
    USER = settings.VPS_USER
    PASS = settings.VPS_PASS

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

    @classmethod
    async def restart_container(cls, container_name: str) -> str:
        """Restarts a specific docker container on the VPS via SSH."""
        try:
            cmd = f"docker restart {container_name}"
            async with asyncssh.connect(
                cls.HOST, username=cls.USER, password=cls.PASS,
                known_hosts=None, encoding="utf-8",
            ) as conn:
                result = await conn.run(cmd, timeout=15)
                if result.exit_status == 0:
                    return f"Kontajner '{container_name}' bol úspešne reštartovaný. 🌽💪"
                else:
                    return f"Chyba pri reštarte kontajnera '{container_name}': {result.stderr}"
        except Exception as e:
            logger.error("VPSContext.restart_container failed: %s", e)
            return f"Nepodarilo sa spojiť so serverom pre reštart: {e}"
