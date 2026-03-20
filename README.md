# API Centrum — Nexify Monitoring Platform

> Full-stack infraštruktúra monitoring & management platforma.

## 🏗️ Architektúra

```
┌─────────────────────────────────────────────┐
│              FRONTEND (Vercel)              │
│  Vue 3 + Vite 5 + TailwindCSS 4 + PWA     │
│  12 views • 11+ komponentov • 5 composables│
└─────────────────┬───────────────────────────┘
                  │ HTTPS / WSS
┌─────────────────▼───────────────────────────┐
│              BACKEND (VPS)                  │
│  FastAPI + SQLAlchemy + Alembic             │
│  15 route skupín • AI (GPT-4o)             │
│  Websupport API • SSH/VPS • DynDNS         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           DATABASE (PostgreSQL)             │
│  Neon PostgreSQL (prod) / SQLite (dev)      │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

### Backend (Development)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # vyplň reálne hodnoty
uvicorn app.main:app --reload --port 8000
```

## 🌐 Deployment

### Frontend → Vercel
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Framework**: Vite

### Vercel Environment Variables
| Premenná | Hodnota |
|----------|---------|
| `VITE_API_URL` | `https://api.nexify-studio.tech/api` |
| `VITE_WS_URL` | `wss://api.nexify-studio.tech/ws` |
| `VITE_APP_NAME` | `API Centrum` |

### Backend → VPS
```bash
./deploy.ps1
```

## 🔐 Environment Variables (Backend)

| Premenná | Popis | Povinné |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Prod |
| `JWT_SECRET` | Min 32 znakov | ✅ Prod |
| `ENV` | `development` / `production` | ✅ |
| `WEBSUPPORT_API_KEY` | Websupport API kľúč | Pre DNS |
| `WEBSUPPORT_SECRET` | Websupport secret | Pre DNS |
| `OPENAI_API_KEY` | GPT-4o pre AI Autopilot | Pre AI |
| `VPS_HOST`, `VPS_USER`, `VPS_PASS` | SSH prístup na VPS | Pre VPS mgmt |
| `CORS_ORIGINS` | Povolené origins (čiarkou oddelené) | ✅ Prod |
| `ALLOWED_HOSTS` | Povolené hostnames | ✅ Prod |

## 📦 Funkcie

- **Dashboard** — real-time monitoring, system health, activity feed
- **Domény** — Websupport DNS management, WHOIS, expiry tracking
- **DNS Monitor** — live DNS polling, AI audit, auto-fix
- **AI Chat** — "General Kukurica" 🌽 s function calling (DNS, VPS kontrola)
- **VPS Management** — SSH, Docker reštart, disk/RAM metriky
- **Radar** — domain portfolio intelligence, competitor watch
- **Terminal** — web-based SSH klient (xterm.js)
- **GitHub Profile** — GitHub aktivita widget
- **PWA** — offline support, installable, push notifikácie ready

## 🧪 Testy

```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend
cd frontend && npx vitest run
```

## 📄 License

Private — Nexify Studio © 2026
