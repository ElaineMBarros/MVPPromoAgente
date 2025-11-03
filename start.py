#!/usr/bin/env python3
"""Script de inicialização para Railway"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando servidor em {host}:{port}")
    
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        log_level="info"
    )
