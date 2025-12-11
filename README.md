# Moments Bot

A Telegram bot for capturing daily storyworthy moments, inspired by Matthew Dicks' Homework for Life.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
BOT_TOKEN=your_bot_token_from_botfather
```

Run:
```bash
python bot.py
```

## Commands

- `/start` - Welcome message
- `/story` - Record today's moment
- `/mystories` - View your saved stories
- `/help` - Show all commands

## Deploy to Render

1. Push to GitHub
2. Create Web Service on Render
3. Add `BOT_TOKEN` environment variable
4. Deploy
