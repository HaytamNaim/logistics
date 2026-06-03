# Logistics and Delivery Management System

Implementation of the [TECHNICAL_BLUEPRINT.md](./TECHNICAL_BLUEPRINT.md): order lifecycle, delivery tracking, driver assignment, routes, analytics, RBAC, and audit logs.

## Tech stack

- **Backend:** Python 3.12, FastAPI
- **Database:** PostgreSQL 15
- **Cache / real-time:** Redis (optional for current features)
- **Auth:** JWT (access + refresh), RBAC (ADMIN, FLEET_MANAGER, DRIVER)
- **Frontend:** React 18, TypeScript, Vite — implements [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) (“Logistics in Harmony” biophilic UI)

## Quick start

### 1. Start PostgreSQL (and Redis) with Docker

```bash
docker-compose up -d
```

### 2. Create venv and install deps

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults point to local PostgreSQL and Redis)
```

### 4. Run the API

From the project root (`/home/haytam/Desktop/logistics`):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: http://localhost:8000  
- OpenAPI docs: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  

### 5. Run the frontend (optional)

From the project root:

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:3000  
- Uses DESIGN_SYSTEM.md tokens (Stone Paper, Sage, Sand, organic status colors). Proxy for API: `/api` → http://127.0.0.1:8000  

### 6. Default admin user (created on first startup)

- **Email:** `admin@logistics.local`  
- **Password:** `admin123`  

Use `POST /api/v1/auth/login` with `{"email":"admin@logistics.local","password":"admin123"}` to get an access token, or in Swagger use **Authorize** and the `/api/v1/auth/token` flow with username=`admin@logistics.local`, password=`admin123`.

## API overview

| Area | Endpoints |
|------|-----------|
| **Auth** | `POST /api/v1/auth/login`, `POST /api/v1/auth/token`, `POST /api/v1/auth/refresh` |
| **Me** | `GET /api/v1/me` |
| **Audit** | `GET /api/v1/audit-logs` (Admin) |
| **Zones** | `GET/POST /api/v1/zones`, `GET/PATCH /api/v1/zones/{id}` |
| **Addresses** | `GET/POST /api/v1/delivery-addresses`, `GET/PATCH /api/v1/delivery-addresses/{id}` |
| **Orders** | `GET/POST /api/v1/orders`, `GET/PATCH/DELETE /api/v1/orders/{id}`, `POST /api/v1/orders/{id}/transition` |
| **Deliveries** | `GET/POST /api/v1/deliveries`, `GET/PATCH /api/v1/deliveries/{id}`, `POST .../status`, `POST .../assign`, `POST /api/v1/deliveries/assign-auto`, `POST .../location`, `WS .../track` |
| **Drivers** | `GET /api/v1/drivers`, `GET /api/v1/drivers/available`, `GET/PATCH /api/v1/drivers/{id}`, `POST .../availability` |
| **Routes** | `GET/POST /api/v1/routes`, `GET/PATCH /api/v1/routes/{id}`, `POST .../optimize`, `POST .../publish` |
| **Analytics** | `GET /api/v1/analytics/kpis`, `GET /api/v1/analytics/deliveries`, `GET /api/v1/analytics/drivers` |

## Run without Docker

If PostgreSQL is installed locally:

- Create a database: `createdb logistics`
- Set `DATABASE_URL=postgresql://USER:PASSWORD@localhost:5433/logistics` in `.env` (project uses host port 5433 to avoid conflict with local PostgreSQL on 5432)

Redis is optional for the current implementation; auto-assignment and drivers work without it.

## Seed data

On first startup, the app creates tables and seeds:

- Roles: `ADMIN`, `FLEET_MANAGER`, `DRIVER`
- User `admin@logistics.local` with role `ADMIN`

To re-run only the seed (e.g. after resetting the DB):

```bash
python -m app.db_seed
```

## Project layout

```
app/
  main.py           # FastAPI app, CORS, router includes
  config.py         # Settings from env
  database.py       # SQLAlchemy engine, session, Base
  db_seed.py        # Seed roles + admin
  models/           # SQLAlchemy models (ER from blueprint)
  schemas/          # Pydantic request/response
  core/             # security (JWT, bcrypt), rbac, audit
  api/v1/           # auth, me, audit, zones, addresses, orders, deliveries, drivers, routes, analytics
  services/         # order_state, delivery_state, auto_assign
```
