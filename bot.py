#!/usr/bin/env python3
"""
Telegram Bot for capturing daily storyworthy moments
"""

import logging
import sys
from datetime import datetime, time as datetime_time, timedelta
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler

from config.settings import settings
from handlers.commands import CommandHandlers, WAITING_FOR_STORY, WAITING_FOR_REMINDER_TIME, WAITING_FOR_TIMEZONE

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def check_and_send_reminders(context):
    """
    Job that runs periodically to check and send reminders.
    Checks every minute and sends reminders to users whose time has come.
    """
    from models.story import StoryDatabase
    
    db = StoryDatabase()
    active_reminders = db.get_all_active_reminders()
    
    # Get current time in UTC
    now = datetime.utcnow()
    current_time_str = now.strftime('%H:%M')
    
    logger.info(f"Checking reminders at {current_time_str} UTC. Found {len(active_reminders)} active reminders.")
    
    for reminder in active_reminders:
        user_id = reminder['user_id']
        reminder_time = reminder['reminder_time']
        
        # Check if current time matches the reminder time
        if current_time_str == reminder_time:
            logger.info(f"Sending reminder to user {user_id} at {reminder_time}")
            
            # Try to get user's first name from database (from their stories)
            stories = db.get_user_stories(user_id, limit=1)
            first_name = stories[0]['first_name'] if stories and stories[0]['first_name'] else None
            
            await CommandHandlers.send_reminder_to_user(context, user_id, first_name)

def main():
    """Main function to run the Telegram bot"""
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print("🤖 Starting Bot...")
    telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    # Log all incoming updates
    async def log_update(update, context):
        logging.info(f"Received update: {update.to_dict()}")
    
    # Add logger as the first handler to catch everything
    telegram_app.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    # Story command with conversation handler
    story_conversation = ConversationHandler(
        entry_points=[CommandHandler("story", CommandHandlers.story_command)],
        states={
            WAITING_FOR_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_story)
            ]
        },
        fallbacks=[CommandHandler("cancel", CommandHandlers.cancel_story)]
    )
    telegram_app.add_handler(story_conversation)
    
    # Reminder setup conversation handler
    reminder_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("setreminder", CommandHandlers.setreminder_command),
            CallbackQueryHandler(CommandHandlers.reminder_menu_callback, pattern="^reminder:")
        ],
        states={
            WAITING_FOR_TIMEZONE: [
                CallbackQueryHandler(CommandHandlers.timezone_button_callback, pattern="^tz:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_timezone)
            ],
            WAITING_FOR_REMINDER_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_reminder_time)
            ]
        },
        fallbacks=[CommandHandler("cancel", CommandHandlers.cancel_reminder)]
    )
    telegram_app.add_handler(reminder_conversation)

    # Other commands
    telegram_app.add_handler(CommandHandler("start", CommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("about", CommandHandlers.about_command))
    telegram_app.add_handler(CommandHandler("help", CommandHandlers.help_command))
    telegram_app.add_handler(CommandHandler("mystories", CommandHandlers.mystories_command))
    telegram_app.add_handler(CommandHandler("export", CommandHandlers.export_command))
    telegram_app.add_handler(CommandHandler("reminders", CommandHandlers.reminders_command))
    telegram_app.add_handler(MessageHandler(filters.COMMAND, CommandHandlers.unknown_command))
    telegram_app.add_error_handler(CommandHandlers.error_handler)
    
    # Set up job queue for reminders (check every minute)
    job_queue = telegram_app.job_queue
    job_queue.run_repeating(check_and_send_reminders, interval=60, first=10)
    
    # Register bot commands with Telegram
    async def post_init(application: Application) -> None:
        """Set bot commands after initialization."""
        commands = [
            BotCommand("start", "Welcome message"),
            BotCommand("help", "Show help message"),
            BotCommand("story", "Record today's moment"),
            BotCommand("mystories", "View your stories"),
            BotCommand("reminders", "⏰ Manage daily reminders"),
            BotCommand("about", "Learn about Homework for Life"),
            BotCommand("export", "Export all stories"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands registered with Telegram")
    
    telegram_app.post_init = post_init
    
    print("🚀 Bot running. Press Ctrl+C to stop.")
    print("⏰ Reminder system activated - checking every minute.")
    
    try:
        telegram_app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

if __name__ == '__main__':
    main()