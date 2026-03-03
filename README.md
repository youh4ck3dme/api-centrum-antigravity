# Domain & SSL Manager

## Popis

FastAPI backend integrujúci Websupport REST API + Vue 3 PWA frontend. Obsahuje SQLAlchemy, Alembic migrácie, JWT autentifikáciu a 2FA (TOTP).

## Rýchle spustenie (dev)

1. Skopíruj backend/.env.example do backend/.env a doplň hodnoty.
2. Backend:
   - cd backend
   - pip install -r requirements.txt
   - uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
3. Frontend:
   - cd frontend
   - npm install
   - npm run dev
4. Migrácie:
   - alembic upgrade head

## Nasadenie s Docker Compose

docker-compose up --build

## Bezpečnostné poznámky

- JWT_SECRET a iné citlivé hodnoty ukladaj mimo repozitára.
- V produkcii obmedz CORS, zapni HTTPS a nastav reverzný proxy (Nginx).
- Certbot vyžaduje porty 80/443; v Docker prostredí rieš s hostom alebo Nginx.
