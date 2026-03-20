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

## Roadmap: Chýbajúce Super Funkcie (Prompty pre AI)

Tu je zoznam funkcií, ktoré posunú projekt na úroveň profesionálneho SaaS, spolu s promptami na ich realizáciu:

### 1. 🤖 Radar AI (Interaktívny Copilot)
- **Prompt**: *"Implementuj do pohľadu Radar.vue interaktívne chatovacie rozhranie (AI Copilot) v štýle Apple. Napoj ho na backend endpointy v ai_routes.py. Copilot musí mať prístup k aktuálnym dátam z dashboardu, aby vedel odpovedať na otázky typu 'Ktorá doména expruje prvá?' alebo 'Analyzuj výkon môjho VPS'. Použi moderný glassmorphism dizajn a plynulé animácie písania."*

### 2. 🌐 Full Websupport Management (DNS & SSL)
- **Prompt**: *"Rozšír modul Websupport.vue tak, aby umožňoval plný manažment DNS záznamov (A, CNAME, MX). Implementuj modálne okná pre pridanie a editáciu záznamov pomocou funkcií v websupport.py. Pridaj vizuálnu indikáciu stavu SSL certifikátov a tlačidlo 'Obnoviť certifikát', ktoré zavolá príslušnú API akciu. Celé rozhranie musí byť v 1px precision dizajne."*

### 3. 🔔 Aktívny Monitoring & Push Notifikácie
- **Prompt**: *"Vytvor v App.vue a api.js systém pre spracovanie real-time notifikácií. Využi možnosti PWA (Service Workers) pre zasielanie push správ, ak backend v monitoring/ detectne výpadok (status 404/500). Pridaj do Sidebar.vue funkčný zvonček s badgeom počtu neprečítaných upozornení a panel s históriou incidentov."*

### 4. 📈 Historické Grafy (Performance Analytics)
- **Prompt**: *"Implementuj do Performance.vue a VPS.vue grafy (použi Chart.js alebo Vue-Chartjs), ktoré budú zobrazovať históriu vyťaženia CPU, RAM a sieťovej prevádzky za posledných 24 hodín. Uprav backend v performance/ tak, aby ukladal minútové snapshoty do databázy a poskytoval ich cez nový endpoint /metrics/history. Grafy musia ladiť s tmavým 'Pure Black' dizajnom (neónové čiary, jemné gradienty)."*

### 5. 💻 Funkčný SSH Terminál (xterm.js)
- **Prompt**: *"Premeň Terminal.vue na reálne funkčnú konzolu pomocou knižnice xterm.js. Na backende v terminal/ vytvor WebSocket server, ktorý bude tunelovať príkazu cez SSH na definované VPS servery. Implementuj podporu pre uloženie viacerých SSH profilov (host, meno, kľúč) a zabezpeč šifrovaný prenos dát."*

### 6. 💳 Licenčný a Fakturačný Portál
- **Prompt**: *"Vytvor pohľad Billing.vue (alebo rozšír Settings.vue), kde si používateľ môže spravovať svoje predplatné. Implementuj zobrazenie aktuálnej licencie pomocou dát z license_routes.py, zoznam faktúr v PDF a tlačidlá na upgrade balíka. Integruj vizuálny indikátor platnosti licencie ('Aktívna', 'Expruje', 'Neplatná')."*

### 7. ⌘K Global Search (Command Palette)
- **Prompt**: *"Implementuj globálnu 'Command Palette' (ako v Raycast alebo macOS Spotlight), ktorá sa otvorí po stlačení ⌘K (alebo CTRL+K). Paleta musí umožňovať okamžité vyhľadávanie v doménach, navigáciu medzi sekciami a rýchle akcie ako 'Pridať doménu' alebo 'Reštartovať VPS'. Použi hlboký blur efekt a ultra-rýchlu odozvu."*

---
https://studio-2491913884-9484a.web.app/dashboard - dalsie napady z mojeho projektu !