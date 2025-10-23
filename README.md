# Moments-Telegram-Bot

A simple "Hello World" Telegram bot that demonstrates basic bot functionality.

## Features

- 👋 Responds to `/start` command with a welcome message
- 🌟 Responds to `/hello` command with a friendly greeting
- 📚 Provides help with `/help` command
- 💬 Echoes back any text messages with friendly responses
- 🤖 Handles basic conversation patterns (hello, how are you, bye)

## Prerequisites

- Python 3.7 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))

## Setup Instructions

### 1. Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a conversation and send `/newbot`
3. Follow the instructions to create your bot:
   - Choose a name for your bot (e.g., "My Hello World Bot")
   - Choose a username for your bot (must end in 'bot', e.g., "my_hello_world_bot")
4. Copy the bot token that BotFather gives you

### 2. Set Up the Project

1. Clone this repository and navigate to the project directory:
```bash
cd "Moments Bot"
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create your environment file:
```bash
cp .env.example .env
```

5. Edit the `.env` file and add your bot token:
```
BOT_TOKEN=your_actual_bot_token_here
BOT_USERNAME=@your_bot_username
```

### 3. Run the Bot

```bash
python bot.py
```

You should see:
```
🤖 Starting Hello World Bot @your_bot_username...
✅ Bot is running! Press Ctrl+C to stop.
```

## Testing Your Bot

1. Open Telegram and search for your bot by its username
2. Start a conversation with your bot
3. Try these commands:
   - `/start` - Get a welcome message
   - `/hello` - Get a friendly greeting
   - `/help` - See available commands
   - Send any message - Get an echo response

## Available Commands

- `/start` - Welcome message and bot introduction
- `/hello` - Get a friendly greeting
- `/help` - Show help message

## Project Structure

```
.
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env              # Your actual environment variables (don't commit!)
├── .gitignore        # Git ignore file
└── README.md         # This file
```

## Troubleshooting

### Bot Token Error
If you see "❌ Error: BOT_TOKEN not found", make sure:
- You created the `.env` file
- You added your actual bot token to the `.env` file
- The token is correctly formatted (no extra spaces)

### Bot Not Responding
- Make sure the bot is running (`python bot.py`)
- Check that you're messaging the correct bot username
- Verify your bot token is valid by testing it with BotFather

## Next Steps

This is a basic "Hello World" bot. You can extend it by:
- Adding more commands
- Implementing conversation flows
- Adding database storage
- Integrating with external APIs
- Adding inline keyboards and buttons

## Development

To extend this bot for the "Moments" storytelling feature, you could add:
- Story submission handlers
- Spanish translation features
- Progress tracking
- User databases
