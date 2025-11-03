import uvicorn
from src.app import app
from src.core.config import HOST, PORT, DEBUG, logger

if __name__ == "__main__":
    logger.info(f"Iniciando servidor em http://{HOST}:{PORT}")
    uvicorn.run(
        "src.app:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )