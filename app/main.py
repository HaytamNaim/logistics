"""Logistics and Delivery Management System — FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.database import engine, Base
from app.core.limiter import limiter
from app.api.v1 import auth, me, audit, zones, addresses, orders, deliveries, drivers, routes, analytics

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/docs", redoc_url="/redoc")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(me.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(zones.router, prefix="/api/v1")
app.include_router(addresses.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(deliveries.router, prefix="/api/v1")
app.include_router(drivers.router, prefix="/api/v1")
app.include_router(routes.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": settings.app_name, "docs": "/docs", "api": "/api/v1"}


@app.on_event("startup")
def startup():
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    from app.db_seed import seed
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
