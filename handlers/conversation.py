"""
Conversation handlers for the Moments Bot
Handles the multi-step conversation flow for capturing and processing moments.
"""
import logging
from typing import Dict, Any

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    filters
)

from models.moment import Moment
from services.storage import storage
from config.settings import settings

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_MOMENT = 1
WAITING_FOR_SPANISH = 2
REVIEWING_FEEDBACK = 3
MOMENT_SAVED = 4

class MomentConversationHandler:
    """Handles the conversation flow for capturing moments"""
    
    @staticmethod
    async def start_moment_capture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the moment capture conversation"""
        user = update.effective_user
        
        # Check if user has reached daily limit
        from datetime import date
        today_moments = storage.get_moments_by_date(user.id, date.today())
        
        if len(today_moments) >= settings.MAX_MOMENTS_PER_DAY:
            await update.message.reply_text(
                f"🎯 You've already captured {len(today_moments)} moments today! "
                f"That's fantastic dedication. Come back tomorrow for more practice! 🌟\n\n"
                f"Or use /recent to review your recent moments."
            )
            return ConversationHandler.END
        
        # Create keyboard for moment prompts
        prompt_options = [
            ["🎭 Tell me about an interesting moment"],
            ["🌟 Share something that made you smile"],
            ["🤔 Describe something you learned today"],
            ["💭 Write about any moment you choose"]
        ]
        keyboard = ReplyKeyboardMarkup(prompt_options, one_time_keyboard=True, resize_keyboard=True)
        
        welcome_message = (
            f"✨ Hello {user.first_name}! Ready to capture a story-worthy moment?\n\n"
            f"📝 Today you've captured {len(today_moments)}/{settings.MAX_MOMENTS_PER_DAY} moments.\n\n"
            f"Choose a prompt below or just start writing about any moment from your day in English:"
        )
        
        await update.message.reply_text(welcome_message, reply_markup=keyboard)
        
        # Store user info in context for later use
        context.user_data['user_id'] = user.id
        context.user_data['user_name'] = user.first_name
        
        return WAITING_FOR_MOMENT
    
    @staticmethod
    async def receive_english_moment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the English moment text"""
        english_text = update.message.text.strip()
        user_id = context.user_data.get('user_id')
        
        # Validate input
        if len(english_text) < 10:
            await update.message.reply_text(
                "🤔 That seems a bit short for a story-worthy moment. "
                "Could you share a bit more detail? I'd love to hear more about it!"
            )
            return WAITING_FOR_MOMENT
        
        if len(english_text) > 500:
            await update.message.reply_text(
                "📝 That's a wonderful, detailed moment! However, let's keep it under 500 characters "
                "for better Spanish practice. Could you share a more concise version?"
            )
            return WAITING_FOR_MOMENT
        
        # Create and store the moment
        moment = Moment.create_new(user_id, english_text)
        success = storage.save_moment(moment)
        
        if not success:
            await update.message.reply_text(
                "😅 Oops! I had trouble saving your moment. Please try again."
            )
            return ConversationHandler.END
        
        # Store moment ID in context
        context.user_data['current_moment_id'] = moment.id
        
        # Ask for Spanish translation
        spanish_prompt = (
            "🇪🇸 Perfect! Now try writing that same moment in Spanish.\n\n"
            "💡 **Tips:**\n"
            "• Don't worry about perfection - just try your best!\n"
            "• Use simple sentences if needed\n"
            "• I'll help you improve it afterwards\n\n"
            "**Your English moment:**\n"
            f"_{english_text}_\n\n"
            "Now write it in Spanish:"
        )
        
        await update.message.reply_text(spanish_prompt, reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_SPANISH
    
    @staticmethod
    async def receive_spanish_attempt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the Spanish translation attempt"""
        spanish_text = update.message.text.strip()
        user_id = context.user_data.get('user_id')
        moment_id = context.user_data.get('current_moment_id')
        
        if not moment_id:
            await update.message.reply_text(
                "😅 I seem to have lost track of your moment. Let's start over with /moment"
            )
            return ConversationHandler.END
        
        # Load the moment and add Spanish attempt
        moment = storage.get_moment_by_id(user_id, moment_id)
        if not moment:
            await update.message.reply_text(
                "😅 I couldn't find your moment. Let's start over with /moment"
            )
            return ConversationHandler.END
        
        moment.add_spanish_attempt(spanish_text)
        storage.save_moment(moment)
        
        # For Phase 1, we'll provide a simple encouraging response
        # In Phase 2, this will be replaced with AI feedback
        feedback_message = (
            "🎉 Excellent work! You've completed your Spanish moment.\n\n"
            "**Your English moment:**\n"
            f"_{moment.english_text}_\n\n"
            "**Your Spanish version:**\n"
            f"_{moment.spanish_attempt}_\n\n"
            "🚀 **Coming soon:** AI-powered feedback and corrections!\n"
            "For now, great job practicing your Spanish! 🇪🇸✨\n\n"
            "Ready for another moment? Use /moment to start again!"
        )
        
        # Mark as completed (simple completion for Phase 1)
        moment.add_ai_feedback(
            correction="AI feedback coming in Phase 2!",
            explanation="Detailed explanations will be available soon.",
            difficulty=5,  # Default difficulty
            vocabulary=[]
        )
        storage.save_moment(moment)
        
        await update.message.reply_text(feedback_message)
        
        # Show options for next actions
        next_actions = [
            ["📝 Capture another moment"],
            ["📊 View my stats"],
            ["🔍 See recent moments"]
        ]
        keyboard = ReplyKeyboardMarkup(next_actions, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=keyboard
        )
        
        return ConversationHandler.END
    
    @staticmethod
    async def handle_conversation_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle conversation timeout"""
        await update.message.reply_text(
            "⏰ The conversation has timed out. No worries! "
            "Use /moment when you're ready to capture a new moment.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the current conversation"""
        await update.message.reply_text(
            "❌ Moment capture cancelled. Use /moment to start again when you're ready!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    @staticmethod
    def get_conversation_handler() -> ConversationHandler:
        """Create and return the conversation handler"""
        return ConversationHandler(
            entry_points=[CommandHandler("moment", MomentConversationHandler.start_moment_capture)],
            states={
                WAITING_FOR_MOMENT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        MomentConversationHandler.receive_english_moment
                    )
                ],
                WAITING_FOR_SPANISH: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        MomentConversationHandler.receive_spanish_attempt
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", MomentConversationHandler.cancel_conversation),
                CommandHandler("start", MomentConversationHandler.cancel_conversation),
            ],
            conversation_timeout=settings.CONVERSATION_TIMEOUT,
            name="moment_conversation",
            persistent=False
        )

# Additional command handlers for moment management
class MomentCommandHandlers:
    """Additional command handlers for moment-related functionality"""
    
    @staticmethod
    async def show_recent_moments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show recent moments"""
        user_id = update.effective_user.id
        recent_moments = storage.get_recent_moments(user_id, days=7)
        
        if not recent_moments:
            await update.message.reply_text(
                "📝 You haven't captured any moments in the last 7 days.\n"
                "Use /moment to start capturing your first story-worthy moment!"
            )
            return
        
        message_lines = ["📚 **Your Recent Moments (Last 7 days):**\n"]
        
        for i, moment in enumerate(recent_moments[:5], 1):  # Show max 5
            message_lines.append(f"{i}. {moment.get_summary()}")
        
        if len(recent_moments) > 5:
            message_lines.append(f"\n... and {len(recent_moments) - 5} more moments")
        
        message_lines.append(f"\nUse /stats to see your overall progress!")
        
        await update.message.reply_text("\n".join(message_lines), parse_mode='Markdown')
    
    @staticmethod
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user statistics"""
        user_id = update.effective_user.id
        stats = storage.get_user_stats(user_id)
        
        await update.message.reply_text(stats.get_summary(), parse_mode='Markdown')
    
    @staticmethod
    async def search_moments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Search through moments"""
        # Get search query from command arguments
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text(
                "🔍 **Search your moments**\n\n"
                "Usage: `/search [your search term]`\n\n"
                "Example: `/search coffee` to find moments mentioning coffee"
            )
            return
        
        user_id = update.effective_user.id
        matching_moments = storage.search_moments(user_id, query)
        
        if not matching_moments:
            await update.message.reply_text(
                f"🔍 No moments found containing '{query}'\n\n"
                "Try a different search term or use /recent to see your latest moments."
            )
            return
        
        message_lines = [f"🔍 **Found {len(matching_moments)} moments with '{query}':**\n"]
        
        for i, moment in enumerate(matching_moments[:5], 1):  # Show max 5
            message_lines.append(f"{i}. {moment.get_summary()}")
        
        if len(matching_moments) > 5:
            message_lines.append(f"\n... and {len(matching_moments) - 5} more results")
        
        await update.message.reply_text("\n".join(message_lines), parse_mode='Markdown')
    
    @staticmethod
    async def export_moments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export user's moments"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        try:
            # Create text export
            export_text = storage.export_moments(user_id, format='text')
            
            # Create a temporary file and send it
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(export_text)
                temp_file_path = f.name
            
            # Send the file
            with open(temp_file_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"{user_name}_moments_export.txt",
                    caption="📄 Here's your complete moments export!"
                )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Error exporting moments for user {user_id}: {e}")
            await update.message.reply_text(
                "😅 Sorry, I had trouble creating your export. Please try again later."
            )