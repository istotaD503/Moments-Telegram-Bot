"""
Basic command handlers for the Telegram Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.assets import load_about_message
from .shared import story_db

logger = logging.getLogger(__name__)


class BasicCommandHandlers:
    """Basic command handlers for start, about, help, and error handling"""
    
    # Reference to shared database instance
    story_db = story_db
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a minimal welcome message when the command /start is issued."""
        user_first_name = update.effective_user.first_name
        
        welcome_message = (
            f"Hello {user_first_name}! 👋\n\n"
            "Welcome to <b>Moments Bot</b> - your daily companion for capturing life's storyworthy moments!\n\n"
        )
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("📖 Learn More", callback_data="quick:about")],
            [InlineKeyboardButton("📝 Record a Story", callback_data="quick:story")],
            [InlineKeyboardButton("⏰ Set Daily Reminder", callback_data="quick:reminder")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, parse_mode='HTML', reply_markup=reply_markup)
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send detailed information about the bot and Homework for Life."""
        user_first_name = update.effective_user.first_name
        
        about_message = load_about_message(user_first_name)

        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Record a Story", callback_data="quick:story")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="quick:help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(about_message, parse_mode='HTML', reply_markup=reply_markup)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "/start — welcome message\n"
            "/help — this list\n"
            "/story — record today's moment\n"
            "/report — AI story report\n"
            "/reminders — manage daily reminders\n"
            "/mystories — your stats + export\n"
            "/export — download all stories as a file\n"
            "/about — what is Homework for Life",
        )
    
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
    
    @staticmethod
    async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle 'about' quick action callback."""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        about_message = load_about_message(user.first_name)
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Record a Story", callback_data="quick:story")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="quick:help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(about_message, parse_mode='HTML', reply_markup=reply_markup)
        return ConversationHandler.END
    
    @staticmethod
    async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "/start — welcome message\n"
            "/help — this list\n"
            "/story — record today's moment\n"
            "/report — AI story report\n"
            "/reminders — manage daily reminders\n"
            "/mystories — your stats + export\n"
            "/export — download all stories as a file\n"
            "/about — what is Homework for Life",
        )
        return ConversationHandler.END
