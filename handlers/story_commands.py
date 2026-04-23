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
            "<i>What moment from today would be worth telling as a story?</i>\n\n"
            "It doesn't need to be life-changing — just a moment that mattered to you.\n\n"
            "Keep it brief (1-2 sentences). What's your moment? 📝"
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
        """Show a summary card of the user's stories"""
        user = update.effective_user
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id)

        if not stories:
            keyboard = [[InlineKeyboardButton("📝 Record Your First Story", callback_data="quick:story")]]
            await update.message.reply_text(
                "You haven't saved any moments yet.\n\nUse /story to capture your first one.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        keyboard = [
            [InlineKeyboardButton("📥 Export All Stories", callback_data="quick:export")],
        ]
        await update.message.reply_text(
            _stories_summary(stories),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
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
        
        export_date = datetime.now().strftime('%Y-%m-%d')
        content = _build_export_content(stories, user.first_name, export_date)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            filename = f"moments_{user.first_name}_{export_date}.html"
            with open(temp_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"📚 Here are your <b>{len(stories)}</b> storyworthy moments!\n\nKeep capturing life's meaningful moments. ✨",
                    parse_mode='HTML'
                )
            logger.info(f"Exported {len(stories)} stories for user {user.id} ({user.first_name})")
        finally:
            os.unlink(temp_path)
    
    @staticmethod
    async def receive_story_after_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Capture a story from a user who typed directly after receiving a reminder."""
        if not context.user_data.pop('awaiting_story', False):
            return
        await StoryCommandHandlers.receive_story(update, context)

    @staticmethod
    async def story_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle 'story' quick action callback - starts story recording."""
        query = update.callback_query
        await query.answer()
        
        user_first_name = query.from_user.first_name
        
        prompt_message = (
            f"Hey {user_first_name}! 👋\n\n"
            "<i>What moment from today would be worth telling as a story?</i>\n\n"
            "It doesn't need to be life-changing — just a moment that mattered to you.\n\n"
            "Keep it brief (1-2 sentences). What's your moment? 📝"
        )
        
        # Add cancel button
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel:story")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(prompt_message, parse_mode='HTML', reply_markup=reply_markup)
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
        
        stories = StoryCommandHandlers.story_db.get_user_stories(user.id)
        keyboard = [[InlineKeyboardButton("📥 Export All Stories", callback_data="quick:export")]]
        await query.edit_message_text(
            _stories_summary(stories),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
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
        
        export_date = datetime.now().strftime('%Y-%m-%d')
        content = _build_export_content(stories, user.first_name, export_date)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            filename = f"moments_{user.first_name}_{export_date}.html"
            with open(temp_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"📚 Here are your <b>{len(stories)}</b> storyworthy moments!\n\nKeep capturing life's meaningful moments. ✨",
                    parse_mode='HTML'
                )
            await query.edit_message_text(f"✅ Exported {len(stories)} stories!\n\nCheck the file above. 📥")
            logger.info(f"Exported {len(stories)} stories for user {user.id} ({user.first_name}) via callback")
        finally:
            os.unlink(temp_path)

        return ConversationHandler.END


def _stories_summary(stories: list) -> str:
    total = len(stories)
    # stories are newest-first
    first_date = datetime.strptime(stories[-1]['created_at'][:10], '%Y-%m-%d').strftime('%B %-d, %Y')
    last_date = datetime.strptime(stories[0]['created_at'][:10], '%Y-%m-%d').strftime('%B %-d, %Y')

    from datetime import date, timedelta
    today = date.today()
    two_weeks_ago = str(today - timedelta(weeks=2))
    recent = sum(1 for s in stories if s['created_at'][:10] >= two_weeks_ago)

    lines = [
        "📚 <b>Your Moments</b>",
        "",
        f"Total recorded: <b>{total}</b>",
        f"First entry: <b>{first_date}</b>",
        f"Last entry: <b>{last_date}</b>",
        f"Last 2 weeks: <b>{recent}</b>",
    ]
    return "\n".join(lines)


def _build_export_content(stories: list, first_name: str, export_date: str) -> str:
    import html as html_mod

    count = len(stories)
    story_word = 'moment' if count == 1 else 'moments'

    entries_html = []
    current_month = None
    for story in reversed(stories):  # oldest first
        raw_date = story['created_at'][:10]
        dt = datetime.strptime(raw_date, '%Y-%m-%d')
        month_heading = dt.strftime('%B %Y')
        day_heading = dt.strftime('%B %-d, %Y')

        if month_heading != current_month:
            if current_month is not None:
                entries_html.append('</section>')
            entries_html.append(f'<section><h2>{month_heading}</h2>')
            current_month = month_heading

        text = html_mod.escape(story['story_text']).replace('\n', '<br>')
        entries_html.append(
            f'<article><time>{day_heading}</time><p>{text}</p></article>'
        )

    if current_month is not None:
        entries_html.append('</section>')

    body = "\n".join(entries_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My Storyworthy Moments</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 680px;
      margin: 0 auto;
      padding: 24px 20px 60px;
      background: #fafaf8;
      color: #1a1a1a;
    }}
    header {{
      border-bottom: 2px solid #e8e4de;
      padding-bottom: 20px;
      margin-bottom: 36px;
    }}
    header h1 {{
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 6px;
    }}
    header p {{
      color: #888;
      font-size: 0.9rem;
      margin: 0;
    }}
    section {{ margin-bottom: 40px; }}
    h2 {{
      font-size: 1rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #888;
      border-bottom: 1px solid #e8e4de;
      padding-bottom: 6px;
      margin-bottom: 20px;
    }}
    article {{
      margin-bottom: 24px;
      padding-left: 14px;
      border-left: 3px solid #d4c9b8;
    }}
    time {{
      display: block;
      font-size: 0.78rem;
      font-weight: 600;
      color: #aaa;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 6px;
    }}
    p {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.65;
      color: #2d2d2d;
    }}
    footer {{
      margin-top: 48px;
      padding-top: 20px;
      border-top: 1px solid #e8e4de;
      font-style: italic;
      color: #aaa;
      font-size: 0.88rem;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <header>
    <h1>My Storyworthy Moments</h1>
    <p>{html_mod.escape(first_name)} &middot; {export_date} &middot; {count} {story_word}</p>
  </header>

  {body}

  <footer>
    &ldquo;When you start looking for story-worthy moments in your life,
    you start to see them everywhere.&rdquo;<br>
    &mdash; Matthew Dicks
  </footer>
</body>
</html>"""
