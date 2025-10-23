from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.logger_config import setup_logger
from app.services.hashing_service import hashing_service
from app.core.config import settings

logger = setup_logger('main_app', log_file=settings.LOG_FILE_API)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service is starting up.")
    logger.info(f"Initial nodes: {hashing_service.get_all_nodes()}")
    yield
    logger.info("Service is shutting down.")

app = FastAPI(
    title="Consistent Hashing Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redirects the root URL to the /docs endpoint.
    """
    return RedirectResponse(url="/docs")

app.include_router(api_router, prefix="/api")
