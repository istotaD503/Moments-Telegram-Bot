"""
Feedback-related command handlers for the Telegram Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from .shared import story_db

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_FEEDBACK = 10


class FeedbackCommandHandlers:
    """Handlers for user feedback collection"""
    
    # Reference to shared database instance
    story_db = story_db
    
    @staticmethod
    async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Start the feedback conversation.
        Prompts user to share their feedback about the bot.
        """
        user_first_name = update.effective_user.first_name
        
        prompt_message = (
            f"Hey {user_first_name}! 👋\n\n"
            "I'd love to hear your thoughts! 💭\n\n"
            "Your feedback helps make this bot better for everyone. "
            "Whether it's a bug report, feature request, or just a comment "
            "about your experience — I'm all ears!\n\n"
            "What's on your mind? 📝"
        )
        
        # Add cancel button
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel:feedback")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(prompt_message, parse_mode='HTML', reply_markup=reply_markup)
        
        # Set the conversation state
        return WAITING_FOR_FEEDBACK
    
    @staticmethod
    async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Receive and save the user's feedback.
        """
        user = update.effective_user
        feedback_text = update.message.text
        
        # Save to database
        feedback_id = FeedbackCommandHandlers.story_db.save_feedback(
            user_id=user.id,
            feedback_text=feedback_text,
            username=user.username,
            first_name=user.first_name
        )
        
        logger.info(f"Feedback received from {user.id} (@{user.username}): {feedback_text[:50]}...")
        
        # Thank you message
        thank_you_message = (
            "🙏 <b>Thank you so much!</b>\n\n"
            "Your feedback has been recorded and will help improve the bot. "
            "I really appreciate you taking the time to share your thoughts!\n\n"
            "Keep capturing those moments! ✨"
        )
        
        await update.message.reply_text(thank_you_message, parse_mode='HTML')
        
        # End conversation
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the feedback collection conversation (via command)."""
        await update.message.reply_text(
            "Feedback cancelled. No worries! You can share feedback anytime with /feedback 💙",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the feedback collection conversation (via button)."""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "Feedback cancelled. No worries! You can share feedback anytime with /feedback 💙"
        )
        return ConversationHandler.END
