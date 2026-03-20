# API Centrum - Lovable.dev Export Guide

Tento dokument slúži ako prehľad kľúčových funkcií projektu `api-centrum` pre implementáciu v prostredí `lovable.dev` a prehliadači PANDORA.

## Kľúčové Funkcie (Super Funkcie)

### 1. Autentifikačný Systém (Auth SDK)
- **Hybridná Autentifikácia**: Podpora pre lokálne JWT tokeny aj integráciu s Neon Auth (pre trial obdobia).
- **Bezpečnosť**: Automatické spracovanie 401 chýb (unauthorized) a bezpečná správa relácií.
- **Spracovanie**: Pozrite súbory `backend/app/auth.py` a `frontend/src/api/api.js`.

### 2. Dynamický Dashboard & Monitoring
- **Real-time Štatistiky**: Načítavanie dát o VPS, doménach a SSL certifikátoch.
- **Vizuálna Spätná Väzba**: Animované "flash" karty pri zmene hodnôt.
- **Implementácia**: Hlavné súčasti sú v `frontend/src/composables/useStats.js` a `frontend/src/views/Dashboard.vue`.

### 3. GitHub Profile Engine (ResendHub Style)
- **GHP Integrácia**: Synchronizácia s GitHub API pomocou osobného tokenu.
- **Prémiový Dizajn**: Čisté čierne pozadie (#000000), sklenené karty, graf kontribúcií a dynamický výpis aktivity s kódovými blokmi.
- **Dôležité**: Súbor `frontend/src/views/GithubProfile.vue` obsahuje kompletnú vizuálnu a logickú časť.

### 4. Systémová Architektúra
- **Backend (FastAPI)**: Modulárne routovanie (`backend/app/main.py`), PostgreSQL (Neon) a SQLite kompatibilita.
- **Frontend (Vue 3 + Vite)**: Moderný prístup k správe stavu cez composables a Apple-style UI.

## Inštrukcie pre Implementáciu

1. **Vizuál**: Dodržujte "Pure Black" estetiku pre všetky nové panely.
2. **Konektivita**: Použite priložený `api.js` ako vzor pre interceptory a správu tokenov.
3. **Komponenty**: Čerpajte zo `Sidebar.vue` pre modernú a responsívnu navigáciu.

---
Vygenerované pre: **PANDORA BROWSER / lovable.dev**
Dátum: 2026-03-19
