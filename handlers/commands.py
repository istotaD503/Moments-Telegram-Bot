"""
Basic command handlers for the Moments Bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.storage import storage

logger = logging.getLogger(__name__)

class BasicCommandHandlers:
    """Basic command handlers for common bot functionality"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user_first_name = update.effective_user.first_name
        user_id = update.effective_user.id
        
        # Get user stats for personalized welcome
        stats = storage.get_user_stats(user_id)
        
        if stats.total_moments == 0:
            # New user welcome
            welcome_message = (
                f"¡Hola {user_first_name}! 👋 Welcome to your Spanish Moments Bot!\n\n"
                f"🌟 **What is this bot about?**\n"
                f"I help you practice Spanish by capturing your daily story-worthy moments. "
                f"Here's how it works:\n\n"
                f"1️⃣ You write about a moment from your day in English\n"
                f"2️⃣ You try to translate it to Spanish\n"
                f"3️⃣ I help you improve your Spanish (coming soon!)\n"
                f"4️⃣ Your moments are saved for review and progress tracking\n\n"
                f"📝 **Ready to start?** Use /moment to capture your first story-worthy moment!\n\n"
                f"🤔 **Need help?** Use /help to see all available commands."
            )
        else:
            # Returning user welcome
            welcome_message = (
                f"¡Bienvenido de nuevo, {user_first_name}! 🎉\n\n"
                f"📊 **Your Progress:**\n"
                f"• {stats.total_moments} moments captured\n"
                f"• {stats.current_streak} day streak\n"
                f"• {stats.vocabulary_count} vocabulary words learned\n\n"
                f"📝 Ready to capture another moment? Use /moment to continue your Spanish journey!"
            )
        
        await update.message.reply_text(welcome_message)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a help message when the command /help is issued."""
        help_message = (
            "🤖 **Spanish Moments Bot - Help**\n\n"
            "**📝 Capturing Moments:**\n"
            "• `/moment` - Start capturing a new story-worthy moment\n"
            "• `/cancel` - Cancel current moment capture\n\n"
            "**📚 Reviewing Your Progress:**\n"
            "• `/recent` - View your recent moments (last 7 days)\n"
            "• `/stats` - See your learning statistics\n"
            "• `/search [term]` - Search through your moments\n"
            "• `/export` - Download all your moments as a text file\n\n"
            "**ℹ️ Information:**\n"
            "• `/help` - Show this help message\n"
            "• `/start` - Welcome message and overview\n\n"
            "**💡 Tips:**\n"
            "• Try to capture 1-3 moments daily for consistent practice\n"
            "• Don't worry about perfect Spanish - focus on trying!\n"
            "• Review your old moments to see your progress\n"
            "• Story-worthy moments can be small but meaningful\n\n"
            "**🔮 Coming Soon:**\n"
            "• AI-powered Spanish corrections and explanations\n"
            "• Daily reminder notifications\n"
            "• Vocabulary review sessions\n"
            "• Voice message support\n\n"
            "¡Vamos a practicar español! Let's practice Spanish! 🇪🇸✨"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    @staticmethod
    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands"""
        await update.message.reply_text(
            "🤔 I don't recognize that command. Use /help to see all available commands!"
        )
    
    @staticmethod
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages outside of conversations"""
        message_text = update.message.text.lower()
        user_name = update.effective_user.first_name
        
        # Handle quick action buttons from conversation end
        if "capture another moment" in message_text or "📝" in message_text:
            await update.message.reply_text(
                "Great! Use /moment to start capturing a new moment! ✨"
            )
        elif "view my stats" in message_text or "📊" in message_text:
            # Import here to avoid circular imports
            from handlers.conversation import MomentCommandHandlers
            await MomentCommandHandlers.show_stats(update, context)
        elif "see recent moments" in message_text or "🔍" in message_text:
            from handlers.conversation import MomentCommandHandlers
            await MomentCommandHandlers.show_recent_moments(update, context)
        elif "hello" in message_text or "hi" in message_text:
            await update.message.reply_text(
                f"¡Hola {user_name}! 👋 Ready to capture a Spanish moment? Use /moment to get started!"
            )
        elif "help" in message_text:
            await BasicCommandHandlers.help_command(update, context)
        else:
            # General response for unrecognized text
            responses = [
                f"¡Hola {user_name}! 😊 Use /moment to capture a story-worthy moment in Spanish!",
                f"Hi there! 🌟 Ready to practice Spanish? Try /moment to get started!",
                f"¡Qué tal, {user_name}! Use /help if you need guidance on available commands.",
            ]
            
            import random
            response = random.choice(responses)
            await update.message.reply_text(response)
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a user-friendly message."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😅 Oops! Something went wrong. Please try again or use /help if you need assistance."
            )