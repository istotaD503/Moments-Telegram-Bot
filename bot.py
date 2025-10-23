#!/usr/bin/env python3
"""
Spanish Moments Telegram Bot
A language learning bot that helps users practice Spanish by capturing daily story-worthy moments.

Concept inspired by Matthew Dicks' "Homework for Life" combined with active language learning.
"""

import logging
import sys
from typing import Final

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

def main() -> None:
    """Start the Spanish Moments Bot."""
    
    # Validate configuration
    if not settings.validate():
        print("Please create a .env file with your bot token:")
        print("BOT_TOKEN=your_telegram_bot_token_here")
        sys.exit(1)

    print(f"🤖 Starting Spanish Moments Bot {settings.BOT_USERNAME}...")
    print(f"📁 Data directory: {settings.DATA_DIR}")

    # Create the Application
    app = Application.builder().token(settings.BOT_TOKEN).build()

    # Add conversation handler for moment capture (highest priority)
    moment_conversation = MomentConversationHandler.get_conversation_handler()
    app.add_handler(moment_conversation)

    # Add basic command handlers
    app.add_handler(CommandHandler("start", BasicCommandHandlers.start_command))
    app.add_handler(CommandHandler("help", BasicCommandHandlers.help_command))
    
    # Add moment management command handlers
    app.add_handler(CommandHandler("recent", MomentCommandHandlers.show_recent_moments))
    app.add_handler(CommandHandler("stats", MomentCommandHandlers.show_stats))
    app.add_handler(CommandHandler("search", MomentCommandHandlers.search_moments))
    app.add_handler(CommandHandler("export", MomentCommandHandlers.export_moments))

    # Add handler for unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, BasicCommandHandlers.unknown_command))

    # Add message handler for non-command messages (lowest priority)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, BasicCommandHandlers.handle_text_message))

    # Add error handler
    app.add_error_handler(BasicCommandHandlers.error_handler)

    # Print startup information
    print("✅ Bot handlers registered:")
    print("   📝 /moment - Start moment capture conversation")
    print("   📚 /recent - View recent moments")
    print("   📊 /stats - Show learning statistics")
    print("   🔍 /search - Search through moments")
    print("   📄 /export - Export moments to file")
    print("   ℹ️  /help - Show help message")
    print("   🏠 /start - Welcome message")
    
    # Run the bot until the user presses Ctrl-C
    print("🚀 Spanish Moments Bot is running! Press Ctrl+C to stop.")
    print("💡 Start a conversation with your bot and use /moment to capture your first story-worthy moment!")
    
    try:
        app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Spanish Moments Bot stopped. ¡Hasta luego!")

if __name__ == '__main__':
    main()