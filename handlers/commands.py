"""
Basic command handlers for the Telegram Bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Basic command handlers for common bot functionality"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user_first_name = update.effective_user.first_name
        
        welcome_message = (
            f"Hello {user_first_name}! 👋 Welcome to this Telegram Bot!\n\n"
            f"This is a basic bot skeleton ready for customization.\n\n"
            f"Use /help to see available commands."
        )
        
        await update.message.reply_text(welcome_message)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a help message when the command /help is issued."""
        help_message = (
            "🤖 **Bot Help**\n\n"
            "**Available Commands:**\n"
            "• `/start` - Welcome message\n"
            "• `/help` - Show this help message\n\n"
            "This is a basic Telegram bot skeleton. "
            "Add your custom functionality here!"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    @staticmethod
    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands"""
        await update.message.reply_text(
            "🤔 I don't recognize that command. Use /help to see all available commands!"
        )
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a user-friendly message."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😅 Oops! Something went wrong. Please try again or use /help if you need assistance."
            )