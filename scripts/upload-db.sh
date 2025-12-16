#!/bin/bash
# filepath: upload_db.sh

APP_NAME="moments-bot"
LOCAL_DB="./data/remote-stories.db"

echo "📦 Uploading database to Fly.io..."

# 1. Delete existing file
echo "🗑️  Deleting old database..."
fly ssh console -a $APP_NAME -C "rm -f /data/stories.db"

# 2. Verify deletion
echo "🔍 Verifying deletion..."
RESULT=$(fly ssh console -a $APP_NAME -C "ls /data/stories.db" 2>&1)
if echo "$RESULT" | grep -q "No such file"; then
    echo "✅ Old file deleted"
else
    echo "❌ Failed to delete old file"
    exit 1
fi

# 3. Upload new file
echo "⬆️  Uploading new database..."
fly ssh sftp put $LOCAL_DB /data/stories.db -a $APP_NAME

# 4. Verify upload
echo "🔍 Verifying upload..."
fly ssh console -a $APP_NAME -C "python3 -c \"
import sqlite3, os
from pathlib import Path

db_path = Path(os.getenv('DB_DIR', 'data')) / 'stories.db'

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    stories = conn.execute('SELECT COUNT(*) FROM stories').fetchone()[0]
    feedback = conn.execute('SELECT COUNT(*) FROM feedback').fetchone()[0]
    reminders = conn.execute('SELECT COUNT(*) FROM reminder_preferences WHERE enabled=1').fetchone()[0]
    conn.close()
    
    print(f'✅ Database uploaded successfully!')
    print(f'   Stories: {stories}')
    print(f'   Feedback: {feedback}')
    print(f'   Active Reminders: {reminders}')
else:
    print('❌ Upload failed - file not found')
    exit(1)
\""

# 5. Restart bot
echo "🔄 Restarting bot..."
fly apps restart $APP_NAME

echo "✅ Upload complete!"