import asyncio
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import router as api_router
from src.core.agent_logic import promo_agente
from src.core.config import log_configs

def create_app() -> FastAPI:
    log_configs()
    
    app = FastAPI(
        title="PromoAgente Local", 
        version="2.0.0",
        description="Sistema de promoções B2B com arquitetura modular."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        await promo_agente.initialize()
        # asyncio.create_task(promo_agente.start_periodic_extraction())

    # Health check para Railway
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "PromoAgente"}

    # Incluir rotas da API com prefixo /api
    app.include_router(api_router, prefix="/api")

    # Servir frontend buildado (para produção)
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app

app = create_app()
