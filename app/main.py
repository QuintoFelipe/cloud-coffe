import logging
import os

# ⚠️ Escribir el archivo de credenciales si está en el entorno quinto
if "GCP_SA_JSON" in os.environ:
    with open("/tmp/sa.json", "w") as f:
        f.write(os.environ["GCP_SA_JSON"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/sa.json"

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers.webhook import router as webhook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Include API routes
app.include_router(webhook_router)
