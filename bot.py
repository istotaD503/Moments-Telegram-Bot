#!/usr/bin/env python3
"""
Simple "Hello World" Telegram Bot
This bot responds to the /start and /hello commands with greeting messages.
"""

import logging
import os
from typing import Final

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN: Final = os.getenv('BOT_TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME', '@your_bot')

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_first_name = update.effective_user.first_name
    welcome_message = (
        f"👋 Hello {user_first_name}! Welcome to the Hello World Bot!\n\n"
        "I'm a simple bot that responds to basic commands. Try these:\n"
        "• /start - Show this welcome message\n"
        "• /hello - Get a friendly greeting\n"
        "• /help - Show available commands\n\n"
        "You can also just send me any message and I'll respond!"
    )
    await update.message.reply_text(welcome_message)

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a hello message when the command /hello is issued."""
    user_first_name = update.effective_user.first_name
    hello_message = f"🌟 Hello there, {user_first_name}! Hope you're having a great day! 🌟"
    await update.message.reply_text(hello_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    help_message = (
        "🤖 *Hello World Bot Help*\n\n"
        "*Available Commands:*\n"
        "• `/start` - Welcome message and bot introduction\n"
        "• `/hello` - Get a friendly greeting\n"
        "• `/help` - Show this help message\n\n"
        "*About this bot:*\n"
        "This is a simple 'Hello World' Telegram bot created for testing purposes. "
        "It demonstrates basic bot functionality including command handling and message responses.\n\n"
        "Send me any message and I'll echo it back with a friendly response! 😊"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages that are not commands."""
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user_first_name = update.effective_user.first_name

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # Generate response
    if 'hello' in text.lower():
        response = f"Hello {user_first_name}! 👋 Thanks for saying hello!"
    elif 'how are you' in text.lower():
        response = "I'm doing great! Thanks for asking! 😊 How are you?"
    elif 'bye' in text.lower() or 'goodbye' in text.lower():
        response = f"Goodbye {user_first_name}! Have a wonderful day! 👋"
    else:
        response = f"Hi {user_first_name}! You said: '{text}'\n\nI'm a simple Hello World bot. Try sending /help to see what I can do! 🤖"

    print('Bot:', response)
    await update.message.reply_text(response)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    # Check if token is provided
    if not TOKEN:
        print("❌ Error: BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("BOT_TOKEN=your_telegram_bot_token_here")
        return

    print(f"🤖 Starting Hello World Bot {BOT_USERNAME}...")

    # Create the Application
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("help", help_command))

    # Add message handler for non-command messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    app.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()