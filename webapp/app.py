"""
FastAPI app serving the Telegram Mini App for reminder time capture.
"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

static_dir = Path(__file__).parent / "static"

webapp_app = FastAPI(title="Moments Bot WebApp")


@webapp_app.get("/")
async def health_check():
    return {"status": "ok"}


@webapp_app.get("/webapp/reminder")
async def serve_reminder_page():
    return FileResponse(
        static_dir / "reminder.html",
        media_type="text/html",
    )
