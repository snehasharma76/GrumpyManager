#!/usr/bin/env python3
import logging
import os
from dotenv import load_dotenv
from bot import InternBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        'TELEGRAM_BOT_TOKEN', 
        'TELEGRAM_GROUP_CHAT_ID',
        'GOOGLE_SHEET_ID',
        'GOOGLE_SERVICE_ACCOUNT_FILE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in the .env file.")
        return
    
    # Initialize and start the bot
    logger.info("Starting InternBot...")
    bot = InternBot()
    bot.start()

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Start the bot
    main()
