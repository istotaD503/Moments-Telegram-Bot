"""
Story model for storing user's storyworthy moments
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StoryDatabase:
    """Manage story storage in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use /data for Fly.io persistent volume, fall back to local for development
            db_dir = os.getenv('DB_DIR', 'data')
            db_path = Path(db_dir) / "stories.db"
        else:
            db_path = Path(db_path)
        
        # Ensure data directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    story_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create reminder preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminder_preferences (
                    user_id INTEGER PRIMARY KEY,
                    reminder_time TEXT NOT NULL,
                    timezone TEXT DEFAULT 'UTC',
                    enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    feedback_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster user queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON stories(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON stories(created_at)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def save_story(self, user_id: int, story_text: str, 
                   username: str = None, first_name: str = None) -> int:
        """
        Save a story to the database
        
        Args:
            user_id: Telegram user ID
            story_text: The story content
            username: Optional Telegram username
            first_name: Optional user's first name
            
        Returns:
            The ID of the saved story
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stories (user_id, username, first_name, story_text)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, story_text))
            
            conn.commit()
            story_id = cursor.lastrowid
            logger.info(f"Story {story_id} saved for user {user_id}")
            return story_id
    
    def get_user_stories(self, user_id: int, limit: int = None):
        """
        Get all stories for a specific user
        
        Args:
            user_id: Telegram user ID
            limit: Optional limit on number of stories to return
            
        Returns:
            List of story dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT id, user_id, username, first_name, story_text, created_at
                FROM stories
                WHERE user_id = ?
                ORDER BY created_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_stories_by_date(self, user_id: int, date: datetime):
        """
        Get stories for a specific date
        
        Args:
            user_id: Telegram user ID
            date: The date to search for
            
        Returns:
            List of story dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            date_str = date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT id, user_id, username, first_name, story_text, created_at
                FROM stories
                WHERE user_id = ? 
                AND DATE(created_at) = ?
                ORDER BY created_at DESC
            """, (user_id, date_str))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def count_user_stories(self, user_id: int) -> int:
        """Count total stories for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM stories WHERE user_id = ?
            """, (user_id,))
            
            return cursor.fetchone()[0]
    
    def set_reminder(self, user_id: int, reminder_time: str, timezone: str = 'UTC') -> None:
        """
        Set or update reminder preferences for a user
        
        Args:
            user_id: Telegram user ID
            reminder_time: Time in HH:MM format (24-hour)
            timezone: User's timezone (default UTC)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reminder_preferences (user_id, reminder_time, timezone, enabled)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    reminder_time = excluded.reminder_time,
                    timezone = excluded.timezone,
                    enabled = 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, reminder_time, timezone))
            
            conn.commit()
            logger.info(f"Reminder set for user {user_id} at {reminder_time} {timezone}")
    
    def disable_reminder(self, user_id: int) -> bool:
        """
        Disable reminder for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if reminder was disabled, False if no reminder existed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reminder_preferences
                SET enabled = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND enabled = 1
            """, (user_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                logger.info(f"Reminder disabled for user {user_id}")
                return True
            return False
    
    def get_reminder_preference(self, user_id: int):
        """
        Get reminder preference for a specific user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with reminder settings or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, reminder_time, timezone, enabled, created_at, updated_at
                FROM reminder_preferences
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_active_reminders(self):
        """
        Get all active reminder preferences
        
        Returns:
            List of dictionaries with reminder settings
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, reminder_time, timezone, enabled
                FROM reminder_preferences
                WHERE enabled = 1
                ORDER BY reminder_time
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def save_feedback(self, user_id: int, feedback_text: str,
                     username: str = None, first_name: str = None) -> int:
        """
        Save user feedback to the database
        
        Args:
            user_id: Telegram user ID
            feedback_text: The feedback content
            username: Optional Telegram username
            first_name: Optional user's first name
            
        Returns:
            The ID of the saved feedback
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_id, username, first_name, feedback_text)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, feedback_text))
            
            conn.commit()
            feedback_id = cursor.lastrowid
            logger.info(f"Feedback {feedback_id} saved from user {user_id}")
            return feedback_id
    
    def get_all_feedback(self):
        """
        Get all feedback from all users
        
        Returns:
            List of feedback dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, first_name, feedback_text, created_at
                FROM feedback
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
