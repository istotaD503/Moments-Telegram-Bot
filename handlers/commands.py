"""
Basic command handlers for the Telegram Bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.assets import load_welcome_message
from models.story import StoryDatabase

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_STORY = 1

class CommandHandlers:
    """Basic command handlers for common bot functionality"""
    
    # Initialize story database
    story_db = StoryDatabase()
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a minimal welcome message when the command /start is issued."""
        user_first_name = update.effective_user.first_name
        
        welcome_message = (
            f"Hello {user_first_name}! 👋\n\n"
            "Welcome to <b>Moments Bot</b> - your daily companion for capturing life's storyworthy moments!\n\n"
            "📝 Use /story to record today's moment\n"
            "📖 Use /about to learn more about this practice\n"
            "❓ Use /help to see all commands"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='HTML')
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send detailed information about the bot and Homework for Life."""
        user_first_name = update.effective_user.first_name
        
        about_message = load_welcome_message(user_first_name)
        
        await update.message.reply_text(about_message, parse_mode='HTML')
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a help message when the command /help is issued."""
        help_message = (
            "🤖 <b>Bot Help</b>\n\n"
            "<b>Available Commands:</b>\n"
            "• /start - Welcome message\n"
            "• /about - Learn about Homework for Life\n"
            "• /story - Record today's storyworthy moment\n"
            "• /mystories - View your saved stories\n"
            "• /help - Show this help message\n\n"
            "💡 Use /story daily to capture moments worth remembering!"
        )
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    @staticmethod
    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands"""
        await update.message.reply_text(
            "🤔 I don't recognize that command. Use /help to see all available commands!"
        )
    
    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages"""
        message_text = update.message.text
        user_first_name = update.effective_user.first_name
        
        response = (
            f"Hi {user_first_name}! 👋\n\n"
            f"I received your message: \"{message_text}\"\n\n"
            f"I'm still learning what to do with regular messages. "
            f"For now, try using /help to see what I can do!"
        )
        
        await update.message.reply_text(response)
    
    @staticmethod
    async def story_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Start the story recording conversation.
        Prompts user for their storyworthy moment in Matthew Dicks' voice.
        """
        user_first_name = update.effective_user.first_name
        
        # Matthew Dicks-inspired prompt
        prompt_message = (
            f"Hey {user_first_name}! 👋\n\n"
            "Here's your homework for today:\n\n"
            "<i>If you had to tell a story from today — a five-minute story onstage "
            "about something that took place over the course of this day — what would it be?</i>\n\n"
            "It doesn't need to be spectacular. It doesn't need to be life-changing. "
            "It just needs to be a moment that mattered to you.\n\n"
            "Keep it to 1-2 sentences. What's your moment? 📝"
        )
        
        await update.message.reply_text(prompt_message, parse_mode='HTML')
        
        # Set the conversation state
        return WAITING_FOR_STORY
    
    @staticmethod
    async def receive_story(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Receive and save the user's story.
        """
        story_text = update.message.text
        user = update.effective_user
        
        try:
            # Save the story to database
            story_id = CommandHandlers.story_db.save_story(
                user_id=user.id,
                story_text=story_text,
                username=user.username,
                first_name=user.first_name
            )
            
            # Get total count for this user
            total_stories = CommandHandlers.story_db.count_user_stories(user.id)
            
            # Encouraging response in Matthew Dicks' spirit
            response = (
                f"✨ Beautiful! Story saved.\n\n"
                f"That's <b>{total_stories}</b> moment{'s' if total_stories != 1 else ''} captured so far.\n\n"
                f"<i>\"When you start looking for story-worthy moments in your life, "
                f"you start to see them everywhere.\"</i>\n\n"
                f"See you tomorrow! 🌟"
            )
            
            await update.message.reply_text(response, parse_mode='HTML')
            
            logger.info(f"Story {story_id} saved for user {user.id} ({user.first_name})")
            
        except Exception as e:
            logger.error(f"Error saving story: {e}")
            await update.message.reply_text(
                "😅 Oops! Something went wrong saving your story. Please try again with /story"
            )
        
        # End conversation
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_story(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the story recording conversation."""
        await update.message.reply_text(
            "No worries! Your story wasn't saved. "
            "Come back with /story whenever you're ready! 👋"
        )
        return ConversationHandler.END
    
    @staticmethod
    async def mystories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's saved stories"""
        user = update.effective_user
        
        stories = CommandHandlers.story_db.get_user_stories(user.id, limit=10)
        
        if not stories:
            await update.message.reply_text(
                "📭 You haven't saved any stories yet!\n\n"
                "Use /story to capture your first moment.",
                parse_mode='HTML'
            )
            return
        
        total_count = CommandHandlers.story_db.count_user_stories(user.id)
        
        message = f"📚 <b>Your Stories</b> (showing last {len(stories)} of {total_count}):\n\n"
        
        for i, story in enumerate(stories, 1):
            date = story['created_at'].split(' ')[0]  # Get just the date part
            story_preview = story['story_text'][:100]
            if len(story['story_text']) > 100:
                story_preview += "..."
            
            message += f"<b>{i}. {date}</b>\n{story_preview}\n\n"
        
        message += "\n💡 Use /story to add a new moment!"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a user-friendly message."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😅 Oops! Something went wrong. Please try again or use /help if you need assistance."
            )