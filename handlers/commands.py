"""
Basic command handlers for the Telegram Bot
"""
import logging
import re
from datetime import datetime, time as datetime_time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.assets import load_about_message
from models.story import StoryDatabase

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_STORY = 1
WAITING_FOR_REMINDER_TIME = 2
WAITING_FOR_TIMEZONE = 3

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
        """Send a help message when the command /help is issued."""
        help_message = (
            "🤖 <b>Bot Help</b>\n\n"
            "<b>Getting Started:</b>\n"
            "• /start - Welcome message\n"
            "• /help - Show this help message\n"
            "• /about - Learn about Homework for Life\n\n"
            "<b>Capture Your Stories:</b>\n"
            "• /story - Record today's storyworthy moment\n"
            "• /mystories - View your saved stories\n\n"
            "<b>Reminders:</b>\n"
            "• /reminders - ⏰ Manage daily reminders\n\n"
            "<b>Additional:</b>\n"
            "• /export - Export all your stories as a text file\n\n"
            "💡 Use /story daily to capture moments worth remembering!"
        )
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Try Recording a Story", callback_data="quick:story")],
            [InlineKeyboardButton("⏰ Set Up Reminders", callback_data="quick:reminder")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_message, parse_mode='HTML', reply_markup=reply_markup)
    
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
            story_id = CommandHandlers.story_db.save_story(
                user_id=user.id,
                story_text=story_text,
                username=user.username,
                first_name=user.first_name
            )
            
            # Get total count for this user
            total_stories = CommandHandlers.story_db.count_user_stories(user.id)
            
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
    async def mystories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's saved stories"""
        user = update.effective_user
        
        stories = CommandHandlers.story_db.get_user_stories(user.id, limit=10)
        
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
        
        total_count = CommandHandlers.story_db.count_user_stories(user.id)
        
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
        stories = CommandHandlers.story_db.get_user_stories(user.id)
        
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
        from datetime import datetime
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
        import tempfile
        import os
        
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
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a user-friendly message."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😅 Oops! Something went wrong. Please try again or use /help if you need assistance."
            )
    
    @staticmethod
    async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show reminder management submenu with inline keyboard."""
        user = update.effective_user
        
        # Check if user has a reminder set
        reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
        
        status_text = ""
        if reminder_pref and reminder_pref['enabled']:
            try:
                timezone_str = reminder_pref.get('timezone', 'UTC')
                user_tz = pytz.timezone(timezone_str)
                
                # Parse UTC time and convert to local
                utc_time_str = reminder_pref['reminder_time']
                hour, minute = map(int, utc_time_str.split(':'))
                utc_now = datetime.now(pytz.UTC)
                utc_time = utc_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                local_time = utc_time.astimezone(user_tz)
                local_time_str = local_time.strftime('%H:%M')
                
                status_text = f"\n\n✅ <b>Active Reminder:</b> {local_time_str} ({timezone_str})"
            except:
                status_text = f"\n\n✅ <b>Active Reminder:</b> {reminder_pref['reminder_time']} UTC"
        else:
            status_text = "\n\n🔕 No active reminder set"
        
        keyboard = [
            [InlineKeyboardButton("⏰ Set Daily Reminder", callback_data="reminder:set")],
            [InlineKeyboardButton("📊 View Reminder Status", callback_data="reminder:view")],
            [InlineKeyboardButton("🔕 Stop Reminders", callback_data="reminder:stop")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "⏰ <b>Reminder Settings</b>\n\n"
            "Set up daily reminders to capture your storyworthy moments.{status_text}\n\n"
            "Choose an option below:"
        ).format(status_text=status_text)
        
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)
    
    @staticmethod
    async def reminder_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle reminder submenu button clicks."""
        query = update.callback_query
        await query.answer()
        
        action = query.data.split(':')[1]
        user = query.from_user
        
        if action == 'set':
            # Start the setreminder flow
            reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
            
            existing_info = ""
            if reminder_pref and reminder_pref['enabled']:
                tz_name = reminder_pref['timezone']
                local_time = reminder_pref['reminder_time']
                existing_info = f"\n\nYou currently have a reminder set for <b>{local_time}</b> in <b>{tz_name}</b> timezone."
            
            # Create inline keyboard with common timezones
            keyboard = [
                [InlineKeyboardButton("🇺🇸 US Eastern", callback_data="tz:America/New_York"),
                 InlineKeyboardButton("🇺🇸 US Pacific", callback_data="tz:America/Los_Angeles")],
                [InlineKeyboardButton("🇺🇸 US Central", callback_data="tz:America/Chicago"),
                 InlineKeyboardButton("🇺🇸 US Mountain", callback_data="tz:America/Denver")],
                [InlineKeyboardButton("🇬🇧 London", callback_data="tz:Europe/London"),
                 InlineKeyboardButton("🇫🇷 Paris/Berlin", callback_data="tz:Europe/Paris")],
                [InlineKeyboardButton("🇯🇵 Tokyo", callback_data="tz:Asia/Tokyo"),
                 InlineKeyboardButton("🇨🇳 Shanghai", callback_data="tz:Asia/Shanghai")],
                [InlineKeyboardButton("🇮🇳 India", callback_data="tz:Asia/Kolkata"),
                 InlineKeyboardButton("🇦🇺 Sydney", callback_data="tz:Australia/Sydney")],
                [InlineKeyboardButton("🌍 Other (type manually)", callback_data="tz:manual")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prompt_message = (
                f"Hey {user.first_name}! ⏰\n\n"
                f"Let's set up your daily reminder to capture your storyworthy moment.{existing_info}\n\n"
                f"First, select your timezone:"
            )
            
            await query.edit_message_text(prompt_message, parse_mode='HTML', reply_markup=reply_markup)
            return WAITING_FOR_TIMEZONE
            
        elif action == 'view':
            # Show reminder status
            reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
            
            if not reminder_pref:
                await query.edit_message_text(
                    "🤔 You don't have a reminder set yet.\n\n"
                    "Use /reminders to set one up!",
                    parse_mode='HTML'
                )
                return ConversationHandler.END
            
            status = "✅ Active" if reminder_pref['enabled'] else "🔕 Stopped"
            
            # Convert UTC time to user's local timezone
            try:
                timezone_str = reminder_pref.get('timezone', 'UTC')
                user_tz = pytz.timezone(timezone_str)
                
                # Parse UTC time
                utc_time_str = reminder_pref['reminder_time']
                hour, minute = map(int, utc_time_str.split(':'))
                
                # Create UTC datetime and convert to user's timezone
                utc_now = datetime.now(pytz.UTC)
                utc_time = utc_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                local_time = utc_time.astimezone(user_tz)
                local_time_str = local_time.strftime('%H:%M')
                
                info_message = (
                    f"⏰ <b>Reminder Status</b>\n\n"
                    f"Status: {status}\n"
                    f"Time: <b>{local_time_str}</b>\n"
                    f"Timezone: <b>{timezone_str}</b>\n\n"
                )
            except Exception as e:
                logger.error(f"Error converting timezone: {e}")
                info_message = (
                    f"⏰ <b>Reminder Status</b>\n\n"
                    f"Status: {status}\n"
                    f"Scheduled time: <b>{reminder_pref['reminder_time']} UTC</b>\n\n"
                )
            
            if reminder_pref['enabled']:
                info_message += "Your daily reminder is active! I'll send you a message at the scheduled time.\n\n"
            else:
                info_message += "Your reminder is currently stopped.\n\n"
            
            info_message += (
                "💡 Use /reminders to manage your reminder settings."
            )
            
            await query.edit_message_text(info_message, parse_mode='HTML')
            return ConversationHandler.END
            
        elif action == 'stop':
            # Stop reminders
            was_disabled = CommandHandlers.story_db.disable_reminder(user.id)
            
            if was_disabled:
                response = (
                    "🔕 Your daily reminder has been stopped.\n\n"
                    "You can always turn it back on with /reminders whenever you're ready!\n\n"
                    "Keep capturing those moments! ✨"
                )
            else:
                response = (
                    "🤔 You don't have an active reminder set.\n\n"
                    "Use /reminders to create one!"
                )
            
            await query.edit_message_text(response, parse_mode='HTML')
            return ConversationHandler.END
        
        return ConversationHandler.END
    
    @staticmethod
    async def setreminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Start the reminder setup conversation.
        Show inline keyboard with common timezones.
        """
        user_first_name = update.effective_user.first_name
        user = update.effective_user
        reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
        
        existing_info = ""
        if reminder_pref and reminder_pref['enabled']:
            tz_name = reminder_pref['timezone']
            local_time = reminder_pref['reminder_time']
            existing_info = f"\n\nYou currently have a reminder set for <b>{local_time}</b> in <b>{tz_name}</b> timezone."
        
        # Create inline keyboard with common timezones
        keyboard = [
            [InlineKeyboardButton("🇺🇸 US Eastern", callback_data="tz:America/New_York"),
             InlineKeyboardButton("🇺🇸 US Pacific", callback_data="tz:America/Los_Angeles")],
            [InlineKeyboardButton("🇺🇸 US Central", callback_data="tz:America/Chicago"),
             InlineKeyboardButton("🇺🇸 US Mountain", callback_data="tz:America/Denver")],
            [InlineKeyboardButton("🇬🇧 London", callback_data="tz:Europe/London"),
             InlineKeyboardButton("🇫🇷 Paris/Berlin", callback_data="tz:Europe/Paris")],
            [InlineKeyboardButton("🇯🇵 Tokyo", callback_data="tz:Asia/Tokyo"),
             InlineKeyboardButton("🇨🇳 Shanghai", callback_data="tz:Asia/Shanghai")],
            [InlineKeyboardButton("🇮🇳 India", callback_data="tz:Asia/Kolkata"),
             InlineKeyboardButton("🇦🇺 Sydney", callback_data="tz:Australia/Sydney")],
            [InlineKeyboardButton("🌍 Other (type manually)", callback_data="tz:manual")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel:reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        prompt_message = (
            f"Hey {user_first_name}! ⏰\n\n"
            f"Let's set up your daily reminder to capture your storyworthy moment.{existing_info}\n\n"
            f"First, select your timezone:"
        )
        
        await update.message.reply_text(prompt_message, parse_mode='HTML', reply_markup=reply_markup)
        
        return WAITING_FOR_TIMEZONE
    
    @staticmethod
    async def timezone_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handle timezone selection from inline keyboard.
        """
        query = update.callback_query
        await query.answer()
        
        timezone_data = query.data.replace("tz:", "")
        
        # If user selected "Other", ask for manual input
        if timezone_data == "manual":
            prompt_message = (
                "📝 Please type your timezone manually.\n\n"
                "Examples:\n"
                "• <code>America/New_York</code>\n"
                "• <code>Europe/London</code>\n"
                "• <code>Asia/Tokyo</code>\n\n"
                "<i>Find your timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones</i>"
            )
            await query.edit_message_text(prompt_message, parse_mode='HTML')
            return WAITING_FOR_TIMEZONE
        
        # Validate and use the selected timezone
        try:
            tz = pytz.timezone(timezone_data)
            context.user_data['timezone'] = timezone_data
            
            # Show current time in their timezone
            now_in_tz = datetime.now(tz)
            current_time = now_in_tz.strftime('%H:%M')
            
            prompt_message = (
                f"✅ Timezone set to <b>{timezone_data}</b>\n"
                f"Current time there: <b>{current_time}</b>\n\n"
                f"Now, what time would you like your daily reminder?\n\n"
                f"Please use <b>HH:MM</b> format (24-hour) in <b>your local time</b>:\n\n"
                f"Examples:\n"
                f"• <code>09:00</code> - 9:00 AM\n"
                f"• <code>14:30</code> - 2:30 PM\n"
                f"• <code>20:00</code> - 8:00 PM\n\n"
                f"What time works for you? 📝"
            )
            
            await query.edit_message_text(prompt_message, parse_mode='HTML')
            return WAITING_FOR_REMINDER_TIME
            
        except pytz.exceptions.UnknownTimeZoneError:
            await query.edit_message_text(
                f"⚠️ Something went wrong. Please try /setreminder again.",
                parse_mode='HTML'
            )
            return ConversationHandler.END
    
    @staticmethod
    async def receive_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Receive and validate the timezone from the user (manual text input).
        """
        timezone_text = update.message.text.strip()
        user = update.effective_user
        
        # Validate timezone
        try:
            tz = pytz.timezone(timezone_text)
            # Store timezone in context for next step
            context.user_data['timezone'] = timezone_text
            
            # Show current time in their timezone
            now_in_tz = datetime.now(tz)
            current_time = now_in_tz.strftime('%H:%M')
            
            prompt_message = (
                f"✅ Great! Timezone set to <b>{timezone_text}</b>.\n"
                f"Current time there: <b>{current_time}</b>\n\n"
                f"Now, what time would you like your daily reminder?\n\n"
                f"Please use <b>HH:MM</b> format (24-hour) in <b>your local time</b>:\n\n"
                f"Examples:\n"
                f"• <code>09:00</code> - 9:00 AM\n"
                f"• <code>14:30</code> - 2:30 PM\n"
                f"• <code>20:00</code> - 8:00 PM\n\n"
                f"What time works for you? 📝"
            )
            
            await update.message.reply_text(prompt_message, parse_mode='HTML')
            return WAITING_FOR_REMINDER_TIME
            
        except pytz.exceptions.UnknownTimeZoneError:
            await update.message.reply_text(
                f"⚠️ I don't recognize <code>{timezone_text}</code> as a valid timezone.\n\n"
                f"Please try again with a timezone like:\n"
                f"• <code>America/New_York</code>\n"
                f"• <code>Europe/London</code>\n"
                f"• <code>Asia/Tokyo</code>\n\n"
                f"Or use /cancel to stop.",
                parse_mode='HTML'
            )
            return WAITING_FOR_TIMEZONE
    @staticmethod
    async def receive_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Receive and validate the reminder time from the user (in their local timezone).
        Convert to UTC for storage.
        """
        time_text = update.message.text.strip()
        user = update.effective_user
        
        # Validate time format (HH:MM)
        time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$')
        match = time_pattern.match(time_text)
        
        if not match:
            await update.message.reply_text(
                "⚠️ That doesn't look like a valid time format.\n\n"
                "Please use <b>HH:MM</b> format (24-hour), like:\n"
                "• <code>09:00</code>\n"
                "• <code>14:30</code>\n"
                "• <code>20:00</code>\n\n"
                "Try again or use /cancel to stop:",
                parse_mode='HTML'
            )
            return WAITING_FOR_REMINDER_TIME
        
        try:
            # Get timezone from context
            timezone_str = context.user_data.get('timezone', 'UTC')
            user_tz = pytz.timezone(timezone_str)
            
            # Parse the time
            hour, minute = map(int, time_text.split(':'))
            
            # Create a datetime in user's timezone for today
            now = datetime.now(user_tz)
            local_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Convert to UTC
            utc_time = local_time.astimezone(pytz.UTC)
            utc_time_str = utc_time.strftime('%H:%M')
            
            # Save the reminder preference with UTC time
            CommandHandlers.story_db.set_reminder(
                user_id=user.id,
                reminder_time=utc_time_str,
                timezone=timezone_str
            )
            
            response = (
                f"✅ Perfect! Your daily reminder is set for <b>{time_text}</b> ({timezone_str}).\n\n"
                f"I'll send you a friendly nudge every day at this time to capture your moment.\n\n"
                f"💡 Use /reminders to manage your reminder settings anytime.\n\n"
                f"Happy storytelling! 🌟"
            )
            
            await update.message.reply_text(response, parse_mode='HTML')
            
            logger.info(f"Reminder set for user {user.id} ({user.first_name}) at {time_text} {timezone_str} (UTC: {utc_time_str})")
            
            # Clear user data
            context.user_data.clear()
            
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            await update.message.reply_text(
                "😅 Oops! Something went wrong setting your reminder. Please try again with /setreminder"
            )
        
        return ConversationHandler.END
    
    @staticmethod
    async def stopreminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop daily reminders for the user."""
        user = update.effective_user
        
        # Try to disable the reminder
        was_disabled = CommandHandlers.story_db.disable_reminder(user.id)
        
        if was_disabled:
            response = (
                "🔕 Your daily reminder has been stopped.\n\n"
                "You can always turn it back on with /setreminder whenever you're ready!\n\n"
                "Keep capturing those moments! ✨"
            )
        else:
            response = (
                "🤔 You don't have an active reminder set.\n\n"
                "Use /setreminder to create one!"
            )
        
        await update.message.reply_text(response, parse_mode='HTML')
    
    @staticmethod
    async def myreminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the user's current reminder status."""
        user = update.effective_user
        
        # Check if user has a reminder set
        reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
        
        if not reminder_pref:
            await update.message.reply_text(
                "🤔 You don't have a reminder set yet.\n\n"
                "Use /setreminder to create one first!",
                parse_mode='HTML'
            )
            return
        
        status = "✅ Active" if reminder_pref['enabled'] else "🔕 Stopped"
        
        # Convert UTC time to user's local timezone
        try:
            timezone_str = reminder_pref.get('timezone', 'UTC')
            user_tz = pytz.timezone(timezone_str)
            
            # Parse UTC time
            utc_time_str = reminder_pref['reminder_time']
            hour, minute = map(int, utc_time_str.split(':'))
            
            # Create UTC datetime and convert to user's timezone
            utc_now = datetime.now(pytz.UTC)
            utc_time = utc_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            local_time = utc_time.astimezone(user_tz)
            local_time_str = local_time.strftime('%H:%M')
            
            info_message = (
                f"⏰ <b>Reminder Status</b>\n\n"
                f"Status: {status}\n"
                f"Time: <b>{local_time_str}</b>\n"
                f"Timezone: <b>{timezone_str}</b>\n\n"
            )
        except Exception as e:
            logger.error(f"Error converting timezone: {e}")
            info_message = (
                f"⏰ <b>Reminder Status</b>\n\n"
                f"Status: {status}\n"
                f"Scheduled time: <b>{reminder_pref['reminder_time']} UTC</b>\n\n"
            )
        
        if reminder_pref['enabled']:
            info_message += "Your daily reminder is active! I'll send you a message at the scheduled time.\n\n"
        else:
            info_message += "Your reminder is currently stopped.\n\n"
        
        info_message += "💡 Use /reminders to manage your reminder settings."
        
        await update.message.reply_text(info_message, parse_mode='HTML')
    
    @staticmethod
    async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the reminder setup conversation."""
        await update.message.reply_text(
            "No problem! Your reminder wasn't changed.\n\n"
            "Use /setreminder whenever you want to set it up! 👋"
        )
        return ConversationHandler.END
    
    @staticmethod
    async def send_reminder_to_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, first_name: str = None) -> None:
        """
        Send a reminder message to a specific user.
        This is called by the job queue scheduler.
        """
        if not first_name:
            first_name = "there"
        
        reminder_message = (
            f"🌟 <b>Daily Reminder</b> 🌟\n\n"
            f"Hey {first_name}! Time for your Homework for Life.\n\n"
            f"<i>If you had to tell a story from today — a five-minute story onstage "
            f"about something that took place over the course of this day — what would it be?</i>\n\n"
            f"Take a moment to reflect on your day. What moment stood out?\n\n"
            f"Use /story to capture it! 📝"
        )
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=reminder_message,
                parse_mode='HTML'
            )
            logger.info(f"Reminder sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send reminder to user {user_id}: {e}")
    
    @staticmethod
    async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle cancel button clicks from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        action = query.data.split(':')[1]
        
        if action == 'story':
            await query.edit_message_text(
                "No worries! Your story wasn't saved. "
                "Come back with /story whenever you're ready! 👋"
            )
        elif action == 'reminder':
            await query.edit_message_text(
                "No problem! Your reminder wasn't changed.\n\n"
                "Use /reminders whenever you want to set it up! 👋"
            )
        
        return ConversationHandler.END
    
    @staticmethod
    async def quick_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle quick action button clicks from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        action = query.data.split(':')[1]
        user = query.from_user
        
        if action == 'story':
            # Start story conversation
            user_first_name = user.first_name
            
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
            
        elif action == 'about':
            # Show about message
            about_message = load_about_message(user.first_name)
            
            # Add quick action buttons
            keyboard = [
                [InlineKeyboardButton("📝 Record a Story", callback_data="quick:story")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="quick:help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(about_message, parse_mode='HTML', reply_markup=reply_markup)
            return ConversationHandler.END
        
        elif action == 'help':
            # Show help message
            help_message = (
                "🤖 <b>Bot Help</b>\n\n"
                "<b>Getting Started:</b>\n"
                "• /start - Welcome message\n"
                "• /help - Show this help message\n"
                "• /about - Learn about Homework for Life\n\n"
                "<b>Capture Your Stories:</b>\n"
                "• /story - Record today's storyworthy moment\n"
                "• /mystories - View your saved stories\n\n"
                "<b>Reminders:</b>\n"
                "• /reminders - ⏰ Manage daily reminders\n\n"
                "<b>Additional:</b>\n"
                "• /export - Export all your stories as a text file\n\n"
                "💡 Use /story daily to capture moments worth remembering!"
            )
            await query.edit_message_text(help_message, parse_mode='HTML')
            return ConversationHandler.END
        
        elif action == 'mystories':
            # Show user's stories
            stories = CommandHandlers.story_db.get_user_stories(user.id, limit=10)
            
            if not stories:
                await query.edit_message_text(
                    "📭 You haven't saved any stories yet!\n\n"
                    "Use /story to capture your first moment.",
                    parse_mode='HTML'
                )
                return ConversationHandler.END
            
            total_count = CommandHandlers.story_db.count_user_stories(user.id)
            
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
        
        elif action == 'export':
            # Export user stories
            stories = CommandHandlers.story_db.get_user_stories(user.id)
            
            if not stories:
                await query.edit_message_text(
                    "📭 You don't have any stories to export yet!\n\n"
                    "Use /story to capture your first moment.",
                    parse_mode='HTML'
                )
                return ConversationHandler.END
            
            # Generate the text file content
            from datetime import datetime
            import tempfile
            import os
            
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
            
        elif action == 'reminder':
            # Start reminder setup - show reminders menu
            reminder_pref = CommandHandlers.story_db.get_reminder_preference(user.id)
            
            status_text = ""
            if reminder_pref and reminder_pref['enabled']:
                try:
                    timezone_str = reminder_pref.get('timezone', 'UTC')
                    user_tz = pytz.timezone(timezone_str)
                    
                    utc_time_str = reminder_pref['reminder_time']
                    hour, minute = map(int, utc_time_str.split(':'))
                    utc_now = datetime.now(pytz.UTC)
                    utc_time = utc_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    local_time = utc_time.astimezone(user_tz)
                    local_time_str = local_time.strftime('%H:%M')
                    
                    status_text = f"\n\n✅ <b>Active Reminder:</b> {local_time_str} ({timezone_str})"
                except:
                    status_text = f"\n\n✅ <b>Active Reminder:</b> {reminder_pref['reminder_time']} UTC"
            else:
                status_text = "\n\n🔕 No active reminder set"
            
            keyboard = [
                [InlineKeyboardButton("⏰ Set Daily Reminder", callback_data="reminder:set")],
                [InlineKeyboardButton("📊 View Reminder Status", callback_data="reminder:view")],
                [InlineKeyboardButton("🔕 Stop Reminders", callback_data="reminder:stop")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = (
                "⏰ <b>Reminder Settings</b>\n\n"
                "Set up daily reminders to capture your storyworthy moments.{status_text}\n\n"
                "Choose an option below:"
            ).format(status_text=status_text)
            
            await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
            return ConversationHandler.END
        
        return ConversationHandler.END