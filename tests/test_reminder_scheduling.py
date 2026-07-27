"""
Unit tests for reminder scheduling helpers in handlers/shared.py.
No Telegram bot token required.
"""
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def make_mock_job_queue():
    """Create a mock job queue that tracks scheduled jobs."""
    jobs = {}

    def run_daily(callback, time, name):
        job = MagicMock()
        job.name = name
        job.callback = callback
        job.time = time

        def remove():
            jobs.pop(name, None)
        job.schedule_removal = MagicMock(side_effect=remove)
        jobs[name] = job
        return job

    jq = MagicMock()
    jq.run_daily = MagicMock(side_effect=run_daily)
    jq.get_jobs_by_name = MagicMock(side_effect=lambda name: [jobs[name]] if name in jobs else [])
    jq._jobs = jobs
    return jq


def test_schedule_reminder_job():
    from handlers.shared import schedule_reminder_job
    import pytz

    jq = make_mock_job_queue()
    schedule_reminder_job(jq, user_id=12345, reminder_time_str="14:30", timezone_str="UTC")

    jq.run_daily.assert_called_once()
    call_args = jq.run_daily.call_args
    assert call_args.kwargs["name"] == "reminder_12345"
    t = call_args.kwargs["time"]
    assert t.hour == 14
    assert t.minute == 30
    assert t.tzinfo is not None

    print("  PASS  schedule_reminder_job creates correct job")


def test_schedule_reminder_job_cancels_existing():
    from handlers.shared import schedule_reminder_job

    jq = make_mock_job_queue()
    schedule_reminder_job(jq, user_id=12345, reminder_time_str="14:30", timezone_str="UTC")
    old_job = jq._jobs["reminder_12345"]

    schedule_reminder_job(jq, user_id=12345, reminder_time_str="09:00", timezone_str="UTC")

    old_job.schedule_removal.assert_called_once()
    new_job = jq._jobs["reminder_12345"]
    assert new_job.time.hour == 9
    assert new_job.time.minute == 0

    print("  PASS  schedule_reminder_job replaces existing job")


def test_cancel_reminder_job():
    from handlers.shared import cancel_reminder_job, schedule_reminder_job

    jq = make_mock_job_queue()
    schedule_reminder_job(jq, user_id=12345, reminder_time_str="14:30", timezone_str="UTC")
    job = jq._jobs["reminder_12345"]

    cancel_reminder_job(jq, user_id=12345)

    job.schedule_removal.assert_called_once()
    assert "reminder_12345" not in jq._jobs

    print("  PASS  cancel_reminder_job removes job")


def test_cancel_reminder_job_noop():
    from handlers.shared import cancel_reminder_job

    jq = make_mock_job_queue()
    cancel_reminder_job(jq, user_id=99999)

    print("  PASS  cancel_reminder_job is safe when no job exists")


def test_schedule_all_reminders():
    from handlers.shared import schedule_all_reminders

    jq = make_mock_job_queue()
    mock_reminders = [
        {"user_id": 1, "reminder_time": "09:00", "timezone": "UTC"},
        {"user_id": 2, "reminder_time": "18:30", "timezone": "America/New_York"},
    ]

    with patch("handlers.shared.story_db") as mock_db:
        mock_db.get_all_active_reminders.return_value = mock_reminders
        count = schedule_all_reminders(jq)

    assert count == 2
    assert "reminder_1" in jq._jobs
    assert "reminder_2" in jq._jobs
    assert jq._jobs["reminder_1"].time.hour == 9
    assert jq._jobs["reminder_1"].time.minute == 0
    assert jq._jobs["reminder_2"].time.hour == 18
    assert jq._jobs["reminder_2"].time.minute == 30

    print("  PASS  schedule_all_reminders loads and schedules from DB")


def test_daily_reminder_callback():
    from handlers.shared import daily_reminder_callback

    context = MagicMock()
    context.job.name = "reminder_42"
    context.application.user_data = {42: {}}
    context.bot.send_message = AsyncMock()

    mock_stories = [{"first_name": "Alice"}]

    with patch("handlers.shared.story_db") as mock_db:
        mock_db.get_user_stories.return_value = mock_stories
        with patch("handlers.shared.send_reminder_to_user", new_callable=AsyncMock) as mock_send:
            import asyncio
            asyncio.run(daily_reminder_callback(context))

            mock_send.assert_called_once_with(context, 42, "Alice")

    print("  PASS  daily_reminder_callback extracts user_id and looks up name")


def test_daily_reminder_callback_no_name():
    from handlers.shared import daily_reminder_callback

    context = MagicMock()
    context.job.name = "reminder_99"
    context.application.user_data = {99: {}}
    context.bot.send_message = AsyncMock()

    with patch("handlers.shared.story_db") as mock_db:
        mock_db.get_user_stories.return_value = []
        with patch("handlers.shared.send_reminder_to_user", new_callable=AsyncMock) as mock_send:
            import asyncio
            asyncio.run(daily_reminder_callback(context))

            mock_send.assert_called_once_with(context, 99, None)

    print("  PASS  daily_reminder_callback handles missing name gracefully")


def test_timezone_parsing():
    from handlers.shared import schedule_reminder_job
    import pytz

    jq = make_mock_job_queue()
    schedule_reminder_job(jq, user_id=1, reminder_time_str="09:00", timezone_str="America/New_York")

    call_args = jq.run_daily.call_args
    t = call_args.kwargs["time"]
    assert t.hour == 9
    assert t.minute == 0
    assert t.tzinfo == pytz.UTC

    print("  PASS  scheduling uses UTC (DB stores UTC time)")


if __name__ == "__main__":
    print("Running reminder scheduling tests...\n")
    test_schedule_reminder_job()
    test_schedule_reminder_job_cancels_existing()
    test_cancel_reminder_job()
    test_cancel_reminder_job_noop()
    test_schedule_all_reminders()
    test_daily_reminder_callback()
    test_daily_reminder_callback_no_name()
    test_timezone_parsing()
    print("\nAll tests passed.")
