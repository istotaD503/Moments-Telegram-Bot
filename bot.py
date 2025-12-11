#!/usr/bin/env python3
"""
Telegram Bot Skeleton
"""

import logging
import sys
import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from config.settings import settings
from handlers.commands import CommandHandlers, WAITING_FOR_STORY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return {'status': 'ok', 'message': 'Telegram bot is running'}, 200

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

def run_flask():
    """Run Flask server in a separate thread"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot():
    """Run the Telegram bot with polling"""
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
    telegram_app.add_handler(CommandHandler("help", CommandHandlers.help_command))
    telegram_app.add_handler(MessageHandler(filters.COMMAND, CommandHandlers.unknown_command))
    # Removed default message handler to avoid conflicts with conversation handlers
    telegram_app.add_error_handler(CommandHandlers.error_handler)
    print("🚀 Bot running. Press Ctrl+C to stop.")
    
    try:
        telegram_app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

def main():
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    # Start Flask server in a background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"🌐 Web server started on port {os.environ.get('PORT', 10000)}")

    # Run the bot
    run_bot()

if __name__ == '__main__':
    main()