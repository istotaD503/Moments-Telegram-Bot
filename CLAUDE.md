# CLAUDE.md — Moments Bot

## Project Purpose

Moments Bot is a Telegram bot for capturing daily storyworthy moments, inspired by Matthew Dicks' Homework for Life practice.

## Tech Stack

- **Language:** Python 3.9+
- **Framework:** `python-telegram-bot` v22.5 (polling mode, job queue)
- **Database:** SQLite via `models/story.py` (`StoryDatabase`)
- **Deployment:** Docker on Fly.io
- **Config:** python-dotenv

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

**Required env vars** (in `.env`):
- `BOT_TOKEN` — Telegram bot token

**Optional:**
- `DB_DIR` — defaults to `data/`; on Fly.io, set to the mounted volume path

## Architecture

- **`bot.py`** — entry point: wires handlers, registers conversation state machines, starts job queue
- **`handlers/`** — feature-based command handlers:
  - `basic_commands.py` — `/start`, `/help`, `/about`, unknown command fallback, error handler
  - `story_commands.py` — `/story`, `/mystories`, `/export`
  - `reminder_commands.py` — `/setreminder`, `/reminders`, timezone/time parsing
  - `feedback_commands.py` — `/feedback`
  - `quick_actions.py` — inline button callback router
  - `shared.py` — shared DB instance and UI helpers
- **`models/story.py`** — `StoryDatabase` class; tables: `stories`, `reminder_preferences`, `feedback`
- **`config/settings.py`** — loads and validates environment config
- **`utils/assets.py` + `assets/*.txt`** — message templates
- **Job queue** — runs `check_and_send_reminders()` every 60 seconds

## Coding Rules

1. **Conversation state** — keep `ConversationHandler` states explicit; no catch-all text handler that would intercept conversation input
2. **Handler order** — `ConversationHandler`s registered before generic fallbacks; `unknown_command` stays near the end
3. **Async** — all Telegram handlers are `async`; always `await` API calls
4. **Database** — put persistence changes in `StoryDatabase` methods, not inline SQL in handlers; preserve schema compatibility unless migration is explicitly requested
5. **New commands** — wire in `bot.py`, implement in the relevant `handlers/*_commands.py`, update help text
6. **Formatting** — use `parse_mode='HTML'` consistently; keep story prompts concise and aligned with Homework for Life framing
7. **Logging** — use `logger = logging.getLogger(__name__)` per module
8. **Minimal diffs** — avoid unrelated refactors; don't change deployment config unless asked

## Secret Handling

- Never print or log `BOT_TOKEN` or any secret value
- Keep `.env` local and uncommitted; use `.env.example` with placeholders
- If a secret is exposed, instruct immediate rotation

## Validation (No Automated Tests)

Manually verify after changes:
1. Full conversation flow: start → input → cancel/complete
2. Database writes/reads in the relevant table
3. Unknown command and error handler behavior
4. Reminder checks still run without exceptions

## Out-of-Scope Defaults

- No webhooks or server frameworks unless explicitly requested
- No new storage backends by default
- No changes to Fly.io deployment config unless requested
