"""
FastAPI app serving the Telegram Mini App for reminder time capture.
"""
import json
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

static_dir = Path(__file__).parent / "static"

webapp_app = FastAPI(title="Moments Bot WebApp")


@webapp_app.get("/")
async def health_check():
    print("❤️  Health check hit", flush=True)
    return {"status": "ok"}


@webapp_app.get("/webapp/reminder")
async def serve_reminder_page():
    print("📱 Mini App page requested", flush=True)
    return FileResponse(
        static_dir / "reminder.html",
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


@webapp_app.post("/api/test-set-reminder")
async def test_set_reminder(body: dict):
    """
    Fallback endpoint for browser testing outside Telegram.
    In production, sendData() is used instead.
    """
    from handlers.shared import story_db

    try:
        time_str = body.get("time")
        timezone_str = body.get("timezone")
        if not time_str or not timezone_str:
            return {"ok": False, "error": "Missing time or timezone"}

        logger.info(f"Test endpoint: time={time_str}, tz={timezone_str}")
        return {"ok": True, "message": "Received (test mode — not saved to DB)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
