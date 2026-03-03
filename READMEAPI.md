# API Centrum PWA - Kompletná dokumentácia

## Obsah
1. [Prehľad systému](#prehľad-systému)
2. [Inštalácia a spustenie](#inštalácia-a-spustenie)
3. [Konfigurácia](#konfigurácia)
4. [API Endpoints](#api-endpoints)
5. [Websupport API integrácia](#websupport-api-integrácia)
6. [Autentifikácia a 2FA](#autentifikácia-a-2fa)
7. [SSL certifikáty](#ssl-certifikáty)
8. [Frontend - PWA](#frontend---pwa)
9. [Docker deployment](#docker-deployment)
10. [Troubleshooting](#troubleshooting)

---

## 1. Prehľad systému

API Centrum je komplexný systém pre správu domén a SSL certifikátov cez Websupport API.

### Architektúra
- **Backend**: FastAPI (Python) - REST API
- **Frontend**: Vue 3 + PWA - Webová aplikácia
- **Databáza**: PostgreSQL
- **Kontajnerizácia**: Docker + Docker Compose

### Funkcionalita
- Správa domén cez Websupport API
- Generovanie SSL certifikátov (Let's Encrypt)
- JWT autentifikácia
- 2FA (TOTP) podpora
- PWA - možnosť inštalácie ako aplikácia

---

## 2. Inštalácia a spustenie

### 2.1 Lokálny vývoj (bez Docker)

#### Backend
`ash
cd backend

# Vytvor virtuálne prostredie
python -m venv venv
source venv/bin/activate  # Linux/Mac
# alebo
venv\Scripts\activate     # Windows

# Nainštaluj závislosti
pip install -r requirements.txt

# Skopíruj a uprav .env
cp .env.example .env
# Uprav hodnoty v .env súbore

# Spusti migrácie
alembic upgrade head
# Alebo pre dev:
python -c \"from app.db import Base, engine; Base.metadata.create_all(bind=engine)\"

# Spusti server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
`

#### Frontend
`ash
cd frontend

# Nainštaluj závislosti
npm install

# Spusti vývojový server
npm run dev
`

#### Prístup
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### 2.2 Docker Compose (odporúčané)

`ash
# Skopíruj .env.example a uprav hodnoty
cp backend/.env.example backend/.env
nano backend/.env

# Spusti všetky služby
docker-compose up --build

# Alebo na pozadí
docker-compose up -d --build
`

---

## 3. Konfigurácia

### 3.1 Environment premenné

Vytvor súbor ackend/.env:

`env
# Websupport API (povinné)
WEBSUPPORT_API_KEY=your_api_key_here
WEBSUPPORT_SECRET=your_secret_here

# Databáza
DATABASE_URL=postgresql://postgres:password@postgres:5432/postgres

# SSL (Certbot)
CERTBOT_EMAIL=admin@mojadomena.sk

# JWT
JWT_SECRET=velmi-tajny-retazec-min-32-znakov
JWT_EXPIRE_MINUTES=1440

# Prostredie
ENV=production

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=postgres
`

### 3.2 Websupport API kľúče

1. Prihlás sa do Websupport administrácie
2. Choď do Nastavenia > API
3. Vytvor nový API kľúč
4. Skopíruj API Key a Secret do .env

---

## 4. API Endpoints

### 4.1 Zdravie systému
`
GET /health
`

Odpoveď:
`json
{
  \"status\": \"ok\",
  \"env\": \"production\"
}
`

### 4.2 Domény

#### Zoznam domén
`
GET /api/domains
`

#### Vytvorenie domény
`
POST /api/domains
Content-Type: application/json

{
  \"name\": \"mojadomena.sk\",
  \"description\": \"Hlavná doména\"
}
`

### 4.3 SSL certifikáty

#### Generovanie SSL
`
POST /api/ssl/generate
Content-Type: application/json

{
  \"domain\": \"mojadomena.sk\",
  \"email\": \"admin@mojadomena.sk\"
}
`

### 4.4 Používatelia

#### Registrácia
`
POST /api/users/register
Content-Type: application/json

{
  \"email\": \"admin@mojadomena.sk\",
  \"password\": \"tajne-heslo\"
}
`

#### Prihlásenie
`
POST /api/users/login
Content-Type: application/json

{
  \"email\": \"admin@mojadomena.sk\",
  \"password\": \"tajne-heslo\",
  \"totp\": \"123456\"  # voliteľné, ak je 2FA aktivované
}
`

Odpoveď:
`json
{
  \"access_token\": \"eyJ0eXAiOiJKV1QiLCJhbGc...\",
  \"token_type\": \"bearer\"
}
`

#### Aktuálny používateľ
`
GET /api/users/me
Authorization: Bearer <token>
`

#### Nastavenie 2FA
`
POST /api/users/2fa/setup
Authorization: Bearer <token>
`

#### Overenie 2FA
`
POST /api/users/2fa/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  \"token\": \"123456\",
  \"secret\": \"JBSWY3DPEHPK3PXP\"
}
`

---

## 5. Websupport API integrácia

### 5.1 Autentifikácia

Systém používa HMAC SHA1 autentifikáciu pre Websupport API:

`python
# Automaticky generované v app/websupport.py
timestamp = int(time.time())
canonical_request = f\"GET /v2/service/domains {timestamp}\"
signature = hmac.new(secret.encode(), canonical_request.encode(), hashlib.sha1).hexdigest()
`

### 5.2 Dostupné operácie

- **GET /v2/service/domains** - Zoznam domén
- **POST /v2/service/domains** - Vytvorenie domény
- **GET /v2/service/domains/{id}** - Detail domény
- **DELETE /v2/service/domains/{id}** - Vymazanie domény
- **GET /v2/user/me** - Info o účte

---

## 6. Autentifikácia a 2FA

### 6.1 JWT Tokeny

- Tokeny expirovanú po 1440 minútach (24 hodín)
- Ukladajú sa v hlavičke: Authorization: Bearer <token>

### 6.2 2FA (Two-Factor Authentication)

1. **Aktivácia 2FA:**
   - Prihlás sa do systému
   - Choď do profilu
   - Klikni na \"Nastaviť 2FA\"
   - Naskenuj QR kód v aplikácii (Google Authenticator, Authy, atď.)
   - Zadaj 6-miestny kód na overenie

2. **Prihlásenie s 2FA:**
   - Zadaj email a heslo
   - Zadaj 6-miestny kód z autentifikačnej aplikácie

---

## 7. SSL certifikáty

### 7.1 Generovanie nového certifikátu

`ash
# Cez API
curl -X POST http://localhost:8000/api/ssl/generate \\
  -H \"Content-Type: application/json\" \\
  -d '{\"domain\": \"mojadomena.sk\", \"email\": \"admin@mojadomena.sk\"}'
`

### 7.2 Automatická obnova

Certifikáty sa ukladajú do:
- /etc/letsencrypt/live/<domain>/fullchain.pem
- /etc/letsencrypt/live/<domain>/privkey.pem

Pre automatickú obnovu nastav cron:
`ash
certbot renew --post-hook \"systemctl reload nginx\"
`

---

## 8. Frontend - PWA

### 8.1 Inštalácia aplikácie

1. Otvor v prehliadači: http://localhost:3000
2. Klikni na \"Inštalovať\" (alebo v menu prehliadača)
3. Aplikácia sa nainštaluje ako samostatná app

### 8.2 Funkcie

- **Dashboard** - Prehľad domén a SSL
- **Domény** - Zoznam a správa domén
- **SSL** - Generovanie certifikátov
- **Profil** - Nastavenia 2FA, zmena hesla

---

## 9. Docker deployment

### 9.1 Produčný server

`ash
# Build a spustenie
docker-compose up -d --build

# Zastavenie
docker-compose down

# Logy
docker-compose logs -f

# Reštart služby
docker-compose restart backend
`

### 9.2 Nginx reverse proxy

Vytvor 
ginx.conf:

`
ginx
server {
    listen 80;
    server_name api.mojadomena.sk;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP ;
    }
}

server {
    listen 80;
    server_name mojadomena.sk;

    location / {
        proxy_pass http://localhost:3000;
    }
    
    # Pre SSL certbot
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
`

### 9.3 SSL s Nginx

`ash
# Získanie certifikátu
certbot --nginx -d mojadomena.sk -d api.mojadomena.sk

# Alebo pre existing Nginx config
certbot --nginx --deploy-hook \"systemctl reload nginx\"
`

---

## 10. Troubleshooting

### 10.1 Časté problémy

#### \"Connection refused\" pri Websupport API
- Skontroluj API kľúče v .env
- Overiť prístup k rest.websupport.sk

#### \"Database connection failed\"
- Skontroluj DATABASE_URL
- Overiť bežiacu PostgreSQL databázu

#### \"Port already in use\"
`ash
# Zisti proces na porte
netstat -ano | findstr :8000
# Ukonči proces
taskkill /PID <PID> /F
`

#### Docker kontajner neštartuje
`ash
# Logy
docker-compose logs backend
# Re-build
docker-compose build --no-cache
`

### 10.2 Reset databázy

`ash
# Zastav kontajnery
docker-compose down

# Zmaž volumes
docker-compose down -v

# Znova spusti
docker-compose up -d
`

### 10.3 Logovanie

`ash
# Všetky logy
docker-compose logs -f

# Len backend
docker-compose logs -f backend

# Len frontend
docker-compose logs -f frontend
`

---

## API Cheat Sheet

| Metóda | Endpoint | Popis |
|--------|----------|-------|
| GET | /health | Zdravie systému |
| GET | /api/domains | Zoznam domén |
| POST | /api/domains | Vytvor doménu |
| POST | /api/ssl/generate | Generuj SSL |
| POST | /api/users/register | Registrácia |
| POST | /api/users/login | Prihlásenie |
| GET | /api/users/me | Môj profil |
| POST | /api/users/2fa/setup | Nastav 2FA |
| POST | /api/users/2fa/verify | Overi 2FA |

---

## Kontakt a podpora

Pre technickú podporu kontaktuj: support@mojadomena.sk
