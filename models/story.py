"""
Story model for storing user's storyworthy moments
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StoryDatabase:
    """Manage story storage in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "stories.db"
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
