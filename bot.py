#!/usr/bin/env python3
"""
Telegram Bot for capturing daily storyworthy moments
"""

import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from config.settings import settings
from handlers.commands import CommandHandlers, WAITING_FOR_STORY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Main function to run the Telegram bot"""
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print("🤖 Starting Bot...")
    telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    # Log all incoming updates
    async def log_update(update, context):
        logging.info(f"Received update: {update.to_dict()}")
    
    # Add logger as the first handler to catch everything
    telegram_app.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    # Story command with conversation handler
    story_conversation = ConversationHandler(
        entry_points=[CommandHandler("story", CommandHandlers.story_command)],
        states={
            WAITING_FOR_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_story)
            ]
        },
        fallbacks=[CommandHandler("cancel", CommandHandlers.cancel_story)]
    )
    telegram_app.add_handler(story_conversation)

    # Other commands
    telegram_app.add_handler(CommandHandler("start", CommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("about", CommandHandlers.about_command))
    telegram_app.add_handler(CommandHandler("help", CommandHandlers.help_command))
    telegram_app.add_handler(CommandHandler("mystories", CommandHandlers.mystories_command))
    telegram_app.add_handler(CommandHandler("export", CommandHandlers.export_command))
    telegram_app.add_handler(MessageHandler(filters.COMMAND, CommandHandlers.unknown_command))
    telegram_app.add_error_handler(CommandHandlers.error_handler)
    
    print("🚀 Bot running. Press Ctrl+C to stop.")
    
    try:
        telegram_app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

if __name__ == '__main__':
    main()