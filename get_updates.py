#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get the bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("No bot token found. Please set TELEGRAM_BOT_TOKEN in your .env file.")
        return
    
    # Make a request to the Telegram API
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    
    # Parse the response
    data = response.json()
    
    # Pretty print the response
    print(json.dumps(data, indent=2))
    
    # Check if there are any updates
    if data['ok'] and data['result']:
        print("\n--- Chat IDs found ---")
        for update in data['result']:
            if 'message' in update and 'chat' in update['message']:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat['type']
                chat_title = chat.get('title', 'Private Chat')
                print(f"Chat ID: {chat_id}, Type: {chat_type}, Title: {chat_title}")
    else:
        print("\nNo updates found. Make sure to:")
        print("1. Add your bot to the group")
        print("2. Send some messages in the group")
        print("3. Run this script again")
        print("\nIf that doesn't work, try enabling privacy mode for your bot:")
        print("1. Talk to @BotFather")
        print("2. Use /mybots command")
        print("3. Select your bot")
        print("4. Select 'Bot Settings'")
        print("5. Select 'Group Privacy'")
        print("6. Select 'Turn off'")

if __name__ == '__main__':
    main()
