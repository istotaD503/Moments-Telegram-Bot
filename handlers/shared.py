"""
Shared resources for all handler modules
"""
from models.story import StoryDatabase

# Single shared database instance used by all handlers
story_db = StoryDatabase()
