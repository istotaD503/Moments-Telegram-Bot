# Copilot Instructions - Moments Bot

## Architecture Overview

This is a **Telegram bot for capturing daily "storyworthy moments"**, inspired by Matthew Dicks' "Homework for Life" practice. The bot runs with dual-threaded architecture:
- **Primary thread**: Telegram polling (`telegram.ext.Application`)
- **Background thread**: Flask web server for Render.com health checks (port 10000)

### Key Components

- `bot.py`: Main entry point with dual-server setup and ConversationHandler registration
- `handlers/commands.py`: All command handlers live here as static methods in `CommandHandlers` class
- `models/story.py`: SQLite database layer (`StoryDatabase`) for story persistence
- `config/settings.py`: Environment config using singleton `settings` instance
- `utils/assets.py`: Template loading utilities (e.g., `welcome_message.txt`)

## Critical Patterns

### 1. ConversationHandler State Machine
The `/story` command uses telegram's ConversationHandler with state `WAITING_FOR_STORY`:
```python
story_conversation = ConversationHandler(
    entry_points=[CommandHandler("story", CommandHandlers.story_command)],
    states={WAITING_FOR_STORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_story)]},
    fallbacks=[CommandHandler("cancel", CommandHandlers.cancel_story)]
)
```
**Never** add a default text message handler - it conflicts with conversation states.

### 2. Database Initialization Pattern
`StoryDatabase` auto-creates `data/stories.db` on first import. All handlers share a **single class-level instance**:
```python
class CommandHandlers:
    story_db = StoryDatabase()  # Singleton pattern
```
Don't create new instances - use `CommandHandlers.story_db`.

### 3. Asset Loading
Template messages (like welcome) use `{user_first_name}` placeholders loaded via `load_welcome_message()`. See `assets/welcome_message.txt` for the format.

## Development Workflow

**Setup**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Required Environment**:
- `BOT_TOKEN`: From @BotFather (required)
- `PORT`: Web server port (defaults to 10000)

**Run locally**:
```bash
python bot.py
```
Look for "🚀 Bot running" confirmation. Health endpoint: `http://localhost:10000/health`

**Deployment**: Render.com auto-deploys via `render.yaml` + Dockerfile. No manual build needed.

## Testing Conventions

No test suite exists yet. Manual testing via Telegram client. When adding features:
1. Test conversation flows end-to-end
2. Verify database writes in `data/stories.db` 
3. Check error handler with invalid inputs

## Code Style Notes

- **Async handlers**: All telegram handlers are `async` - use `await` for bot API calls
- **Logging**: Use module-level `logger = logging.getLogger(__name__)` 
- **Error handling**: User-facing errors go through `CommandHandlers.error_handler`
- **Markdown/HTML**: Commands use `parse_mode='HTML'` for rich text (see `/story` prompts)
- **Matthew Dicks quotes**: Maintain the inspirational tone in story-related messages

## Key Files to Reference

- `handlers/commands.py`: See `story_command()` and `receive_story()` for conversation pattern
- `models/story.py`: Study `get_user_stories()` for SQL query patterns
- `bot.py`: Understand handler registration order (logger group=-1, conversation handlers, then commands)
