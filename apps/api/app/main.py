from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import engine, Base, get_db
import app.models  # asegura registro de modelos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # En desarrollo, aseguramos la creacion de tablas si el motor esta disponible
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        # Si la base de datos aun no esta arriba en local, no bloqueamos el arranque
        print(f"Aviso al inicializar tablas: {exc}")
    yield
    # Limpieza al apagar
    await engine.dispose()


app = FastAPI(
    title="Vocatus & Animus API",
    description="Backend Core para suite de eventos sociales (RSVP y Boveda Colaborativa)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuracion CORS
origins = [
    settings.FRONTEND_URL,
    settings.ADMIN_URL,
    "http://localhost:3000",
    "http://localhost:4321",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4321",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    return {
        "service": "Vocatus & Animus API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "environment": settings.ENV,
    }


# Inclusion de Routers
from app.routers import auth, events, rsvp, vault, admin

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(rsvp.router)
app.include_router(vault.router)
app.include_router(admin.router)

