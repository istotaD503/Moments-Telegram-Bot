"""
Utility functions for loading assets and templates
"""
import os
from pathlib import Path

def get_asset_path(filename: str) -> Path:
    """Get the absolute path to an asset file"""
    current_dir = Path(__file__).parent.parent
    return current_dir / "assets" / filename

def load_about_message(user_first_name: str = "") -> str:
    """
    Load the about message from assets and format it with user data
    
    Args:
        user_first_name: The user's first name to personalize the message
    
    Returns:
        Formatted about message string
    """
    asset_path = get_asset_path("about_message.txt")
    
    try:
        with open(asset_path, 'r', encoding='utf-8') as f:
            message = f.read()
        
        # Format with user's name if provided
        if user_first_name:
            message = message.format(user_first_name=user_first_name)
        
        return message
    except FileNotFoundError:
        # Fallback message if asset file is not found
        return (
            f"Hello {user_first_name}! 👋\n\n"
            "Welcome to the Moments Bot!\n\n"
            "Use /help to see available commands."
        )
    except Exception as e:
        # Log error and return fallback
        import logging
        logging.error(f"Error loading about message: {e}")
        return f"Hello {user_first_name}! 👋 Welcome to the Moments Bot!"
