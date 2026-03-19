# Copilot Instructions - Moments Bot

## Project Purpose

Moments Bot is a Telegram bot for capturing daily storyworthy moments inspired by Matthew Dicks' Homework for Life practice.

## Architecture Overview

- Runtime entrypoint is `bot.py`, using `python-telegram-bot` polling mode.
- The bot registers multiple `ConversationHandler` flows plus standard command handlers.
- Reminder delivery runs via `Application.job_queue` (`run_repeating`) and checks reminders every minute.
- Persistence is SQLite through `models/story.py` (`StoryDatabase`).

## Source of Truth Files

- `bot.py`: handler wiring, conversation state machines, bot command registration, reminder scheduler.
- `handlers/basic_commands.py`: `/start`, `/help`, `/about`, unknown command fallback, shared error handler.
- `handlers/story_commands.py`: `/story`, `/mystories`, `/export`, story conversation flow.
- `handlers/reminder_commands.py`: reminder setup/manage flow and timezone/time parsing.
- `handlers/feedback_commands.py`: `/feedback` conversation flow.
- `handlers/quick_actions.py`: callback router for inline quick actions.
- `handlers/shared.py`: shared UI helpers/constants used across handlers.
- `models/story.py`: story/reminder/feedback schema and data access methods.
- `config/settings.py`: environment config (`BOT_TOKEN`) and validation.
- `utils/assets.py` and `assets/*.txt`: message templates.

## Critical Implementation Rules

1. Respect conversation state boundaries
- Keep `ConversationHandler` states explicit.
- Do not add a catch-all text handler that would intercept conversation input.

2. Keep handler registration order stable
- `ConversationHandler`s should remain registered before generic command fallbacks.
- `MessageHandler(filters.COMMAND, BasicCommandHandlers.unknown_command)` must stay near the end.

3. Use async handler style consistently
- Telegram handlers are async and must `await` Telegram API calls.

4. Reuse the existing database abstraction
- Put persistence changes in `StoryDatabase` methods rather than inline SQL in handlers.
- Preserve existing schema compatibility unless explicitly asked to migrate.

5. Maintain UX tone
- Story-related prompts should stay concise, encouraging, and aligned with Homework for Life framing.

## Data and Storage Notes

- Default DB path is `data/stories.db` locally.
- If `DB_DIR` is set (e.g., Fly volume), database file becomes `${DB_DIR}/stories.db`.
- Current tables: `stories`, `reminder_preferences`, `feedback`.

## Environment and Local Run

Required env:
- `BOT_TOKEN` (required)

Optional env:
- `DB_DIR` (defaults to `data`)

Local setup:
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python bot.py`

## Copilot Coding Preferences for This Repo

- Make focused, minimal diffs; avoid unrelated refactors.
- Follow existing module split under `handlers/` (feature-based files).
- Add logging with `logger = logging.getLogger(__name__)` where useful.
- Keep Telegram formatting consistent (`parse_mode='HTML'` where existing handlers use it).
- If adding a new command, wire it in `bot.py`, implement handler in the relevant `handlers/*_commands.py`, and update user-facing help text.

## Secret Handling Rules

- Never ask users to paste full secret values in chat.
- Never print or echo token/key values from `.env`, logs, or runtime output.
- Use environment variable names only (for example `BOT_TOKEN`, `OPENAI_API_KEY`) when discussing configuration.
- Keep `.env` local-only and uncommitted; use `.env.example` with placeholder values for sharing.
- If a secret is exposed in chat or logs, instruct immediate key rotation and replacement.

## Manual Validation Checklist

Because there is no formal test suite yet, validate changes by running the bot and checking:
1. Conversation start to input to cancel/complete behavior.
2. Database writes/reads in `stories`, `reminder_preferences`, or `feedback` as applicable.
3. Unknown command and error handling behavior.
4. Reminder checks still run without exceptions.

## Out-of-Scope Defaults

- Do not add webhook/server frameworks unless explicitly requested.
- Do not introduce new storage backends by default.
- Do not change deployment targets unless requested (Fly config currently exists in repo).