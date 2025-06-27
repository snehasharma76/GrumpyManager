#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
import telegram
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_telegram_connection():
    """Test the connection to the Telegram API."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
            return False
        
        bot = telegram.Bot(token=bot_token)
        bot_info = bot.get_me()
        logger.info(f"Successfully connected to Telegram as {bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Telegram: {e}")
        return False

def test_google_sheets_connection():
    """Test the connection to the Google Sheets API."""
    try:
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if not sheet_id:
            logger.error("GOOGLE_SHEET_ID not found in .env file")
            return False
        
        if not service_account_file:
            logger.error("GOOGLE_SERVICE_ACCOUNT_FILE not found in .env file")
            return False
        
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        # Authenticate using the service account credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_file, scope)
        
        # Create a gspread client
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get all worksheet tabs
        worksheets = spreadsheet.worksheets()
        worksheet_names = [ws.title for ws in worksheets]
        
        logger.info(f"Successfully connected to Google Sheet. Found tabs: {', '.join(worksheet_names)}")
        
        # Check for required tabs
        required_tabs = ['Task_Log', 'OKR_Log', 'Daily_Progress_Log']
        missing_tabs = [tab for tab in required_tabs if tab not in worksheet_names]
        
        if missing_tabs:
            logger.warning(f"Missing required tabs: {', '.join(missing_tabs)}")
        else:
            logger.info("All required tabs are present")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {e}")
        return False

def test_telegram_group():
    """Test sending a message to the Telegram group."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        group_chat_id = os.getenv('TELEGRAM_GROUP_CHAT_ID')
        
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
            return False
        
        if not group_chat_id:
            logger.error("TELEGRAM_GROUP_CHAT_ID not found in .env file")
            return False
        
        bot = telegram.Bot(token=bot_token)
        bot.send_message(
            chat_id=group_chat_id,
            text="🧪 This is a test message from InternBot. If you can see this, the bot is configured correctly!"
        )
        
        logger.info("Successfully sent a test message to the Telegram group")
        return True
    except Exception as e:
        logger.error(f"Failed to send message to Telegram group: {e}")
        return False

def main():
    """Run all tests."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting setup tests...")
    
    # Test Telegram connection
    telegram_success = test_telegram_connection()
    
    # Test Google Sheets connection
    sheets_success = test_google_sheets_connection()
    
    # Test Telegram group
    group_success = test_telegram_group() if telegram_success else False
    
    # Print summary
    logger.info("\n--- Test Results ---")
    logger.info(f"Telegram API Connection: {'✅ Success' if telegram_success else '❌ Failed'}")
    logger.info(f"Google Sheets API Connection: {'✅ Success' if sheets_success else '❌ Failed'}")
    logger.info(f"Telegram Group Message: {'✅ Success' if group_success else '❌ Failed'}")
    
    if telegram_success and sheets_success and group_success:
        logger.info("\n🎉 All tests passed! Your bot is ready to run.")
    else:
        logger.info("\n⚠️ Some tests failed. Please check the logs above for details.")

if __name__ == "__main__":
    main()
