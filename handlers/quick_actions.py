"""
Quick action router for inline button callbacks from /start command
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from .basic_commands import BasicCommandHandlers
from .story_commands import StoryCommandHandlers
from .reminder_commands import ReminderCommandHandlers

logger = logging.getLogger(__name__)

# Dispatch table mapping action names to their handler methods
QUICK_ACTION_HANDLERS = {
    'about': BasicCommandHandlers.about_callback,
    'help': BasicCommandHandlers.help_callback,
    'story': StoryCommandHandlers.story_callback,
    'mystories': StoryCommandHandlers.mystories_callback,
    'export': StoryCommandHandlers.export_callback,
    'reminder': ReminderCommandHandlers.reminder_callback,
}


async def quick_action_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Routes quick action callbacks from /start inline buttons to appropriate handlers.
    
    Callback data format: "quick:<action>"
    Supported actions: about, help, story, mystories, export, reminder
    """
    query = update.callback_query
    
    # Parse action from callback data
    try:
        action = query.data.split(':')[1]
    except IndexError:
        logger.error(f"Invalid callback data format: {query.data}")
        await query.answer("❌ Invalid action", show_alert=True)
        return
    
    # Dispatch to appropriate handler
    handler = QUICK_ACTION_HANDLERS.get(action)
    
    if handler:
        logger.info(f"Routing quick action '{action}' to {handler.__name__}")
        return await handler(update, context)
    else:
        logger.warning(f"Unknown quick action: {action}")
        await query.answer("❌ Unknown action", show_alert=True)
        return
