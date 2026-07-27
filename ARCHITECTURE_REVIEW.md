# Architecture Review — Moments Bot

The overall structure is clean and well-organized. The handler/model separation is solid. Below are the real issues, ranked by impact.

---

## Critical

**1. ~~Duplicate reminder delivery~~ FIXED (2026-07-27)** — Replaced 60s polling loop with per-user `run_daily` jobs via APScheduler. Each user gets a named job (`reminder_{user_id}`) scheduled at their reminder time. No string comparison, no duplicate risk. See `handlers/shared.py`.

**2. ~~New DB instance every 60 seconds~~ FIXED (2026-07-27)** — Eliminated entirely. The polling loop that created a fresh `StoryDatabase()` on every tick no longer exists. All handlers use the shared `story_db` instance from `handlers/shared.py`.

**3. ~~DST / timezone display bug~~ Partially fixed (2026-07-27)** — The scheduling bug (UTC time treated as local time) was fixed: `schedule_reminder_job` now always schedules in UTC since the DB stores UTC time. The display bug (date mismatch from `utc_now.replace()`) and DST shift on transitions remain open.

---

## High

**4. Tempfile orphan accumulation** — `story_commands.py` creates export tempfiles with `delete=False`. A crash between creation and send leaves orphaned files. No cleanup job exists. Long-running on Fly.io will eventually fill the volume.

**5. ~~No exception handling in the job queue~~ FIXED (2026-07-27)** — `daily_reminder_callback` in `handlers/shared.py` wraps the entire body in `try/except Exception` with logging. Failures no longer crash silently.

**6. Export has no pagination** — `story_commands.py` loads ALL user stories into memory for export. Power users with years of daily entries will cause a spike. Needs streaming or chunked export.

---

## Medium

**7. Bare `except:` clauses** — Several places in `reminder_commands.py` use bare `except:`, catching `SystemExit` and `KeyboardInterrupt`. Should be `except Exception`.

**8. LIMIT string interpolation in SQL** — `models/story.py` does `query += f" LIMIT {limit}"`. The limit comes from code today, but it should be passed as a bound parameter. Low risk now, but bad pattern.

**9. No index on `reminder_preferences.enabled`** — Every reminder check does a full table scan on `WHERE enabled = 1`. Fine now, significant at scale. Add a composite index on `(enabled, reminder_time)`.

**10. Duplicate timezone keyboard definitions** — The same `InlineKeyboardMarkup` is copy-pasted 3+ times in `reminder_commands.py`. Single source of truth, please.

**11. Dockerfile runs as root, no HEALTHCHECK** — Security risk + Fly.io can't detect a crashed process. Add a non-root user and `HEALTHCHECK`.

---

## Low

**12. Asset files read from disk every call** — `utils/assets.py` reads `about_message.txt` on every `/about` command. Cache at import time.

**13. Unused HTTP service in fly.toml** — `fly.toml` defines an `[http_service]` block, but the bot uses polling and has no HTTP server. Remove it.

**14. Feedback logs PII** — `feedback_commands.py` logs the first 50 chars of feedback content. Log receipt only, not content.

**15. Export filename not sanitized** — `user.first_name` goes directly into the tempfile name. A name like `../../etc/passwd` is theoretically problematic. Sanitize with `re.sub(r'[^a-zA-Z0-9_-]', '_', ...)`.

**16. PTBUserWarning: If 'per_message=False', 'CallbackQueryHandler' will not be tracked for every message. Read this FAQ entry to learn more about the per_* settings: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-Asked-Questions#what-do-the-per_-settings-in-conversationhandler-do.
  reminder_conversation = ConversationHandler(

---

## Suggested Fix Order

| # | File | Fix | Status |
|---|------|-----|--------|
| 1 | `bot.py` | Add `sent_at` tracking to prevent duplicate reminders in same minute | **Done** — replaced polling with `run_daily` |
| 2 | `bot.py` | Pass shared `story_db` into `check_and_send_reminders` instead of instantiating | **Done** — polling loop removed entirely |
| 3 | `handlers/reminder_commands.py` | Fix DST: store user's timezone string in DB alongside UTC time, recalculate on trigger | **Partially done** — scheduling fixed (UTC), display bug remains |
| 4 | `bot.py` | Wrap job queue callback in `try/except Exception` | **Done** — in `shared.py:daily_reminder_callback` |
| 5 | `handlers/story_commands.py` | Add tempfile cleanup + export streaming | Pending |
| 6 | `models/story.py` | Parameterize LIMIT, add index on reminder_preferences | Pending |
| 7 | `Dockerfile` | Add non-root user + HEALTHCHECK | Pending |

The biggest bang-for-buck fixes are #1–4 — they directly affect correctness and reliability of the core feature (reminders).

---

## Production Readiness (2026-07-24)

### Architecture Validation

The following architectural decisions were reviewed and confirmed appropriate
for the current scale (single user / small group):

- **Single instance**: Telegram's `getUpdates` API only supports one active
  polling session per bot token. Multi-instance would cause duplicate update
  processing.
- **SQLite + persistent volume**: Sufficient for single instance. Volume
  `moments_data` mounted at `/data` in `fly.toml`.
- **Polling mode**: Simpler than webhooks for single instance. No need to
  manage webhook URLs, certificates, or HTTPS.
- **Single process**: `asyncio` handles concurrency. Reminders are now
  event-driven (`run_daily` jobs) rather than polled, so there is no
  periodic check that could block Telegram update handling.

### Not Needed (for current scale)

- Turso / Postgres (data silos only matter with multiple instances)
- Redis + Celery (job duplication only happens with multiple instances)
- Webhook migration
- Process splitting

### GDPR / Privacy Compliance

| Requirement | Status | Notes |
|---|---|---|
| `/deleteaccount` command | **Missing** | Users must be able to request data deletion |
| Privacy policy | **Missing** | Required for GDPR, Reddit ads |
| Stop logging PII | **Missing** | Architecture review #14: feedback logs content |
| Encrypt `story_text` | **Missing** | Protect personal stories at rest (Fernet recommended) |
| `/export` (data portability) | **Implemented** | `story_commands.py` |

### Dev / Prod Environments

Currently single Fly.io app (`moments-bot`). To test without stopping prod:

1. Create separate bot token via BotFather (`@YourMomentsBotDev`)
2. Create `fly.dev.toml` with `app = 'moments-bot-dev'`
3. Add `[[mounts]]` with `source = 'moments_data_dev'`
4. Update GitHub Actions to deploy both apps

### DB Backups

Current state: No automated backups. `scripts/upload-db.sh` handles upload
only.

Recommended: Add `scripts/backup-db.sh` that downloads DB via SFTP:
```bash
fly ssh sftp get /data/stories.db ./backups/stories_$(date +%Y%m%d).db
```

Run via local cron or Fly.io scheduled Machine.

### Production Launch Checklist

Before Reddit advertisement:

1. ~~Fix critical bugs (architecture review #1-5)~~ **Partially done** — #1, #2, #5 fixed (2026-07-27). #3 (DST) still open.
2. Add `/deleteaccount` command
3. Add privacy policy (link in `/about`)
4. Stop logging PII (#14)
5. Add error tracking (Sentry free tier)
6. Create landing page (Carrd or similar)
7. Set up DB backup script
8. Create dev Fly.io app for testing
