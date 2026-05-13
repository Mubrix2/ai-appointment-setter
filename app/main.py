# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, health
from app.config import APP_ENV
from app.core.agent import get_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting AI Appointment Setter | env={APP_ENV}")
    get_agent()
    logger.info("Appointment agent ready.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Appointment Setter",
        description=(
            "Conversational AI agent that qualifies visitors "
            "and books appointments via Cal.com automatically."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api/v1")

    return app


app = create_app()