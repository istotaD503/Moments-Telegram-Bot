"""
Story-related command handlers for the Telegram Bot
"""
import logging
import tempfile
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from .shared import story_db

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_STORY = 1


class StoryCommandHandlers:
    """Handlers for story recording, viewing, and exporting"""
    
    # Reference to shared database instance
    story_db = story_db
    
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
        
        # Add cancel button
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel:story")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(prompt_message, parse_mode='HTML', reply_markup=reply_markup)
        
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
            story_id = StoryCommandHandlers.story_db.save_story(
                user_id=user.id,
                story_text=story_text,
                username=user.username,
                first_name=user.first_name
            )
            
            # Get total count for this user
            total_stories = StoryCommandHandlers.story_db.count_user_stories(user.id)
            
            # Analyze story length and provide feedback
            word_count = len(story_text.split())
            length_tip = ""
            if word_count < 5:
                length_tip = "\n\n💡 <i>Tip: Try adding a bit more detail next time!</i>"
            elif word_count > 100:
                length_tip = "\n\n💡 <i>Tip: Remember, brevity is key! Aim for 1-2 sentences.</i>"
            
            # Encouraging response in Matthew Dicks' spirit
            response = (
                f"✨ Beautiful! Story saved.\n\n"
                f"That's <b>{total_stories}</b> moment{'s' if total_stories != 1 else ''} captured so far.\n\n"
                f"<i>\"When you start looking for story-worthy moments in your life, "
                f"you start to see them everywhere.\"</i>{length_tip}\n\n"
                f"See you tomorrow! 🌟"
            )
            
            # Add quick action button
            keyboard = [
                [InlineKeyboardButton("📚 View My Stories", callback_data="quick:mystories")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode='HTML', reply_markup=reply_markup)
            
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
    async def cancel_story_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle cancel button click for story recording."""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "No worries! Your story wasn't saved. "
            "Come back with /story whenever you're ready! 👋"
        )
        return ConversationHandler.END
    
    @staticmethod
    async def mystories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's saved stories"""
        user = update.effective_user
        
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id, limit=10)
        
        if not stories:
            # Add action button for empty state
            keyboard = [[InlineKeyboardButton("📝 Record Your First Story", callback_data="quick:story")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📭 You haven't saved any stories yet!\n\n"
                "Use /story to capture your first moment.",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return
        
        total_count = StoryCommandHandlers.story_db.count_user_stories(user.id)
        
        message = f"📚 <b>Your Stories</b> (showing last {len(stories)} of {total_count}):\n\n"
        
        for i, story in enumerate(stories, 1):
            date = story['created_at'].split(' ')[0]  # Get just the date part
            story_preview = story['story_text'][:100]
            if len(story['story_text']) > 100:
                story_preview += "..."
            
            message += f"<b>{i}. {date}</b>\n{story_preview}\n\n"
        
        message += "💡 <i>Tip: Use /export to download all your stories as a text file.</i>"
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Record New Story", callback_data="quick:story")],
            [InlineKeyboardButton("📥 Export Stories", callback_data="quick:export")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    @staticmethod
    async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export all user stories to a text file"""
        user = update.effective_user
        
        # Get all stories for the user
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id)
        
        if not stories:
            # Add action button for empty state
            keyboard = [[InlineKeyboardButton("📝 Record Your First Story", callback_data="quick:story")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📭 You don't have any stories to export yet!\n\n"
                "Use /story to capture your first moment.",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return
        
        # Generate the text file content
        export_date = datetime.now().strftime('%Y-%m-%d')
        
        content = f"My Storyworthy Moments\n"
        content += f"Exported on {export_date}\n"
        content += f"Total moments: {len(stories)}\n"
        content += "=" * 50 + "\n\n"
        
        for i, story in enumerate(reversed(stories), 1):  # Oldest to newest
            date = story['created_at'].split(' ')[0]
            content += f"{i}. {date}\n"
            content += f"{story['story_text']}\n"
            content += "-" * 50 + "\n\n"
        
        content += "\n" + "=" * 50 + "\n"
        content += '"When you start looking for story-worthy moments in your life, '
        content += 'you start to see them everywhere." - Matthew Dicks\n'
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Send the file
            filename = f"moments_{user.first_name}_{export_date}.txt"
            
            with open(temp_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"📚 Here are your <b>{len(stories)}</b> storyworthy moments!\n\nKeep capturing life's meaningful moments. ✨",
                    parse_mode='HTML'
                )
            
            logger.info(f"Exported {len(stories)} stories for user {user.id} ({user.first_name})")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    @staticmethod
    async def story_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle 'story' quick action callback - starts story recording."""
        query = update.callback_query
        await query.answer()
        
        user_first_name = query.from_user.first_name
        
        prompt_message = (
            f"Hey {user_first_name}! 👋\n\n"
            "Here's your homework for today:\n\n"
            "<i>If you had to tell a story from today — a five-minute story onstage "
            "about something that took place over the course of this day — what would it be?</i>\n\n"
            "It doesn't need to be spectacular. It doesn't need to be life-changing. "
            "It just needs to be a moment that mattered to you.\n\n"
            "Keep it to 1-2 sentences. What's your moment? 📝"
        )
        
        await query.edit_message_text(prompt_message, parse_mode='HTML')
        return WAITING_FOR_STORY
    
    @staticmethod
    async def mystories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle 'mystories' quick action callback."""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id, limit=10)
        
        if not stories:
            await query.edit_message_text(
                "📭 You haven't saved any stories yet!\n\n"
                "Use /story to capture your first moment.",
                parse_mode='HTML'
            )
            return ConversationHandler.END
        
        total_count = StoryCommandHandlers.story_db.count_user_stories(user.id)
        
        message = f"📚 <b>Your Stories</b> (showing last {len(stories)} of {total_count}):\n\n"
        
        for i, story in enumerate(stories, 1):
            date = story['created_at'].split(' ')[0]
            story_preview = story['story_text'][:100]
            if len(story['story_text']) > 100:
                story_preview += "..."
            
            message += f"<b>{i}. {date}</b>\n{story_preview}\n\n"
        
        message += "\n💡 Use /story to add a new moment!"
        message += "\n📥 Use /export to download all your stories as a file."
        
        await query.edit_message_text(message, parse_mode='HTML')
        return ConversationHandler.END
    
    @staticmethod
    async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle 'export' quick action callback."""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id)
        
        if not stories:
            await query.edit_message_text(
                "📭 You don't have any stories to export yet!\n\n"
                "Use /story to capture your first moment.",
                parse_mode='HTML'
            )
            return ConversationHandler.END
        
        # Generate the text file content
        export_date = datetime.now().strftime('%Y-%m-%d')
        
        content = f"My Storyworthy Moments\n"
        content += f"Exported on {export_date}\n"
        content += f"Total moments: {len(stories)}\n"
        content += "=" * 50 + "\n\n"
        
        for i, story in enumerate(reversed(stories), 1):
            date = story['created_at'].split(' ')[0]
            content += f"{i}. {date}\n"
            content += f"{story['story_text']}\n"
            content += "-" * 50 + "\n\n"
        
        content += "\n" + "=" * 50 + "\n"
        content += '"When you start looking for story-worthy moments in your life, '
        content += 'you start to see them everywhere." - Matthew Dicks\n'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            filename = f"moments_{user.first_name}_{export_date}.txt"
            
            with open(temp_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"📚 Here are your <b>{len(stories)}</b> storyworthy moments!\n\nKeep capturing life's meaningful moments. ✨",
                    parse_mode='HTML'
                )
            
            # Edit original message to confirm
            await query.edit_message_text(
                f"✅ Exported {len(stories)} stories!\n\nCheck the file above. 📥"
            )
            
            logger.info(f"Exported {len(stories)} stories for user {user.id} ({user.first_name}) via callback")
            
        finally:
            os.unlink(temp_path)
        
        return ConversationHandler.END
