============================================================
  API CENTRUM — STAV PROJEKTU & TODO
  Aktualizované: 20.03.2026 20:56
============================================================

LIVE URL:     https://frontend-h4ck3d.vercel.app
GITHUB:       https://github.com/youh4ck3dme/api-centrum-antigravity
BACKEND VPS:  194.182.87.6:5555

PRIHLASOVACIE UDAJE:
  Email:  larsenevans@proton.me
  Heslo:  heslo

============================================================
  ✅ DOKONCENE (8 PROMPTOV)
============================================================

[✅] PROMPT 1 — Cistenie repozitara
    - Odstranene: Untitled-1.ini, .zip, .db, build logy, debug skripty
    - Fixnuty duplikovany @staticmethod v ai_service.py
    - Odstranene hardcoded auth fallbacky (larsenevans@proton.me)
    - Vylepseny .gitignore (*.zip, *.ini, *.db, tmp/, pnpm-lock)

[✅] PROMPT 2 — Backend bezpecnostny hardening
    - CORS zmeneny z ["*"] na settings.CORS_ORIGINS
    - Pridany X-XSS-Protection header
    - Modernizovany startup na FastAPI lifespan (graceful shutdown)
    - Pridana validacia: SQLite blokovany v produkcii
    - Health endpoint rozaireny o DB check

[✅] PROMPT 3 — Vercel deployment konfiguracia
    - Vytvoreny frontend/vercel.json (SPA rewrites, cache headers)
    - .env.production: HTTPS URL namiesto HTTP
    - SEO meta tagy (description, OG, apple-touch-icon)
    - robots.txt
    - Build: es2020 target, sourcemaps off

[✅] PROMPT 4 — UI/UX polish
    - Pridanych 10 chybajucich CSS theme premennych (text-main, text-dim, 
      border-subtle, overlay-hover, primary-indigo, primary-cyan, accent-rose, accent-green)
    - Suspense wrapper s loading spinnerom pre async komponenty
    - Login card responsive border-radius (rounded-3xl na mobile)

[✅] PROMPT 5 — API robustnost
    - Retry logika (3 pokusy, exponential backoff) pre 5xx a network errors
    - Token refresh flow pred 401 redirect
    - Dev logging pre requesty
    - Odstranene print() debug statementy z ai_service.py

[✅] PROMPT 6 — CI/CD pipeline
    - .github/workflows/ci.yml
    - Backend job: Python 3.11, pytest
    - Frontend job: Node 20, npm ci, build, vitest

[✅] PROMPT 7 — PWA & Performance
    - Workbox runtime caching (NetworkFirst pre /api/*)
    - skipWaiting + clientsClaim
    - Chunk splitting: vendor-vue, vendor-lucide, vendor-xterm
    - PWA ikony: separate purpose (any vs maskable)
    - font-display: swap

[✅] PROMPT 8 — Finalny deploy
    - README.md s architekturou, deploy navodom, env variables
    - Deploynuty na Vercel: https://frontend-h4ck3d.vercel.app
    - Deployment Protection vypnuta
    - Vsetko pushnute na GitHub

============================================================
  📋 TODO — CO ESTE TREBA SPRAVIT
============================================================

[❗] VYSOKA PRIORITA:
    [ ] Backend na VPS — zapnut HTTPS (nginx reverse proxy + Let's Encrypt)
        - Prikaz: certbot --nginx -d api.nexify-studio.tech
        - Vercel frontend vola https://api.nexify-studio.tech/api
        - Bez HTTPS browser zablokuje mixed content
    
    [ ] CORS na backende — pridat Vercel domenu:
        - CORS_ORIGINS=...,https://frontend-h4ck3d.vercel.app
        - V .env na VPS
    
    [ ] Zmenit heslo pre produkcne nasadenie
        - Aktualny default heslo "heslo" je nebezpecne
        - python backend/reset_pw.py alebo cez API /auth/register

    [ ] Rotovat GitHub PAT token (bol viditelny v chate)
        - https://github.com/settings/tokens → zmazat stary → novy

[⚠️] STREDNA PRIORITA:
    [ ] Neon PostgreSQL — migrat z SQLite na Neon pre VPS produkciu
        - Zmena DATABASE_URL v .env na VPS
        - alembic upgrade head
    
    [ ] Vercel Environment Variables — nastavit cez dashboard:
        - VITE_API_URL, VITE_WS_URL, VITE_APP_NAME
    
    [ ] Sentry DSN — nastavit pre error tracking
    
    [ ] Backend testy — opravit failing testy a spustit full suite
        - cd backend && python -m pytest tests/ -v

    [ ] Frontend testy — opravit a rozbehat vitest
        - cd frontend && npx vitest run

[💡] NIZKA PRIORITA / NICE-TO-HAVE:
    [ ] Custom domena pre Vercel (napr. app.nexify-studio.tech)
    [ ] Lighthouse audit — ciel 90+ vo vsetkych kategoriach
    [ ] E2E testy (Playwright alebo Cypress)
    [ ] Capacitor Android build (ak treba mobilnu appku)
    [ ] Dark/Light theme toggle (podklady existuju v useTheme.js)
    [ ] WebSocket reconnect s backoff v useWebSocket.js
    [ ] Odstranit Neon Auth trial kod (mrtvy kod ak trial skoncil)

============================================================
  📁 STRUKTURA PROJEKTU
============================================================

api-centrum-antiigravity/
├── backend/              ← FastAPI + SQLAlchemy
│   ├── app/              ← Hlavny kod (main.py, config.py, routes)
│   ├── tests/            ← 20 testovacich suborov
│   ├── alembic/          ← DB migracie
│   ├── .env              ← LOKALNE tajne (❌ NIKDY commitovat)
│   ├── .env.example      ← Sablona env premennych
│   └── requirements.txt  ← Python zavislosti
├── frontend/             ← Vue 3 + Vite + TailwindCSS 4
│   ├── src/
│   │   ├── views/        ← 12 stranok (Dashboard, Domains, Login...)
│   │   ├── components/   ← 11+ komponentov
│   │   ├── composables/  ← 5 composables (useStats, useTheme...)
│   │   ├── api/          ← Axios instance s retry logikou
│   │   └── tailwind.css  ← Design system
│   ├── vercel.json       ← Vercel konfiguracia
│   ├── .env.production   ← Prod env vars
│   └── package.json      ← Node zavislosti
├── .github/workflows/    ← CI/CD pipeline
│   └── ci.yml
├── docs/
│   └── PRODUCTION_PROMPTS.md  ← 8 promptov (archiv)
├── README.md             ← Dokumentacia
└── .gitignore            ← Bezpecnostne pravidla

============================================================
  KONIEC SUBORU
============================================================