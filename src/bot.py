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
        self.dispatcher.add_handler(CommandHandler("alltasks", self.alltasks_command))
        self.dispatcher.add_handler(CommandHandler("duetasks", self.duetasks_command))
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
            "• `/task [Priority] [Description] -c [Category] -d [YYYY-MM-DD] -a [Assignee]` - Add a new task\n"
            "  Priority must be P1 (High), P2 (Medium), or P3 (Low)\n"
            "  Category is optional (default: General)\n"
            "  Due date is optional in YYYY-MM-DD format\n"
            "  Assignee is optional (default: yourself)\n"
            "  Example: `/task P1 Draft investor email -c Partnerships -d 2025-07-05 -a teammate`\n\n"
            "• `/mytasks` - View your open tasks\n\n"
            "• `/alltasks` - View all team members' tasks\n\n"
            "• `/duetasks` - View tasks sorted by due date\n\n"
            "• `/syncokrs` - Sync OKRs from the Google Sheet\n\n"
            "*Task Completion:*\n"
            "When marking a task as done, you'll be prompted to provide a link to your completed work (document, presentation, etc.).\n"
            "This helps with accountability and makes it easier for the team to review your work.\n\n"
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
            
    def alltasks_command(self, update: Update, context: CallbackContext):
        """Handle the /alltasks command to view all users' tasks."""
        try:
            # Log the request
            username = update.effective_user.username
            logging.info(f"User {username} requested all tasks")
            
            try:
                # Get all tasks
                message, reply_markup = self.task_manager.get_all_open_tasks_message()
                
                # Reply with the tasks
                update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error getting all tasks: {str(e)}")
                update.message.reply_text(
                    f"Error retrieving all tasks: {str(e)}"
                )
        except Exception as e:
            logging.error(f"Error in alltasks_command: {str(e)}")
            update.message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )
            
    def duetasks_command(self, update: Update, context: CallbackContext):
        """Handle the /duetasks command to view tasks sorted by due date."""
        try:
            # Log the request
            username = update.effective_user.username
            logging.info(f"User {username} requested tasks sorted by due date")
            
            try:
                # Get tasks sorted by due date
                message, reply_markup = self.task_manager.get_due_tasks_message()
                
                # Reply with the tasks
                update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error getting due tasks: {str(e)}")
                update.message.reply_text(
                    f"Error retrieving tasks by due date: {str(e)}"
                )
        except Exception as e:
            logging.error(f"Error in duetasks_command: {str(e)}")
            update.message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )
    
    def syncokrs_command(self, update: Update, context: CallbackContext):
        """Handle the /syncokrs command to sync OKRs from the Google Sheet and display a summary."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Handling /syncokrs command")
        
        # First, let the user know we're syncing
        update.message.reply_text("🔄 Syncing OKRs from Google Sheet...")
        
        # Sync OKRs
        success = self.okr_manager.sync_okrs()
        
        if success:
            # Generate OKR summary
            logger.info("Generating OKR summary")
            summary = self.okr_manager.generate_okr_summary()
            
            # Send the summary
            update.message.reply_text(
                f"✅ OKRs synced successfully!\n\n{summary}",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("OKR summary sent successfully")
        else:
            update.message.reply_text(
                "❌ Failed to sync OKRs. Please check the Google Sheet."
            )
            logger.error("Failed to sync OKRs")
    
    def button_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks."""
        query = update.callback_query
        
        # Get the callback data
        data = query.data
        
        # Handle "done" button clicks
        if data.startswith('done:'):
            task_id = data.replace('done:', '')
            
            # Create inline keyboard with options for link submission
            keyboard = [
                [InlineKeyboardButton("✅ Mark as Done (No Link)", callback_data=f"nolink:{task_id}")],
                [InlineKeyboardButton("📎 Add Link to Completed Work", callback_data=f"addlink:{task_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Acknowledge the callback query
            query.answer()
            
            # Ask user to choose an option
            query.message.reply_text(
                "How would you like to complete this task?",
                reply_markup=reply_markup
            )
        
        # Handle "no link" button clicks
        elif data.startswith('nolink:'):
            task_id = data.replace('nolink:', '')
            query.answer("Marking task as done without a link")
            self.handle_task_done(query, task_id, None)
        
        # Handle "add link" button clicks
        elif data.startswith('addlink:'):
            task_id = data.replace('addlink:', '')
            # Store task_id in context for the conversation
            context.user_data['completing_task_id'] = task_id
            
            # Acknowledge the callback query
            query.answer()
            
            # Ask for a completion link
            query.message.reply_text(
                "📎 Please send a link to your completed work (document, presentation, etc.)"
            )
            
            # Set the conversation state
            context.user_data['awaiting_completion_link'] = True
        
        # Handle OKR update button clicks
        elif data.startswith('okr_'):
            okr_id = data.replace('okr_', '')
            self.handle_okr_update(query, okr_id)
    
    def handle_task_done(self, query, task_id, completion_link=None):
        """Handle marking a task as done with an optional completion link."""
        # Mark the task as done
        success = self.task_manager.mark_task_as_done(task_id, completion_link)
        
        if success:
            # Get task details for a more informative message
            all_tasks = self.sheets_manager.task_log.get_all_records()
            task = next((t for t in all_tasks if t['Task_ID'] == task_id), None)
            
            # Get task description
            task_description = task.get('Description', 'this task') if task else 'this task'
            
            # Send a confirmation message
            if completion_link:
                query.message.reply_text(
                    f"✅ *Task completed successfully!*\n\n"
                    f"📝 *Task:* {task_description}\n"
                    f"🔗 *Submission:* {completion_link}\n\n"
                    f"Great job completing this task!",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                query.message.reply_text(
                    f"✅ *Task completed successfully!*\n\n"
                    f"📝 *Task:* {task_description}\n\n"
                    f"Great job completing this task!",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Edit the original message to show the task as done
            message = query.message.text
            
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
        """Handle text messages."""
        # Get the user's username
        username = update.effective_user.username
        
        if not username:
            update.message.reply_text("Please set a username in your Telegram settings first.")
            return
        
        # Check if we're waiting for a completion link
        if 'awaiting_completion_link' in context.user_data and context.user_data['awaiting_completion_link']:
            # Get the task ID
            task_id = context.user_data.get('completing_task_id')
            
            if task_id:
                # Get the link from the message
                link = update.message.text.strip()
                
                # Validate the link format if provided
                if link.lower() != 'none':
                    # Simple URL validation (starts with http:// or https://)
                    if not (link.startswith('http://') or link.startswith('https://')):
                        update.message.reply_text(
                            "⚠️ Please provide a valid URL starting with http:// or https:// \n"
                            "Or type 'none' if there's no link to share."
                        )
                        return
                else:
                    link = None
                
                # Mark the task as done with the link
                success = self.task_manager.mark_task_as_done(task_id, link)
                
                # Clear the conversation state
                context.user_data.pop('awaiting_completion_link', None)
                context.user_data.pop('completing_task_id', None)
                
                if success:
                    # Get task details for a more informative message
                    all_tasks = self.sheets_manager.task_log.get_all_records()
                    task = next((t for t in all_tasks if t['Task_ID'] == task_id), None)
                    
                    task_description = task.get('Description', 'this task') if task else 'this task'
                    
                    # Format the response message
                    if link and link.lower() != 'none':
                        update.message.reply_text(
                            f"✅ *Task completed successfully!*\n\n"
                            f"📝 *Task:* {task_description}\n"
                            f"🔗 *Submission:* {link}\n\n"
                            f"Great job completing this task!",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    else:
                        update.message.reply_text(
                            f"✅ *Task completed successfully!*\n\n"
                            f"📝 *Task:* {task_description}\n\n"
                            f"Great job completing this task!",
                            parse_mode=ParseMode.MARKDOWN
                        )
                else:
                    update.message.reply_text("❌ Failed to mark task as done. Please try again.")
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
