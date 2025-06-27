#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def echo(update: Update, context: CallbackContext):
    """Echo the user message and show chat ID."""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    username = update.effective_user.username
    
    # Log the information
    logger.info(f"Message from {username} in {chat_type} chat with ID: {chat_id}")
    
    # Reply with the chat ID
    update.message.reply_text(f"This chat's ID is: {chat_id}\nChat type: {chat_type}")

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
    
    # Register message handler for all messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    # Start the Bot
    updater.start_polling()
    
    logger.info("Bot started. Send a direct message to the bot or add it to a group and send a message.")
    logger.info("The bot will reply with the chat ID.")
    logger.info("Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
