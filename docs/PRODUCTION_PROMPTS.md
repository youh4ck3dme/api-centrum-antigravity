# 🚀 API Centrum — 8 Produkčných Promptov

> Tieto prompty spúšťaj **postupne (1→8)** v novom AI chate. Každý stavia na predchádzajúcom.
> Odhadovaný čas: 3-5 hodín postupne.

---

## PROMPT 1: 🧹 Čistenie repozitára & bezpečnosť

```
Vyčisti repozitár API Centrum pre produkciu:

1. BEZPEČNOSŤ — KRITICKÉ:
   - Skontroluj či backend/.env nie je trackovaný gitom. Ak áno, pridaj ho do .gitignore a odstráň z git histórie (git rm --cached).
   - Skontroluj celý repozitár na hardcoded secrets, API kľúče, heslá — nahraď ich environment variable references.
   - V backend/app/auth_composite.py odstráň hardcoded fallback user "larsenevans@proton.me" (riadky 62-65). Ak autentifikácia zlyhá, vždy vráť 401.

2. ČISTENIE SÚBOROV:
   - Odstráň z repozitára: Untitled-1.ini, backend_crash.log, build_log_utf8.txt, apicentrumfuncton.zip, image.png, backend/test_tmp.db, backend/verify_migration.db, backend/api_centrum.db, backend/test_errors.log, frontend/build_debug.txt, frontend/build_output.txt, frontend/get_node_procs.py, backend/check_users.py, backend/verify_pw.py, backend/verify_pw_short.py, tmp/inspect_db.py
   - Odstráň duplikovaný pnpm-lock.yaml (ponechaj len package-lock.json)
   - Pridaj všetky vymazané patterny do .gitignore

3. GITIGNORE VYLEPŠENIA:
   - Pridaj: *.db (bez výnimiek), *.log, *.zip, *.ini, *.tar.gz, frontend/build_*.txt, tmp/

4. FIX SYNTAX:
   - V backend/app/ai_service.py odstráň duplikovaný @staticmethod dekorátor na riadku 13-14 (nechaj len jeden).

Po každej zmene urob git add + commit s popisným message.
```

---

## PROMPT 2: 🔒 Backend bezpečnostný hardening

```
Zaharduj backend API Centrum pre produkčné nasadenie:

1. CORS KONFIGURÁCIA (backend/app/main.py):
   - Nahraď allow_origins=["*"] za dynamický zoznam z settings.CORS_ORIGINS
   - CORS_ORIGINS má byť split(",") zo settings
   - Aktualizuj backend/app/config.py — pridaj produkčné origins pre Vercel domény

2. SECURITY HEADERS:
   - CSP musí povoliť 'unsafe-inline' pre Vue.js scoped styles a Google Fonts
   - Pridaj X-XSS-Protection header
   - HSTS len v production

3. AUTH HARDENING:
   - V auth_composite.py: CompositeAuthService.authenticate_composite — ak Neon trial nie je aktívny A lokálne JWT zlyhá, vráť 401 VŽDY, žiadny fallback
   - Rate limiting na /auth/login: 5/minute je OK, skontroluj že funguje
   - Refresh token endpoint musí validovať token_type === "refresh"

4. PRODUKČNÁ DATABÁZA:
   - V config.py nastav default DATABASE_URL na prázdny string pre produkciu (nie sqlite)
   - Pridaj validáciu: ak ENV=production a DATABASE_URL obsahuje "sqlite", raise RuntimeError
   - Uisti sa že db.py správne handluje PostgreSQL connection args (bez check_same_thread)

5. STARTUP MODERNIZÁCIA:
   - Nahraď @app.on_event("startup") za FastAPI lifespan context manager
   - Pridaj graceful shutdown pre background tasks (dns_poll_loop, ssl_poll_loop)

Commitni s message: "security: harden backend for production deployment"
```

---

## PROMPT 3: 🌐 Frontend Vercel deployment konfigurácia

```
Nastav frontend API Centrum pre produkčný deployment na Vercel:

1. VERCEL KONFIGURÁCIA:
   - Vytvor frontend/vercel.json:
     {
       "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
       "headers": [
         {
           "source": "/(.*)",
           "headers": [
             { "key": "X-Content-Type-Options", "value": "nosniff" },
             { "key": "X-Frame-Options", "value": "DENY" },
             { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
           ]
         },
         {
           "source": "/assets/(.*)",
           "headers": [
             { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
           ]
         }
       ]
     }

2. ENV VARIABLES:
   - Aktualizuj frontend/.env.production:
     VITE_API_URL=https://api.nexify-studio.tech/api  (alebo tvoja produkčná URL s HTTPS!)
     VITE_WS_URL=wss://api.nexify-studio.tech/ws
     VITE_APP_NAME=API Centrum
   - Oprav frontend/src/api/api.js — pridaj lepšiu error handling pre network errors

3. BUILD OPTIMALIZÁCIA (vite.config.mjs):
   - Odstráň dev proxy z production buildu (zabaľ server.proxy do podmienky)
   - Pridaj chunk splitting pre xterm.js (je veľký ~600KB)
   - Nastav build.target na 'es2020' pre moderné browsery
   - Pridaj build.sourcemap: false pre produkciu

4. PWA ASSETS:
   - Skontroluj že existujú všetky ikony referencované v manifest (pwa-192x192.png, pwa-512x512.png, icons/*)
   - Pridaj robots.txt do frontend/public/
   - Pridaj favicon.ico ak chýba

5. INDEX.HTML SEO:
   - Pridaj meta description
   - Pridaj Open Graph tagy
   - Pridaj apple-touch-icon link

Commitni: "feat: configure frontend for Vercel production deployment"
```

---

## PROMPT 4: 🎨 UI/UX polish & konzistencia

```
Oprav vizuálne problémy a vylepši UI konzistenciu v API Centrum frontende:

1. TAILWIND CSS THEME FIX (frontend/src/tailwind.css):
   - Login.vue používa triedy ako bg-bg-surface, text-text-main, bg-overlay-hover, border-border-subtle, text-text-dim, bg-primary-indigo, bg-primary-cyan, text-accent-green, text-accent-rose
   - Tieto triedy NIE SÚ definované v @theme bloku. Pridaj ich:
     --color-text-main: #EDEDED
     --color-text-dim: #888888
     --color-bg-surface: #16181D
     --color-border-subtle: rgba(255, 255, 255, 0.08)
     --color-border-default: rgba(255, 255, 255, 0.14)
     --color-overlay-hover: rgba(255, 255, 255, 0.05)
     --color-primary-indigo: #6366F1
     --color-primary-cyan: #06B6D4
     --color-accent-rose: #F43F5E
     --color-accent-green: #10B981
   - Uisti sa že font-password class funguje (ak neexistuje, pridaj do CSS)

2. LOADING STATES:
   - Pridaj loading skeleton do Dashboard.vue (pred načítaním dát)
   - Pridaj error boundary do App.vue (zachytenie chýb v async komponentoch)
   - Pridaj Suspense wrapper okolo defineAsyncComponent views

3. RESPONZIVITA:
   - Skontroluj mobile layout vo všetkých views (najmä Dashboard grid, Sidebar collapse)
   - Login.vue rounded-[48px] je príliš veľa na mobile — použi responsive: rounded-3xl lg:rounded-[48px]

4. ANIMÁCIE:
   - Pridaj animate-in utility class ak chýba
   - Sidebar activeTab pill by mal mať smooth transition (nie instant jump)

5. DARK MODE KONZISTENCIA:
   - Všetky views musia používať theme variables (nie hardcoded farby)
   - Skontroluj že všetky hover stavy sú konzistentné

Commitni: "style: fix theme variables, add loading states, polish UI consistency"
```

---

## PROMPT 5: ⚡ API & Data layer robustnosť

```
Sprav API vrstvu robustnú a produkčne kvalitnú:

1. FRONTEND API LAYER (frontend/src/api/api.js):
   - Pridaj retry logiku (3 pokusy s exponential backoff) pre 5xx chyby a network errors
   - Pridaj request/response logging v development mode
   - Pridaj offline detection — ak je navigator.onLine === false, zobraz notifikáciu
   - Pridaj token refresh flow pred 401 redirect (skús refresh token, ak zlyhá, potom redirect)

2. COMPOSABLES ROBUSTNOSŤ:
   - useStats.js: pridaj error handling pre všetky API calls, pridaj retry, pridaj stale-while-revalidate pattern
   - useWebSocket.js: pridaj reconnect logiku s backoff
   - useTerminal.js: skontroluj memory leaky (xterm instance cleanup)

3. BACKEND ERROR HANDLING:
   - V main.py pridaj global exception handler pre unhandled errors (vráť 500 s generickou správou, loguj detail)
   - Všetky route handlery musia vrátiť konzistentný response format: { "success": bool, "data": ..., "error": string|null }
   - Pridaj request_id do každého response headeru pre tracing

4. BACKEND HEALTH CHECKS:
   - Vylepši /health endpoint — skontroluj DB connectivity, Websupport API stav
   - Pridaj /health/ready a /health/live endpointy pre container orchestration

5. LOGGING:
   - Nastav structured logging (JSON format) pre produkciu
   - Pridaj correlation/request ID do všetkých logov
   - Odstráň print() statements z ai_service.py (riadky 232-233)

Commitni: "feat: robust API layer with retry, error handling, and health checks"
```

---

## PROMPT 6: 🧪 Testy & CI/CD pipeline

```
Nastav testy a CI/CD pre API Centrum:

1. BACKEND TESTY:
   - Prejdi existujúce testy v backend/tests/ — oprav tie čo padajú
   - Spusti: cd backend && python -m pytest tests/ -v --tb=short
   - Oprav importy a fixtures podľa aktuálnych modelov
   - Pridaj test pre /health endpoint
   - Pridaj test pre auth flow (register → login → refresh → protected endpoint)

2. FRONTEND TESTY:
   - Skontroluj/oprav existujúce testy v frontend/src/__tests__/
   - Spusti: cd frontend && npx vitest run --reporter=verbose
   - Pridaj test pre api.js interceptory
   - Pridaj test pre Login.vue (mount, submit, error state)

3. GITHUB ACTIONS CI:
   - Vytvor .github/workflows/ci.yml:
     - Trigger: push to main, pull_request
     - Job 1: Backend tests (Python 3.11, pip install -r requirements.txt, pytest)
     - Job 2: Frontend (Node 20, npm ci, npm run build, npx vitest run)
     - Job 3: Lint (ruff pre Python, eslint pre Vue — ak sú nastavené)

4. GITHUB ACTIONS CD (Vercel):
   - Vytvor .github/workflows/deploy.yml:
     - Trigger: push to main (po CI success)
     - Deploy frontend na Vercel cez Vercel CLI alebo GitHub integration
     - Nastav Vercel project scope na frontend/ directory

Commitni: "ci: add test fixes and GitHub Actions CI/CD pipeline"
```

---

## PROMPT 7: 📱 PWA & Performance optimalizácia

```
Optimalizuj PWA a performance pre produkciu:

1. PWA MANIFEST:
   - Skontroluj frontend/vite.config.mjs VitePWA config
   - Pridaj workbox runtime caching pre API calls (NetworkFirst stratégia pre /api/*)
   - Pridaj offline fallback page
   - Oprav ikony — icons musia mať rozličné purpose (any vs maskable, nie obe naraz)
   - Pridaj screenshots pole do manifest pre install prompt

2. SERVICE WORKER:
   - Nastav skipWaiting a clientsClaim pre okamžitú aktiváciu
   - Pridaj cache stratégie: CacheFirst pre static assets, NetworkFirst pre API
   - Pridaj navigateFallback na /index.html

3. PERFORMANCE:
   - Analyzuj bundle veľkosť: npx vite-bundle-analyzer (alebo rollup-plugin-visualizer)
   - xterm + addon-fit (~600KB) — lazy load len keď user otvorí Terminal tab
   - lucide-vue-next — uisti sa že tree-shaking funguje (importuj len použité ikony)
   - Pridaj loading="lazy" na obrázky
   - Pridaj font-display: swap do Google Fonts linku v index.html

4. LIGHTHOUSE AUDIT:
   - Po builde spusti Lighthouse audit
   - Cieľ: Performance 90+, Accessibility 90+, Best Practices 90+, SEO 90+
   - Oprav čo treba na dosiahnutie týchto metrík

5. CAPACITOR/ANDROID:
   - Skontroluj capacitor.config.json — ak nie je potrebný pre MVP, odstráň android/ folder a @capacitor deps z package.json (zmenšenie bundle)

Commitni: "perf: optimize PWA, bundle size, and achieve Lighthouse 90+"
```

---

## PROMPT 8: 🚀 Finálny deploy + E2E smoke test

```
Finálny deployment a end-to-end verifikácia API Centrum:

1. PRE-DEPLOY CHECKLIST:
   - [ ] Všetky .env súbory sú v .gitignore
   - [ ] Žiadne hardcoded secrets v kóde
   - [ ] CORS nastavený na konkrétne domény (nie "*")
   - [ ] Frontend build prebehne bez chýb: cd frontend && npm run build
   - [ ] Backend testy prejdú: cd backend && python -m pytest tests/ -v
   - [ ] Frontend testy prejdú: cd frontend && npx vitest run
   - [ ] vercel.json existuje a je správny

2. VERCEL DEPLOY:
   - Skontroluj/nastav Vercel projekt:
     - Root Directory: frontend
     - Build Command: npm run build
     - Output Directory: dist
     - Framework: Vite
   - Nastav Vercel environment variables:
     - VITE_API_URL = https://tvoja-api-domena/api
     - VITE_WS_URL = wss://tvoja-api-domena/ws
     - VITE_APP_NAME = API Centrum

3. SMOKE TEST (po deployi):
   Otvor produkčnú URL v prehliadači a over:
   - [ ] Login stránka sa zobrazí správne
   - [ ] Login funguje (email + heslo)
   - [ ] Dashboard sa načíta s dátami
   - [ ] Navigácia medzi tabmi funguje
   - [ ] Command palette (Ctrl+K) funguje
   - [ ] API volania idú na správnu produkčnú URL (nie localhost)
   - [ ] WebSocket connection sa nadviaže
   - [ ] PWA install prompt sa zobrazí
   - [ ] Mobile layout funguje
   - [ ] Logout funguje

4. MONITORING POST-DEPLOY:
   - Over Sentry integráciu — vyvolaj test error a skontroluj Sentry dashboard
   - Over Prometheus metriky na /metrics endpoint
   - Skontroluj VPS health cez /health endpoint

5. DOKUMENTÁCIA:
   - Aktualizuj README.md s:
     - Produkčná URL
     - Environment variables zoznam
     - Deploy postup
     - Architecture diagram (text-based)

Commitni: "release: v1.0.0 — production-ready API Centrum"
```

---

## 📋 PORADIE

```
1️⃣  PROMPT 1 → Čistenie (základ)
2️⃣  PROMPT 2 → Bezpečnosť (backend)
3️⃣  PROMPT 3 → Vercel config (frontend deploy)
4️⃣  PROMPT 4 → UI polish (vizuálna kvalita)
5️⃣  PROMPT 5 → API robustnosť (stabilita)
6️⃣  PROMPT 6 → Testy + CI/CD (kvalita)
7️⃣  PROMPT 7 → PWA + Performance (rýchlosť)
8️⃣  PROMPT 8 → Deploy + Smoke test (DONE! 🎉)
```
