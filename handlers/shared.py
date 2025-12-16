"""
Shared resources for all handler modules
"""
from models.story import StoryDatabase

# Single shared database instance used by all handlers
story_db = StoryDatabase()

# Conversation states
WAITING_FOR_STORY = 1
WAITING_FOR_REMINDER_TIME = 2
WAITING_FOR_TIMEZONE = 3
WAITING_FOR_FEEDBACK = 10
