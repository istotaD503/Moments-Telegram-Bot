"""
Configuration settings for the Moments Bot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Centralized configuration management"""
    
    # Bot configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    BOT_USERNAME: str = os.getenv('BOT_USERNAME', '@moments_bot')
    
    # AI Service configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    AI_MODEL: str = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS: int = int(os.getenv('AI_MAX_TOKENS', '500'))
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    # Storage configuration
    DATA_DIR: str = os.getenv('DATA_DIR', 'data')
    MOMENTS_FILE_PATTERN: str = 'moments_{user_id}.json'
    
    # Bot behavior
    DEFAULT_REMINDER_TIME: str = os.getenv('DEFAULT_REMINDER_TIME', '20:00')
    MAX_MOMENTS_PER_DAY: int = int(os.getenv('MAX_MOMENTS_PER_DAY', '3'))
    
    # Conversation timeouts (in seconds)
    CONVERSATION_TIMEOUT: int = int(os.getenv('CONVERSATION_TIMEOUT', '1800'))  # 30 minutes
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present"""
        if not cls.BOT_TOKEN:
            print("❌ Error: BOT_TOKEN not found in environment variables!")
            return False
        return True
    
    @classmethod
    def get_moments_file_path(cls, user_id: int) -> str:
        """Get the file path for a user's moments"""
        filename = cls.MOMENTS_FILE_PATTERN.format(user_id=user_id)
        return os.path.join(cls.DATA_DIR, filename)

# Global settings instance
settings = Settings()