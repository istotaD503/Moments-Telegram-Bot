"""
Shared resources for all handler modules
"""
import logging
import random
from datetime import time as datetime_time

import pytz
from telegram.ext import CallbackContext

from models.story import StoryDatabase

logger = logging.getLogger(__name__)

# Single shared database instance used by all handlers
story_db = StoryDatabase()

# Conversation states
WAITING_FOR_STORY = 1
WAITING_FOR_REMINDER_TIME = 2
WAITING_FOR_TIMEZONE = 3
WAITING_FOR_FEEDBACK = 10


# --- Reminder messages ---

_REMINDER_TEMPLATES = [
    (
        "Hey {name}.\n\n"
        "What moment from today would make a good five-minute story?\n\n"
        "It doesn't have to be dramatic. A brief exchange, a small decision, a detail that stuck — any of it counts.\n\n"
        "What's yours? 📝"
    ),
    (
        "Hey {name}.\n\n"
        "Something happened today. It may have already slipped past you — but something lingered a little longer than the rest.\n\n"
        "What was it?"
    ),
    (
        "{name} — before the day fully fades:\n\n"
        "What did you see, hear, or feel today that briefly stopped you?\n\n"
        "Even for half a second. That's the one."
    ),
    (
        "Hey {name}.\n\n"
        "Think back through your day. Was there a moment — a pause, a walk, a meal, a conversation that ended — "
        "where something small felt just a little bigger than expected?\n\n"
        "Capture it before it's gone. 📝"
    ),
    (
        "Hey {name}!\n\n"
        "If someone asked you tomorrow what happened today, what would you actually tell them?\n\n"
        "Not the summary. The moment.\n\n"
        "Write it down while it's still fresh."
    ),
    (
        "Hey {name}.\n\n"
        "Today probably wasn't a movie. That's fine — the best material usually isn't.\n\n"
        "What was the quiet thing that happened anyway?"
    ),
    (
        "Hey {name}.\n\n"
        "You were somewhere today that you won't be in exactly that way again. What did you notice?\n\n"
        "Even something small counts. Especially something small."
    ),
    (
        "Hey {name}.\n\n"
        "Did anything catch you off guard today?\n\n"
        "A reaction you didn't expect from yourself. A moment that went sideways, or better than it should have. "
        "A tiny thing that felt oddly meaningful.\n\n"
        "That's your story."
    ),
    (
        "Hey {name}.\n\n"
        "Most of today is already fading. Before it fully goes —\n\n"
        "What moment do you keep coming back to?"
    ),
    (
        "Hey {name}.\n\n"
        "One question: if your day were a story, what would happen in it?\n\n"
        "Not everything. Just the moment that would make someone lean in."
    ),
]


async def send_reminder_to_user(context: CallbackContext, user_id: int, first_name: str = None) -> None:
    """
    Send a reminder message to a specific user.
    """
    if not first_name:
        first_name = "there"

    context.application.user_data[user_id]['awaiting_story'] = True
    reminder_message = random.choice(_REMINDER_TEMPLATES).format(name=first_name)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=reminder_message,
            parse_mode='HTML',
        )
        logger.info(f"Reminder sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send reminder to user {user_id}: {e}")


# --- Job queue scheduling helpers ---

async def daily_reminder_callback(context: CallbackContext) -> None:
    """
    Callback fired by APScheduler's run_daily for each user's reminder.
    """
    try:
        job_name = context.job.name
        user_id = int(job_name.split("_")[1])

        stories = story_db.get_user_stories(user_id, limit=1)
        first_name = stories[0]['first_name'] if stories and stories[0]['first_name'] else None

        await send_reminder_to_user(context, user_id, first_name)
    except Exception as e:
        logger.error(f"Error in daily_reminder_callback: {e}")


def schedule_reminder_job(job_queue, user_id: int, reminder_time_str: str, timezone_str: str) -> None:
    """
    Schedule a daily run_daily job for a user's reminder.
    Cancels any existing job for this user first.
    """
    cancel_reminder_job(job_queue, user_id)

    hour, minute = map(int, reminder_time_str.split(':'))
    reminder_time = datetime_time(hour=hour, minute=minute, tzinfo=pytz.UTC)

    job_queue.run_daily(
        daily_reminder_callback,
        time=reminder_time,
        name=f"reminder_{user_id}",
    )
    logger.info(f"Scheduled daily reminder for user {user_id} at {reminder_time_str} ({timezone_str})")


def cancel_reminder_job(job_queue, user_id: int) -> None:
    """
    Cancel a user's scheduled reminder job if one exists.
    """
    jobs = job_queue.get_jobs_by_name(f"reminder_{user_id}")
    for job in jobs:
        job.schedule_removal()
    if jobs:
        logger.info(f"Cancelled reminder job for user {user_id}")


def schedule_all_reminders(job_queue) -> int:
    """
    Load all active reminders from DB and schedule run_daily jobs for each.
    Called on bot startup.
    Returns the number of reminders scheduled.
    """
    reminders = story_db.get_all_active_reminders()
    for reminder in reminders:
        schedule_reminder_job(
            job_queue,
            reminder['user_id'],
            reminder['reminder_time'],
            reminder['timezone'],
        )
    return len(reminders)
