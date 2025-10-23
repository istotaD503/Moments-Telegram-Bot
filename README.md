# Spanish Moments Bot

A Telegram bot that helps you practice Spanish by capturing and translating your daily story-worthy moments. Inspired by Matthew Dicks' "Homework for Life" concept combined with active language learning.

## 🌟 Concept

This bot helps you:
1. **Capture daily moments** - Write about story-worthy moments from your day in English
2. **Practice Spanish translation** - Attempt to translate your moment into Spanish
3. **Receive feedback** - Get AI-powered corrections and explanations (Phase 2)
4. **Track progress** - Monitor your learning journey with statistics and streaks

## ✨ Features

### Phase 1 (Current Implementation)
- 📝 **Moment Capture**: Multi-step conversation flow for capturing moments
- 🇪🇸 **Spanish Practice**: Attempt Spanish translations of your moments
- � **Persistent Storage**: All moments saved locally in JSON format
- � **Progress Tracking**: View statistics and learning progress
- 🔍 **Search & Review**: Find and review your past moments
- 📄 **Export**: Download your moments as text files

### Coming Soon (Phase 2+)
- 🤖 **AI Feedback**: Detailed corrections and explanations
- ⏰ **Daily Reminders**: Automatic prompts to capture moments
- 📚 **Vocabulary Building**: Track and review learned words
- 🎯 **Difficulty Progression**: Adaptive learning based on your level
- 🎵 **Voice Support**: Practice pronunciation with voice messages

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

- `/start` - Welcome message and overview
- `/moment` - Start capturing a new moment (main feature!)
- `/recent` - View your recent moments
- `/stats` - See your learning progress
- `/search [term]` - Search through your moments
- `/export` - Download all your moments
- `/help` - Show all available commands

### Capturing Your First Moment

1. Send `/moment` to your bot
2. Write about a story-worthy moment from your day in English
3. The bot will ask you to translate it to Spanish
4. Try your best - don't worry about perfection!
5. Your moment is saved for future review

### Example Flow

```
You: /moment

Bot: ✨ Ready to capture a story-worthy moment?
     Choose a prompt or write about any moment...

You: I watched a beautiful sunset today and felt grateful 
     for this peaceful moment.

Bot: 🇪🇸 Perfect! Now try writing that same moment in Spanish.
     Your English moment: "I watched a beautiful sunset..."
     Now write it in Spanish:

You: Vi una puesta de sol hermosa hoy y me sentí agradecido 
     por este momento pacífico.

Bot: 🎉 Excellent work! You've completed your Spanish moment.
     [Shows both versions and encouragement]
```

## 📁 Project Structure

```
moments_bot/
├── bot.py                 # Main bot application
├── config/
│   └── settings.py        # Configuration management
├── handlers/
│   ├── conversation.py    # Moment capture conversation flow
│   └── commands.py        # Basic command handlers
├── services/
│   └── storage.py         # Data persistence (JSON)
├── models/
│   └── moment.py          # Data models (Moment, UserStats)
├── utils/
│   └── helpers.py         # Utility functions
├── data/                  # User moment files (auto-created)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🛠️ Development

### Phase 1 Implementation ✅

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

# Optional
DATA_DIR=data                    # Where to store moment files
MAX_MOMENTS_PER_DAY=3           # Daily capture limit
CONVERSATION_TIMEOUT=1800        # 30 minutes
DEFAULT_REMINDER_TIME=20:00      # 8 PM reminders (Phase 2)

# AI Integration (Phase 2)
OPENAI_API_KEY=your_key         # For AI feedback
AI_MODEL=gpt-3.5-turbo          # Model to use
AI_MAX_TOKENS=500               # Response length limit
AI_TEMPERATURE=0.7              # Creativity level
```

## 📊 Data Storage

Moments are stored as JSON files in the `data/` directory:
- `moments_{user_id}.json` - Contains all moments for each user
- Includes timestamps, progress tracking, and metadata
- Easy to backup, export, or migrate

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Inspiration

- **Matthew Dicks** - "Homework for Life" concept of daily moment observation
- **Language learning communities** - Active recall and spaced repetition principles
- **Telegram bot ecosystem** - Simple, accessible, and conversational interface

---

**¡Vamos a practicar español!** Start capturing your story-worthy moments today! 🇪🇸✨

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
