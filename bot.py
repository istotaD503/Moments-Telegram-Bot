#!/usr/bin/env python3
"""
Telegram Bot for capturing daily storyworthy moments
"""

import logging
import sys
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler

from config.settings import settings
from handlers import (
    BasicCommandHandlers,
    StoryCommandHandlers,
    ReminderCommandHandlers,
    ReportCommandHandlers,
    quick_action_router,
    WAITING_FOR_STORY,
    WAITING_FOR_REMINDER_TIME,
    WAITING_FOR_TIMEZONE,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Reduced from INFO to save memory
)

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Set bot commands and schedule reminders after initialization."""
    commands = [
        BotCommand("story", "📝 Record today's moment"),
        BotCommand("mystories", "📚 Your stats + export"),
        BotCommand("report", "🧠 AI story report"),
        BotCommand("reminders", "⏰ Manage daily reminders"),
        BotCommand("help", "❓ Commands list"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered with Telegram")

    from handlers.shared import schedule_all_reminders
    count = schedule_all_reminders(application.job_queue)
    logger.info(f"Scheduled {count} daily reminder(s)")


def main():
    """Main function to run the Telegram bot"""
    if not settings.validate():
        print("Please set BOT_TOKEN environment variable")
        sys.exit(1)

    print("🤖 Starting Bot...")
    telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

    # Quick action conversation handler (from /start inline buttons)
    quick_action_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(quick_action_router, pattern="^quick:")],
        states={
            WAITING_FOR_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, StoryCommandHandlers.receive_story)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", StoryCommandHandlers.cancel_story),
            CallbackQueryHandler(StoryCommandHandlers.cancel_story_callback, pattern="^cancel:story")
        ]
    )
    telegram_app.add_handler(quick_action_conversation)

    # Story command with conversation handler
    story_conversation = ConversationHandler(
        entry_points=[CommandHandler("story", StoryCommandHandlers.story_command)],
        states={
            WAITING_FOR_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, StoryCommandHandlers.receive_story)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", StoryCommandHandlers.cancel_story),
            CallbackQueryHandler(StoryCommandHandlers.cancel_story_callback, pattern="^cancel:story")
        ]
    )
    telegram_app.add_handler(story_conversation)
    
    # Reminder setup conversation handler
    reminder_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("setreminder", ReminderCommandHandlers.setreminder_command),
            CallbackQueryHandler(ReminderCommandHandlers.reminder_menu_callback, pattern="^reminder:")
        ],
        states={
            WAITING_FOR_TIMEZONE: [
                CallbackQueryHandler(ReminderCommandHandlers.timezone_button_callback, pattern="^tz:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ReminderCommandHandlers.receive_timezone)
            ],
            WAITING_FOR_REMINDER_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ReminderCommandHandlers.receive_reminder_time)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", ReminderCommandHandlers.cancel_reminder),
            CallbackQueryHandler(ReminderCommandHandlers.cancel_reminder_callback, pattern="^cancel:reminder")
        ]
    )
    telegram_app.add_handler(reminder_conversation)
    
    # Other commands
    telegram_app.add_handler(CommandHandler("start", BasicCommandHandlers.start_command))
    telegram_app.add_handler(CommandHandler("about", BasicCommandHandlers.about_command))
    telegram_app.add_handler(CommandHandler("help", BasicCommandHandlers.help_command))
    telegram_app.add_handler(CommandHandler("mystories", StoryCommandHandlers.mystories_command))
    telegram_app.add_handler(CommandHandler("export", StoryCommandHandlers.export_command))
    telegram_app.add_handler(CommandHandler("reminders", ReminderCommandHandlers.reminders_command))
    telegram_app.add_handler(CommandHandler("report", ReportCommandHandlers.report_command))
    telegram_app.add_handler(CallbackQueryHandler(ReportCommandHandlers.report_all_callback, pattern="^report:all$"))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, StoryCommandHandlers.receive_story_after_reminder))
    telegram_app.add_handler(MessageHandler(filters.COMMAND, BasicCommandHandlers.unknown_command))
    telegram_app.add_error_handler(BasicCommandHandlers.error_handler)
    
    telegram_app.post_init = post_init
    
    print("🚀 Bot running. Press Ctrl+C to stop.")
    print("⏰ Reminder system activated - daily jobs loaded.")
    
    try:
        telegram_app.run_polling(poll_interval=1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

if __name__ == '__main__':
    main()