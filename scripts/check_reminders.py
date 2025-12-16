#!/usr/bin/env python3
"""
Helper script to test reminders and show current UTC time
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import from models
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.story import StoryDatabase

def show_current_time():
    """Display current UTC time and suggest test times"""
    now = datetime.utcnow()
    current_time = now.strftime('%H:%M')
    
    # Suggest times 1, 2, and 3 minutes from now
    test_times = []
    for minutes in [1, 2, 3]:
        future_time = now + timedelta(minutes=minutes)
        test_times.append(future_time.strftime('%H:%M'))
    
    print("⏰ Current UTC Time:", current_time)
    print("\n📝 Suggested test times (1-3 minutes from now):")
    for i, time_str in enumerate(test_times, 1):
        print(f"   {i}. {time_str}")
    print()

def list_active_reminders():
    """List all active reminders in the database"""
    db = StoryDatabase()
    reminders = db.get_all_active_reminders()
    
    if not reminders:
        print("📭 No active reminders found")
        return
    
    print(f"📋 Active Reminders ({len(reminders)} total):\n")
    for reminder in reminders:
        user_id = reminder['user_id']
        time_str = reminder['reminder_time']
        status = "✅ Enabled" if reminder['enabled'] else "🔕 Disabled"
        print(f"   User {user_id}: {time_str} UTC - {status}")
    print()

def show_user_reminder(user_id):
    """Show reminder preference for a specific user"""
    db = StoryDatabase()
    reminder = db.get_reminder_preference(user_id)
    
    if not reminder:
        print(f"❌ No reminder found for user {user_id}")
        return
    
    status = "✅ Enabled" if reminder['enabled'] else "🔕 Disabled"
    print(f"\n📝 Reminder for User {user_id}:")
    print(f"   Time: {reminder['reminder_time']} UTC")
    print(f"   Timezone: {reminder['timezone']}")
    print(f"   Status: {status}")
    print(f"   Created: {reminder['created_at']}")
    print(f"   Updated: {reminder['updated_at']}\n")

def main():
    """Main function"""
    print("\n" + "="*50)
    print("🤖 Moments Bot - Reminder Testing Helper")
    print("="*50 + "\n")
    
    show_current_time()
    list_active_reminders()
    
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
            show_user_reminder(user_id)
        except ValueError:
            print("❌ Invalid user ID. Usage: python check_reminders.py [user_id]")

if __name__ == '__main__':
    main()
