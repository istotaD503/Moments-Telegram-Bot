#!/usr/bin/env python3
"""
Script to set up webhook for Telegram bot on Render
"""

import requests
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def setup_webhook():
    """Set up webhook URL for the bot."""
    
    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return False
    
    # Get the Render service URL from environment
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    if not render_url:
        print("❌ RENDER_EXTERNAL_URL not found")
        print("ℹ️  This should be set automatically by Render")
        print("ℹ️  You can also set it manually: https://your-service-name.onrender.com")
        return False
    
    webhook_url = f"{render_url}/webhook"
    telegram_api_url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook"
    
    payload = {
        'url': webhook_url
    }
    
    print(f"🔗 Setting webhook to: {webhook_url}")
    
    try:
        response = requests.post(telegram_api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                print(f"📋 Response: {result.get('description', 'Webhook is set')}")
                return True
            else:
                print(f"❌ Webhook setup failed: {result.get('description')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📋 Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    return False

def check_webhook_info():
    """Check current webhook information."""
    
    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return
    
    telegram_api_url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(telegram_api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                print("📋 Current webhook info:")
                print(f"   URL: {webhook_info.get('url', 'Not set')}")
                print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {webhook_info.get('pending_update_count', 0)}")
                if webhook_info.get('last_error_date'):
                    print(f"   Last error: {webhook_info.get('last_error_message', 'Unknown')}")
            else:
                print(f"❌ Failed to get webhook info: {result.get('description')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def main():
    """Main function."""
    print("🤖 Telegram Bot Webhook Setup for Render")
    print("=" * 50)
    
    # Validate configuration
    if not settings.validate():
        print("❌ Bot configuration is invalid")
        sys.exit(1)
    
    print("📋 Checking current webhook status...")
    check_webhook_info()
    
    print("\n🔧 Setting up new webhook...")
    success = setup_webhook()
    
    if success:
        print("\n✅ Webhook setup completed successfully!")
        print("🎉 Your bot should now be able to receive messages on Render!")
    else:
        print("\n❌ Webhook setup failed!")
        print("💡 Manual setup: Visit this URL in your browser:")
        render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-service-name.onrender.com')
        print(f"   https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook?url={render_url}/webhook")

if __name__ == '__main__':
    main()