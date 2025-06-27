import logging
import re
from datetime import datetime
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, 
    CallbackQueryHandler, MessageHandler, Filters
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')

# Import timezone and time constants
import pytz
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

# Define scheduled times
DAILY_PLANNING_TIME = '10:00'
DAILY_NUDGE_TIME = '11:00'
MIDDAY_CHECK_TIME = '15:00'
EOD_SUMMARY_TIME = '19:00'
from sheets_manager import SheetsManager
from task_manager import TaskManager
from okr_manager import OKRManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InternBot:
    """
    Main bot class for the InternBot Telegram bot.
    """
    def __init__(self):
        """Initialize the bot with all required components."""
        # Initialize the sheets manager
        self.sheets_manager = SheetsManager()
        
        # Initialize task and OKR managers
        self.task_manager = TaskManager(self.sheets_manager)
        self.okr_manager = OKRManager(self.sheets_manager)
        
        # Store conversation states
        self.conversation_state = {}
        
        # Initialize the Telegram updater and dispatcher
        self.updater = Updater(token=TELEGRAM_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Register command handlers
        self.register_handlers()
        
        # Initialize the scheduler
        self.scheduler = BackgroundScheduler(timezone=IST_TIMEZONE)
        self.setup_scheduled_tasks()
    
    def register_handlers(self):
        """Register all command and callback handlers."""
        # Command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("task", self.task_command))
        self.dispatcher.add_handler(CommandHandler("mytasks", self.mytasks_command))
        self.dispatcher.add_handler(CommandHandler("syncokrs", self.syncokrs_command))
        
        # Callback query handler for buttons
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for OKR updates
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.message_handler))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
    
    def setup_scheduled_tasks(self):
        """Set up scheduled tasks using APScheduler."""
        # Daily planning reminder (10:00 AM IST)
        hour, minute = map(int, DAILY_PLANNING_TIME.split(':'))
        self.scheduler.add_job(
            self.send_daily_planning_reminder,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=IST_TIMEZONE),
            id='daily_planning'
        )
        
        # Daily nudge (11:00 AM IST)
        hour, minute = map(int, DAILY_NUDGE_TIME.split(':'))
        self.scheduler.add_job(
            self.send_daily_nudge,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=IST_TIMEZONE),
            id='daily_nudge'
        )
        
        # Mid-day check-in (3:00 PM IST)
        hour, minute = map(int, MIDDAY_CHECK_TIME.split(':'))
        self.scheduler.add_job(
            self.send_midday_checkin,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=IST_TIMEZONE),
            id='midday_checkin'
        )
        
        # End-of-day summary (7:00 PM IST)
        hour, minute = map(int, EOD_SUMMARY_TIME.split(':'))
        self.scheduler.add_job(
            self.send_eod_summary,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=IST_TIMEZONE),
            id='eod_summary'
        )
    
    def start(self):
        """Start the bot and scheduler."""
        # Start the scheduler
        self.scheduler.start()
        
        # Start the bot
        self.updater.start_polling()
        logger.info("Bot started. Press Ctrl+C to stop.")
        
        # Run the bot until you press Ctrl-C
        self.updater.idle()
        
        # Stop the scheduler when the bot is stopped
        self.scheduler.shutdown()
    
    def start_command(self, update: Update, context: CallbackContext):
        """Handle the /start command."""
        update.message.reply_text(
            "👋 Hello! I'm your startup accountability partner. "
            "I'll help you track tasks and OKRs. "
            "Type /help to see what I can do."
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handle the /help command."""
        help_text = (
            "*InternBot - Your Startup Accountability Partner*\n\n"
            "*Commands:*\n"
            "• `/task [Priority] [Description] -c [Category]` - Add a new task\n"
            "  Priority must be P1 (High), P2 (Medium), or P3 (Low)\n"
            "  Example: `/task P1 Draft investor email -c Partnerships`\n\n"
            "• `/mytasks` - View your open tasks\n\n"
            "• `/syncokrs` - Sync OKRs from the Google Sheet\n\n"
            "*Daily Schedule (IST):*\n"
            "• *10:00 AM* - Daily planning reminder\n"
            "• *11:00 AM* - Nudge for missing tasks\n"
            "• *3:00 PM* - Mid-day progress check\n"
            "• *7:00 PM* - End-of-day summary and OKR updates"
        )
        
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def task_command(self, update: Update, context: CallbackContext):
        """Handle the /task command to add a new task."""
        # Get the user's username
        username = update.effective_user.username
        
        if not username:
            update.message.reply_text(
                "Please set a username in your Telegram settings first."
            )
            return
        
        # Get the command text
        command_text = update.message.text
        
        # Add the task
        success, message = self.task_manager.add_task(username, command_text)
        
        # Reply with the result
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    def mytasks_command(self, update: Update, context: CallbackContext):
        """Handle the /mytasks command to view user's tasks."""
        try:
            # Get the user's username
            username = update.effective_user.username
            
            if not username:
                update.message.reply_text(
                    "Please set a username in your Telegram settings first."
                )
                return
            
            # Log the username for debugging
            logging.info(f"Fetching tasks for username: {username}")
            
            try:
                # Get the user's tasks
                message, reply_markup = self.task_manager.get_user_tasks_message(username)
                
                # Reply with the tasks
                update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error getting tasks for {username}: {str(e)}")
                update.message.reply_text(
                    f"Error retrieving your tasks: {str(e)}"
                )
        except Exception as e:
            logging.error(f"Error in mytasks_command: {str(e)}")
            update.message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )
    
    def syncokrs_command(self, update: Update, context: CallbackContext):
        """Handle the /syncokrs command to sync OKRs from the Google Sheet."""
        # Sync OKRs
        success = self.okr_manager.sync_okrs()
        
        if success:
            update.message.reply_text(
                "✅ OKRs synced successfully from the Google Sheet."
            )
        else:
            update.message.reply_text(
                "❌ Failed to sync OKRs. Please check the Google Sheet."
            )
    
    def button_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks."""
        query = update.callback_query
        
        # Get the callback data
        data = query.data
        
        # Handle "done" button clicks
        if data.startswith('done_'):
            task_id = data.replace('done_', '')
            self.handle_task_done(query, task_id)
        
        # Handle OKR update button clicks
        elif data.startswith('okr_'):
            okr_id = data.replace('okr_', '')
            self.handle_okr_update(query, okr_id)
    
    def handle_task_done(self, query, task_id):
        """Handle marking a task as done."""
        # Mark the task as done
        success = self.task_manager.mark_task_as_done(task_id)
        
        if success:
            # Edit the original message to show the task as done
            message = query.message.text
            
            # Find the task line in the message
            all_tasks = self.sheets_manager.task_log.get_all_records()
            task = next((t for t in all_tasks if t['Task_ID'] == task_id), None)
            
            if task:
                # Create a pattern to find the task line
                task_desc = re.escape(task['Task_Description'])
                pattern = f"(• .+{task_desc}.+\n)"
                
                # Replace with strikethrough
                new_message = re.sub(
                    pattern, 
                    f"• ~{task['Task_Description']}~ ✅\n", 
                    message
                )
                
                # Update the message
                query.edit_message_text(
                    text=new_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Answer the callback query
            query.answer("Task marked as done!")
        else:
            query.answer("Failed to mark task as done.")
    
    def handle_okr_update(self, query, okr_id):
        """Handle OKR update button clicks."""
        # Get the user's username
        username = query.from_user.username
        
        if not username:
            query.answer("Please set a username in your Telegram settings first.")
            return
        
        # Get the OKR
        okr = self.okr_manager.get_okr_by_id(okr_id)
        
        if not okr:
            query.answer("OKR not found. Please use /syncokrs to refresh.")
            return
        
        # Set the conversation state
        self.conversation_state[username] = {
            'waiting_for': 'okr_update',
            'okr_id': okr_id
        }
        
        # Answer the callback query
        query.answer()
        
        # Send a message asking for the update
        query.message.reply_text(
            f"What's the current number for '{okr['Goal_Name']}'?",
            reply_markup=None
        )
    
    def message_handler(self, update: Update, context: CallbackContext):
        """Handle text messages for OKR updates."""
        # Get the user's username
        username = update.effective_user.username
        
        if not username:
            return
        
        # Check if we're waiting for an OKR update from this user
        if username in self.conversation_state and self.conversation_state[username]['waiting_for'] == 'okr_update':
            # Get the OKR ID
            okr_id = self.conversation_state[username]['okr_id']
            
            # Get the new value
            new_value = update.message.text.strip()
            
            # Update the OKR progress
            success, feedback = self.okr_manager.update_okr_progress(username, okr_id, new_value)
            
            # Clear the conversation state
            del self.conversation_state[username]
            
            # Reply with the feedback
            update.message.reply_text(feedback)
    
    def send_daily_planning_reminder(self):
        """Send the daily planning reminder at 10:00 AM IST."""
        message = (
            "☀️ Good morning! It's time to plan our day. "
            "Add your tasks with `/task [Priority] [Description] -c [Category]`."
        )
        
        self.updater.bot.send_message(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    def send_daily_nudge(self):
        """Send nudges to users who haven't added tasks at 11:00 AM IST."""
        # Get all users in the group
        try:
            chat_members = self.updater.bot.get_chat_administrators(TELEGRAM_GROUP_CHAT_ID)
            usernames = [member.user.username for member in chat_members if member.user.username]
            
            # Check which users haven't added tasks today
            users_without_tasks = self.task_manager.check_users_without_tasks(usernames)
            
            # Send nudges
            for username in users_without_tasks:
                message = (
                    f"@{username}, you haven't added any tasks for the day yet. "
                    "What's your top priority?"
                )
                
                self.updater.bot.send_message(
                    chat_id=TELEGRAM_GROUP_CHAT_ID,
                    text=message
                )
        except Exception as e:
            logger.error(f"Error sending daily nudge: {e}")
    
    def send_midday_checkin(self):
        """Send the mid-day check-in at 3:00 PM IST."""
        message = "🕒 Afternoon Check-in! Here's the current status of our open tasks:"
        
        # Get all open tasks
        tasks_message, reply_markup = self.task_manager.get_all_open_tasks_message()
        
        # Send the message
        self.updater.bot.send_message(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send the tasks
        self.updater.bot.send_message(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            text=tasks_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def send_eod_summary(self):
        """Send the end-of-day summary at 7:00 PM IST."""
        # Get the EOD summary
        summary = self.task_manager.get_end_of_day_summary()
        
        # Send the summary
        self.updater.bot.send_message(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            text=summary,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send the OKR update message
        okr_message, reply_markup = self.okr_manager.get_okr_update_keyboard()
        
        self.updater.bot.send_message(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            text=okr_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def error_handler(self, update, context):
        """Log errors caused by updates."""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Notify users of the error
        if update and update.effective_chat:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, something went wrong. Please try again later."
            )
