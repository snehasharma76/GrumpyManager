import os
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')

# Timezone Configuration
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

# Sheet Tab Names
TASK_LOG_SHEET = 'Task_Log'
OKR_LOG_SHEET = 'OKR_Log'
DAILY_PROGRESS_LOG_SHEET = 'Daily_Progress_Log'

# Task Priorities
TASK_PRIORITIES = {
    'P1': '🔴',  # High priority
    'P2': '🟡',  # Medium priority
    'P3': '🔵',  # Low priority
}

# Scheduled Message Times (in 24-hour format, IST)
DAILY_PLANNING_TIME = '10:00'
DAILY_NUDGE_TIME = '11:00'
MIDDAY_CHECK_TIME = '15:00'
EOD_SUMMARY_TIME = '19:00'
