#!/usr/bin/env python3
"""
Spanish Moments Telegram Bot
A language learning bot that helps users practice Spanish by capturing daily story-worthy moments.

Concept inspired by Matthew Dicks' "Homework for Life" combined with active language practice.
"""

import logging
import os
import sys
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Import our modular components
from config.settings import settings
from handlers.commands import BasicCommandHandlers
from handlers.conversation import MomentConversationHandler, MomentCommandHandlers

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
        # For webhook mode, don't create an updater
        telegram_app = Application.builder().token(settings.BOT_TOKEN).updater(None).build()
    else:
        # For polling mode, use default setup with updater
        telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    # Add conversation handler for moment capture (highest priority)
    moment_conversation = MomentConversationHandler.get_conversation_handler()
    telegram_app.add_handler(moment_conversation)

    # Add basic command handlers
    telegram_app.add_handler(CommandHandler("start", BasicCommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("help", BasicCommandHandlers.help_command))
    
    # Add moment management command handlers
    telegram_app.add_handler(CommandHandler("recent", MomentCommandHandlers.show_recent_moments))
    telegram_app.add_handler(CommandHandler("stats", MomentCommandHandlers.show_stats))
    telegram_app.add_handler(CommandHandler("search", MomentCommandHandlers.search_moments))
    telegram_app.add_handler(CommandHandler("export", MomentCommandHandlers.export_moments))

    # Add handler for unknown commands
    telegram_app.add_handler(MessageHandler(filters.COMMAND, BasicCommandHandlers.unknown_command))

    # Add message handler for non-command messages (lowest priority)
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, BasicCommandHandlers.handle_text_message))

    # Add error handler
    telegram_app.add_error_handler(BasicCommandHandlers.error_handler)

    return telegram_app

@flask_app.route('/')
def index():
    return "Spanish Moments Bot is running! 🤖"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates."""
    import asyncio
    
    async def process_update():
        telegram_app = create_telegram_app(webhook_mode=True)
        
        # Get the update from Telegram
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        
        # Process the update
        await telegram_app.process_update(update)
    
    # Run the async function
    asyncio.run(process_update())
    
    return "OK"

def main() -> None:
    """Start the bot in the appropriate mode."""
    
    # Validate configuration
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print(f"🤖 Starting Spanish Moments Bot...")
    print(f"📁 Data directory: {settings.DATA_DIR}")

    # Check if we're running on Render (production)
    if os.getenv('RENDER'):
        print("🌐 Running in webhook mode (Render)")
        # Initialize the telegram app for webhook mode
        create_telegram_app(webhook_mode=True)
        
        # Get port from environment
        port = int(os.environ.get('PORT', 10000))
        
        # Run Flask app
        flask_app.run(host='0.0.0.0', port=port)
    else:
        print("🏠 Running in polling mode (local)")
        # Create the Application for local development with updater
        telegram_app = create_telegram_app(webhook_mode=False)
        
        print("✅ Bot handlers registered:")
        print("   📝 /moment - Start moment capture conversation")
        print("   📚 /recent - View recent moments")
        print("   📊 /stats - Show learning statistics")
        print("   🔍 /search - Search through moments")
        print("   📄 /export - Export moments to file")
        print("   ℹ️  /help - Show help message")
        print("   🏠 /start - Welcome message")
        
        print("🚀 Spanish Moments Bot is running! Press Ctrl+C to stop.")
        print("💡 Start a conversation with your bot and use /moment to capture your first story-worthy moment!")
        
        try:
            telegram_app.run_polling(poll_interval=1)
        except KeyboardInterrupt:
            print("\n👋 Spanish Moments Bot stopped. ¡Hasta luego!")

if __name__ == '__main__':
    main()