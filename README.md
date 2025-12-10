# Telegram Bot Skeleton

A basic Telegram bot skeleton with webhook support for Render deployment. This is a clean starting point for building your own Telegram bot with production-ready deployment setup.

## 🌟 Features

- 🤖 **Basic Bot Commands**: `/start` and `/help` commands
- 🌐 **Webhook Support**: Ready for production deployment on Render
- 🏠 **Polling Mode**: Local development with polling
- 📦 **Modular Structure**: Clean code organization
- ⚙️ **Environment Config**: Dotenv configuration support

## 🚀 Quick Start

### 1. Create Your Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token

### 2. Set Up the Project

```bash
# Clone or download this repository
cd "Moments Bot"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configure Your Bot

Edit `.env` and add your bot token:
```
BOT_TOKEN=your_bot_token_from_botfather
BOT_USERNAME=@your_bot_username
```

### 4. Run the Bot

```bash
python bot.py
```

## 🎯 How to Use

### Basic Commands

- `/start` - Welcome message
- `/help` - Show all available commands

## 📁 Project Structure

```
telegram-bot/
├── bot.py                 # Main bot application
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration management
├── handlers/
│   ├── __init__.py
│   └── commands.py        # Basic command handlers
├── models/
│   └── __init__.py
├── services/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── setup_webhook.py      # Webhook setup script
├── .env.example          # Environment template
└── README.md             # This file
```

## 🛠️ Development

### Running Locally

- [x] Modular project structure
- [x] Conversation state management
- [x] Moment data models
- [x] JSON-based storage
- [x] Basic command handlers
- [x] Progress tracking
- [x] Search and export functionality

### Phase 2 Roadmap 🚧

- [ ] AI service integration (OpenAI/Claude)
- [ ] Intelligent Spanish feedback
- [ ] Daily reminder scheduling
- [ ] Vocabulary tracking
- [ ] Difficulty progression

### Phase 3+ Future Features 💭

- [ ] Voice message support
- [ ] Photo moments with captions
- [ ] Social features and sharing
- [ ] Multiple language support
- [ ] Advanced analytics

## 🔧 Configuration Options

Environment variables in `.env`:

```bash
# Required
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=@your_bot_username

```

### Run Locally

```bash
python bot.py
```

You should see:
```
🤖 Starting Telegram Bot...
🏠 Running in polling mode (local)
✅ Bot handlers registered:
   🏠 /start - Welcome message
   ℹ️  /help - Show help message
🚀 Telegram Bot is running! Press Ctrl+C to stop.
```

## 🌐 Deploying to Render

This bot is configured for easy deployment to Render.

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial bot setup"
git push origin main
```

### 2. Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Add environment variable: `BOT_TOKEN` = your bot token
6. Click "Create Web Service"

### 3. Set Up Webhook

After deployment, run the webhook setup script:

```bash
python setup_webhook.py
```

This will configure your bot to receive updates via webhook instead of polling.

## 🔧 Customization

Add your own commands in `handlers/commands.py`:

```python
@staticmethod
async def your_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Your custom command"""
    await update.message.reply_text("Your response here!")
```

Then register it in `bot.py`:

```python
telegram_app.add_handler(CommandHandler("yourcommand", CommandHandlers.your_command))
```

## 📄 License

See [LICENSE](LICENSE) file for details.

---

Built with ❤️ using python-telegram-bot and Flask

```
.
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md             # This file
```

## 🐛 Troubleshooting

### Bot Token Error
If you see "❌ Error: BOT_TOKEN not found", make sure:
- You created the `.env` file
- You added your actual bot token to the `.env` file
- The token is correctly formatted (no extra spaces)

### Bot Not Responding
- Make sure the bot is running (`python bot.py`)
- Check that you're messaging the correct bot username
- Verify your bot token is valid by testing it with BotFather

## 💡 Next Steps

This is a basic bot skeleton. You can extend it by:
- Adding more commands
- Implementing conversation flows with ConversationHandler
- Adding database storage (SQLite, PostgreSQL, etc.)
- Integrating with external APIs
- Adding inline keyboards and buttons
- Implementing user authentication
- Adding logging and monitoring
