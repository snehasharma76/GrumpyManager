#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_id_command(update: Update, context: CallbackContext):
    """Send the chat ID when the command /getchatid is issued."""
    chat_id = update.effective_chat.id
    update.message.reply_text(f"This chat's ID is: {chat_id}")
    logger.info(f"Chat ID request from {update.effective_user.username}: {chat_id}")

def main():
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get the bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("No bot token found. Please set TELEGRAM_BOT_TOKEN in your .env file.")
        return
    
    # Create the Updater and pass it your bot's token
    updater = Updater(token)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("getchatid", get_id_command))
    
    # Start the Bot
    updater.start_polling()
    
    logger.info("Bot started. Add it to a group and use /getchatid to get the chat ID.")
    logger.info("Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
