#!/usr/bin/env python3
import logging
import os
os.makedirs("logs", exist_ok=True)
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
    
    # Check for test mode flag
    import sys
    test_mode = '--test' in sys.argv
    
    # Initialize the bot
    logger.info("Starting InternBot...")
    bot = InternBot()
    
    if test_mode:
        logger.info("Starting in TEST MODE - will not connect to Telegram API")
        # Test the scheduled tasks without starting the bot
        print("\n=== TESTING SCHEDULED TASKS ===\n")
        print("1. Testing daily planning reminder...")
        bot.send_daily_planning_reminder()
        print("\n2. Testing daily nudge...")
        bot.send_daily_nudge()
        print("\n3. Testing midday check-in...")
        bot.send_midday_checkin()
        print("\n4. Testing end-of-day summary...")
        bot.send_eod_summary()
        print("\n=== TEST COMPLETE ===\n")
        print("All scheduled tasks tested. Check logs for details.")
    else:
        # Start the bot normally
        logger.info("Starting bot in NORMAL MODE")
        bot.start()

if __name__ == "__main__":
    # Start the bot
    main()
