# Moments Bot

A Telegram bot for practicing Spanish through daily moments.

## Quick Start

```bash
# Setup
cd "Moments Bot"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
BOT_TOKEN=your_bot_token_from_botfather
BOT_USERNAME=@your_bot_username
```

```bash
# Run
python bot.py
```

## Commands

- `/start` - Welcome and create profile
- `/newmoment` - Record a new moment
- `/mymoments` - View your moments
- `/help` - Show all commands

## Deploy to Render

1. Push to GitHub
2. Create Web Service on Render
3. Add `BOT_TOKEN` environment variable
4. Deploy

## Roadmap

✅ Moment tracking with context  
✅ Progress statistics  
✅ Search and filtering  
🚧 AI feedback and daily reminders
