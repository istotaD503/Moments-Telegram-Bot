#!/usr/bin/env python3
"""
Telegram Bot Skeleton
A basic Telegram bot with webhook support for Render deployment.
"""

import logging
import os
import sys
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Import our modular components
from config.settings import settings
from handlers.commands import CommandHandlers

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for webhook
flask_app = Flask(__name__)

# Global application instance
telegram_app = None

def create_telegram_app(webhook_mode=False):
    """Create and configure the Telegram application."""
    global telegram_app
    
    # Always create a new app based on the mode
    if webhook_mode:
        # For webhook mode, don't create an updater or job queue
        telegram_app = Application.builder().token(settings.BOT_TOKEN).updater(None).job_queue(None).build()
    else:
        # For polling mode, use default setup with updater and job queue
        telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    # Add basic command handlers
    telegram_app.add_handler(CommandHandler("start", CommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("help", CommandHandlers.help_command))

    # Add handler for unknown commands
    telegram_app.add_handler(MessageHandler(filters.COMMAND, CommandHandlers.unknown_command))

    # Add error handler
    telegram_app.add_error_handler(CommandHandlers.error_handler)

    return telegram_app

@flask_app.route('/')
def index():
    return "Telegram Bot is running! 🤖"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates."""
    import asyncio
    import threading
    
    global telegram_app
    
    # Make sure we have an initialized app
    if not telegram_app:
        telegram_app = create_telegram_app(webhook_mode=True)
        # Initialize synchronously in this context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.initialize())
        loop.close()
    
    # Get the update from Telegram
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    
    # Process the update in a separate thread to avoid event loop conflicts
    def process_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(telegram_app.process_update(update))
        finally:
            loop.close()
    
    thread = threading.Thread(target=process_in_thread)
    thread.start()
    thread.join()  # Wait for completion
    
    return "OK"

def main() -> None:
    """Start the bot in the appropriate mode."""
    
    # Validate configuration
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print(f"🤖 Starting Telegram Bot...")

    # Check if we're running on Render (production)
    if os.getenv('RENDER'):
        print("🌐 Running in webhook mode (Render)")
        # Don't pre-initialize here - let webhook handler do it when needed
        global telegram_app
        telegram_app = None
        
        # Get port from environment
        port = int(os.environ.get('PORT', 10000))
        
        print(f"🚀 Starting Flask webhook server on port {port}")
        print("✅ Webhook handler will initialize Telegram app on first request")
        # Run Flask app
        flask_app.run(host='0.0.0.0', port=port)
    else:
        print("🏠 Running in polling mode (local)")
        # Create the Application for local development with updater
        telegram_app = create_telegram_app(webhook_mode=False)
        
        print("✅ Bot handlers registered:")
        print("   🏠 /start - Welcome message")
        print("   ℹ️  /help - Show help message")
        
        print("🚀 Telegram Bot is running! Press Ctrl+C to stop.")
        
        try:
            telegram_app.run_polling(poll_interval=1)
        except KeyboardInterrupt:
            print("\n👋 Telegram Bot stopped!")

if __name__ == '__main__':
    main()