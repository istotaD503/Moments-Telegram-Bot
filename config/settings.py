"""
Configuration settings for the Telegram Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Centralized configuration management"""
    
    # Bot configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present"""
        if not cls.BOT_TOKEN:
            print("❌ Error: BOT_TOKEN not found in environment variables!")
            return False
        return True

# Global settings instance
settings = Settings()