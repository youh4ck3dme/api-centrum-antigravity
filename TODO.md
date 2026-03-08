# API Centrum — Roadmap

## Nápady na ďalší vývoj

- [ ] 🔴 **Live DNS Threat Monitor (WebSocket)**
  Real-time sledovanie DNS zmien na všetkých doménach každých 60 sekúnd.
  Ak niekto zmení A record, MX record alebo pridá podozrivý CNAME — okamžitá push
  notifikácia v paneli + email alert. Detekcia DNS hijackingu, typosquattingu
  a subdomain takeover. Dashboard sa živí z WebSocket streamu, nie polling.

- [ ] 🤖 **GPT-4 Powered SSL/DNS Autopilot**
  Pripoj OpenAI API — pri každom security audite nech AI reálne opraví zistené
  problémy (chýbajúce SPF, DKIM, DMARC, CAA záznamy). Nielen audit ale aj
  autofix s vysvetlením čo zmenil a prečo. Chat interface kde sa pýtaš
  „Prečo moja doména nedostáva emaily?" a AI pozrie DNS a odpovie.

- [ ] ⚡ **One-Click VPS Provisioning**
  Z panelu klikneš „Nový server" → vybereš lokáciu → API zavolá Hetzner/DigitalOcean
  API, vytvorí VPS, automaticky nakonfiguruje nginx, nainštaluje SSL cert cez
  Let's Encrypt, vytvorí A záznam na Websupport a nasadí Docker stack.
  Celé za ~3 minúty bez dotyku terminálu.

- [ ] 📊 **Domain Portfolio Intelligence**
  Analýza expirácie domén s predikciou — ktoré domény sú rizikové (expirujú
  za menej ako 30 dní), koľko ťa stoja ročne, hodnota portfolia. Automatické
  obnovenie cez Websupport API ak je dostupné. Plus competitor monitoring —
  sleduj či niekto nezaregistroval podobnú doménu ako tvoja
  (napr. `nexify-studios.tech`, `nexify-studio.sk`).


https://studio-2491913884-9484a.web.app/dashboard - dalsie napady z mojeho projektu !