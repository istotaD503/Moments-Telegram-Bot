# Timezone-Aware Reminder System

## Overview
The reminder system now supports **timezone-aware scheduling**! Users can set their reminder time in their **local timezone**, and the bot automatically handles the conversion to UTC for storage and scheduling.

## How It Works

### User Flow
1. User runs `/setreminder`
2. Bot asks for timezone (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`)
3. Bot validates timezone and shows current time in that timezone
4. Bot asks for reminder time in **local time** (HH:MM format)
5. Bot converts local time to UTC and stores it
6. User sees confirmation with their local time

### Example
```
User in New York (EST/EDT):
- Timezone: America/New_York
- Desired reminder: 09:00 (9 AM local)
- Stored in DB: 14:00 UTC (or 13:00 UTC depending on DST)
- User sees: "Reminder set for 09:00 (America/New_York)"
```

## Database Schema
The `reminder_preferences` table stores:
- `user_id`: Telegram user ID
- `reminder_time`: Time in **UTC** (HH:MM format)
- `timezone`: User's timezone string (e.g., `America/Los_Angeles`)
- `enabled`: Whether reminder is active

## Commands

### `/setreminder`
Two-step conversation:
1. **Step 1:** Enter timezone
   - Examples: `America/New_York`, `Europe/Paris`, `Asia/Tokyo`
   - Bot validates and shows current time in that zone
2. **Step 2:** Enter time in local timezone
   - Format: HH:MM (24-hour)
   - Bot converts to UTC and saves

### `/myreminder`
Shows reminder status with time in **user's local timezone**:
- Status (Active/Stopped)
- Time in local timezone
- Timezone name

### `/stopreminder`
Disables the reminder (doesn't delete it)

## Technical Details

### Dependencies
- `pytz==2024.1` - Timezone handling and conversion

### Key Functions

**Timezone Validation:**
```python
try:
    tz = pytz.timezone(timezone_text)  # Validates timezone
    # timezone_text examples: "America/New_York", "Europe/London"
except pytz.exceptions.UnknownTimeZoneError:
    # Invalid timezone
```

**Local to UTC Conversion:**
```python
user_tz = pytz.timezone(timezone_str)
hour, minute = map(int, time_text.split(':'))
now = datetime.now(user_tz)
local_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
utc_time = local_time.astimezone(pytz.UTC)
utc_time_str = utc_time.strftime('%H:%M')
```

**UTC to Local Display:**
```python
user_tz = pytz.timezone(timezone_str)
hour, minute = map(int, utc_time_str.split(':'))
utc_now = datetime.now(pytz.UTC)
utc_time = utc_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
local_time = utc_time.astimezone(user_tz)
local_time_str = local_time.strftime('%H:%M')
```

### Job Scheduler
The scheduler still runs on UTC:
- Checks reminders every minute
- Compares current UTC time with stored UTC times
- When match found, sends reminder to user

## Common Timezones

**Americas:**
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `America/Toronto` - Toronto
- `America/Mexico_City` - Mexico City

**Europe:**
- `Europe/London` - UK
- `Europe/Paris` - Central European
- `Europe/Berlin` - Germany
- `Europe/Moscow` - Moscow
- `Europe/Istanbul` - Turkey

**Asia:**
- `Asia/Tokyo` - Japan
- `Asia/Shanghai` - China
- `Asia/Dubai` - UAE
- `Asia/Kolkata` - India
- `Asia/Singapore` - Singapore

**Oceania:**
- `Australia/Sydney` - Sydney
- `Australia/Melbourne` - Melbourne
- `Pacific/Auckland` - New Zealand

**Full list:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Testing

### Test Timezone Conversion
1. Set reminder for a different timezone
2. Use `/myreminder` to verify time shows in local timezone
3. Check database to confirm UTC storage

### Test Reminder Delivery
1. Set reminder for 1-2 minutes from now in your timezone
2. Wait for scheduled time
3. Confirm reminder arrives at correct local time

### Test Timezone Edge Cases
- Test with DST-observing timezones
- Test with non-DST timezones
- Test with offsets (not recommended, use named timezones)

## Conversation State Flow

```
/setreminder
    ↓
WAITING_FOR_TIMEZONE (State 3)
    ↓ (user enters timezone)
receive_timezone() validates & stores in context.user_data
    ↓
WAITING_FOR_REMINDER_TIME (State 2)
    ↓ (user enters time)
receive_reminder_time() converts to UTC & saves
    ↓
ConversationHandler.END
```

## Error Handling

- **Invalid timezone:** Shows examples, stays in WAITING_FOR_TIMEZONE
- **Invalid time format:** Shows examples, stays in WAITING_FOR_REMINDER_TIME
- **Database error:** Shows error message, ends conversation
- **Conversion error:** Falls back to showing UTC time

## Migration Notes

**Existing reminders (if any):**
- Old reminders stored with `timezone='UTC'`
- Will display as UTC until user runs `/setreminder` again
- No data loss, fully backward compatible

## Future Enhancements

Potential improvements:
- Auto-detect timezone from Telegram user settings
- Support for multiple reminders per day
- Daylight Saving Time notifications
- Timezone abbreviations (EST, PST) support
- "Smart" time input (e.g., "9am", "2:30pm")
