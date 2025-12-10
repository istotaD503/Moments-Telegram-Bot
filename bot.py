#!/usr/bin/env python3
"""
Telegram Bot Skeleton
"""

import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.settings import settings
from handlers.commands import CommandHandlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print("🤖 Starting Bot...")
    telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", CommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("help", CommandHandlers.help_command))
    telegram_app.add_handler(MessageHandler(filters.COMMAND, CommandHandlers.unknown_command))
    telegram_app.add_error_handler(CommandHandlers.error_handler)
    print("🚀 Bot running. Press Ctrl+C to stop.")
    
    try:
        telegram_app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

if __name__ == '__main__':
    main()