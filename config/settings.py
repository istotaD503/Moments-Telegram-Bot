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

    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present"""
        if not cls.BOT_TOKEN:
            print("❌ Error: BOT_TOKEN not found in environment variables!")
            return False
        return True

# Global settings instance
settings = Settings()