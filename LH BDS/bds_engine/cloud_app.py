"""Cloud Run webhook entrypoint for the Telegram BĐS bot."""
from __future__ import annotations

import logging
import os

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from ai_client import NineRouterClient
from bot import cmd_start, cmd_gia, on_callback
from config import load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bds-bot-cloud")

settings = load_settings()
ai = NineRouterClient(
    api_key=settings.nineouter_api_key,
    base_url=settings.nineouter_base_url,
    model=settings.nineouter_model,
    timeout=settings.ai_timeout,
)

application = Application.builder().token(settings.telegram_token).updater(None).build()
application.bot_data["settings"] = settings
application.bot_data["ai"] = ai
application.add_handler(CommandHandler("start", cmd_start))
application.add_handler(CommandHandler("help", cmd_start))
application.add_handler(CommandHandler("gia", cmd_gia))
application.add_handler(CallbackQueryHandler(on_callback))

app = Flask(__name__)
_started = False


async def _ensure_started() -> None:
    global _started
    if not _started:
        await application.initialize()
        await application.start()
        _started = True
        logger.info("Telegram application initialized for webhook")


@app.get("/")
def health():
    return {"ok": True, "service": "bds-telegram-bot"}


@app.post("/telegram-webhook")
async def telegram_webhook():
    await _ensure_started()
    data = request.get_json(force=True, silent=True) or {}
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}


@app.get("/set-webhook")
async def set_webhook():
    await _ensure_started()
    base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    if not base_url:
        return {"ok": False, "error": "PUBLIC_BASE_URL is not set"}, 500
    webhook_url = f"{base_url}/telegram-webhook"
    ok = await application.bot.set_webhook(webhook_url)
    return {"ok": bool(ok), "webhook_url": webhook_url}


@app.get("/delete-webhook")
async def delete_webhook():
    await _ensure_started()
    ok = await application.bot.delete_webhook(drop_pending_updates=False)
    return {"ok": bool(ok)}
