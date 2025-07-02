# Troubleshooting Guide for InternBot

This document contains common errors encountered during setup and operation of InternBot, along with their solutions. This guide covers issues from initial setup to specific functionality problems.

## Dependency Conflicts

### Error: Conflicting APScheduler Versions

**Error Message:**
```
ERROR: Cannot install -r requirements.txt (line 1) and apscheduler==3.9.1 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested apscheduler==3.9.1
    python-telegram-bot 13.7 depends on APScheduler==3.6.3
```

**Explanation:**
This error occurs because the `python-telegram-bot` package (version 13.7) specifically requires `APScheduler` version 3.6.3, but our requirements.txt file was specifying version 3.9.1, causing a dependency conflict.

**Solution:**
Update the requirements.txt file to use APScheduler version 3.6.3 instead of 3.9.1:

```diff
python-telegram-bot==13.7
gspread==5.7.2
oauth2client==4.1.3
- apscheduler==3.9.1
+ apscheduler==3.6.3
pytz==2022.7.1
python-dotenv==1.0.0
```

Then run the installation command again:
```bash
pip3 install -r requirements.txt
```

## Environment Setup Issues

### Error: Missing Environment Variables

**Error Message:**
```
ERROR: Missing required environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_CHAT_ID, GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_FILE
```

**Solution:**
1. Copy the `.env.example` file to create a new `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and fill in the required values:
   - `TELEGRAM_BOT_TOKEN`: Obtain from [@BotFather](https://t.me/botfather) on Telegram
   - `TELEGRAM_GROUP_CHAT_ID`: Add @RawDataBot to your group to get this ID
   - `GOOGLE_SHEET_ID`: The ID from your Google Sheet URL
   - `GOOGLE_SERVICE_ACCOUNT_FILE`: Path to your Google service account JSON file

## Google Sheets API Issues

### Error: Unable to Access Google Sheet

**Error Message:**
```
gspread.exceptions.SpreadsheetNotFound: Spreadsheet not found
```

**Solution:**
1. Verify that the Google Sheet ID in your `.env` file is correct
2. Make sure you've shared the Google Sheet with the email address from your service account JSON file
3. Check that your service account has the necessary permissions

### Error: Invalid Credentials

**Error Message:**
```
google.auth.exceptions.TransportError: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))
```

**Solution:**
1. Verify that your service account JSON file is valid and has the correct permissions
2. Make sure the path to the service account file in your `.env` file is correct
3. Check that the Google Sheets API is enabled in your Google Cloud Console

## Telegram Bot Issues

### Error: Unauthorized

**Error Message:**
```
telegram.error.Unauthorized: Unauthorized
```

**Solution:**
1. Verify that your Telegram Bot Token is correct
2. Make sure the bot has not been revoked or blocked
3. Try creating a new bot with [@BotFather](https://t.me/botfather) if needed

### Error: Chat Not Found

**Error Message:**
```
telegram.error.BadRequest: Chat not found
```

**Solution:**
1. Verify that the `TELEGRAM_GROUP_CHAT_ID` in your `.env` file is correct
2. Make sure the bot has been added to the group chat
3. Ensure the bot has the necessary permissions in the group chat

## Data Retrieval and Processing Issues

### Error: Google Sheet Column Headers with Extra Spaces

**Error Message:**
```
logging.info(f"Task: {task.get('Task_Description')} - Raw Priority: 'NOT_FOUND'")
```

**Explanation:**
This issue occurs when Google Sheet column headers have trailing or leading spaces (e.g., "Priority " instead of "Priority"), causing the data retrieval to fail or return unexpected values. This was particularly problematic for task priorities, where all tasks were incorrectly shown as P3 (low priority) in the end-of-day summary.

**Solution:**
1. Fix the column headers in the Google Sheet by removing extra spaces
2. Add data normalization in the code to handle variations:
   ```python
   normalized_priority = str(priority).upper().strip()
   if normalized_priority in ['P1', '1']:
       p1_tasks.append(task)
   elif normalized_priority in ['P2', '2']:
       p2_tasks.append(task)
   else:  # Default to P3 for any other value
       p3_tasks.append(task)
   ```
3. Add detailed logging to track raw and processed values:
   ```python
   logging.info(f"Task: {task.get('Task_Description')} - Raw Priority: '{raw_priority}'")
   logging.info(f"Clean task priority: '{clean_task['Priority']}'")
   ```

### Error: Missing User in Daily Nudges

**Explanation:**
Some users (e.g., "Sethu") were not receiving daily nudges despite being active team members. This was due to the user having completed tasks for the day, which removed them from the nudge list.

**Solution:**
1. Add detailed logging to track which users are checked for nudges and why they might be excluded:
   ```python
   logger.info(f"Checking users for nudges: {user_list}")
   logger.info(f"Users without tasks today: {users_without_tasks}")
   ```
2. Verify the logic in `check_users_without_tasks` method to ensure it correctly identifies users who need nudges
3. Consider adding configuration options to control nudge behavior (e.g., always nudge certain users)

## Telegram Message Formatting Issues

### Error: Can't Parse Entities in Message

**Error Message:**
```
telegram.error.BadRequest: Can't parse entities in message
```

**Explanation:**
This error occurs when the Telegram API cannot parse the formatting entities (Markdown or HTML) in a message. This was particularly problematic for the `/alltasks` command, which would fail when trying to display formatted task lists with usernames, priorities, and task descriptions.

**Solution:**
1. Remove parse_mode entirely for problematic messages and strip formatting characters:
   ```python
   # Instead of using parse_mode=ParseMode.MARKDOWN
   clean_message = message.replace('**', '').replace('*', '')
   update.message.reply_text(
       clean_message,
       reply_markup=reply_markup
   )
   ```

2. Add fallback mechanisms when sending messages with complex formatting:
   ```python
   try:
       bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)
   except BadRequest as e:
       if "can't parse entities" in str(e).lower():
           # Strip formatting and try again without parse mode
           clean_message = message.replace('**', '').replace('*', '')
           bot.send_message(chat_id, clean_message)
   ```

3. For critical messages, consider using HTML formatting which can be more reliable than Markdown for complex messages:
   ```python
   message = f"<b>Tasks for {username}</b>\n\n"
   bot.send_message(chat_id, message, parse_mode=ParseMode.HTML)
   ```

### Error: Inconsistent Markdown Formatting

**Explanation:**
Inconsistent use of Markdown formatting across the application led to parsing errors. For example, mixing `*single asterisks*` with `**double asterisks**` for bold text, or using Markdown in some places and HTML in others.

**Solution:**
1. Standardize on one formatting approach throughout the application (either Markdown or HTML)
2. For Markdown, be consistent with formatting syntax (e.g., always use `**double asterisks**` for bold)
3. Add a utility function to sanitize messages before sending:
   ```python
   def sanitize_markdown(text):
       # Escape special characters
       special_chars = ['_', '*', '`', '[']
       for char in special_chars:
           text = text.replace(char, f'\\{char}')
       return text
   ```

## File Path and Environment Issues

### Error: Service Account File Not Found

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'credentials.json'
```

**Explanation:**
The application couldn't find the Google service account credentials file due to incorrect path resolution, especially when running the bot from different directories.

**Solution:**
1. Use absolute paths for critical files:
   ```python
   base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(base_dir, 'config', 'credentials.json')
   ```

2. Verify file existence before attempting to use it:
   ```python
   if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
       logger.error(f"Service account file not found at: {GOOGLE_SERVICE_ACCOUNT_FILE}")
       raise FileNotFoundError(f"Google service account file not found")
   ```

3. Add detailed error messages that include the full path being searched:
   ```python
   except FileNotFoundError:
       logger.error(f"Could not find credentials file at {GOOGLE_SERVICE_ACCOUNT_FILE}")
       raise
   ```

### Error: Log Directory Not Found

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'logs/bot.log'
```

**Explanation:**
The application attempts to write logs to a directory that doesn't exist, causing startup failures.

**Solution:**
1. Create the logs directory if it doesn't exist:
   ```python
   # Create logs directory if it doesn't exist
   os.makedirs("logs", exist_ok=True)
   ```

2. Use absolute paths for log files:
   ```python
   log_dir = os.path.join(base_dir, 'logs')
   os.makedirs(log_dir, exist_ok=True)
   log_file = os.path.join(log_dir, 'bot.log')
   ```

## Scheduling and Timezone Issues

### Error: Scheduled Tasks Not Running at Expected Times

**Explanation:**
Scheduled tasks (daily planning, nudges, etc.) were not running at the expected times due to timezone configuration issues or scheduler misfire handling.

**Solution:**
1. Explicitly configure the scheduler with the correct timezone:
   ```python
   self.scheduler = BackgroundScheduler(
       timezone=IST_TIMEZONE,
       job_defaults={'misfire_grace_time': 3600}  # Allow jobs to run up to an hour late
   )
   ```

2. Use timezone-aware datetime objects for all time comparisons:
   ```python
   now = datetime.now(IST_TIMEZONE)
   ```

3. Log scheduled job information for debugging:
   ```python
   for job in self.scheduler.get_jobs():
       logger.info(f"Job scheduled: {job.id}")
       logger.info(f"Next run time: {job.next_run_time}")
   ```

### Error: Missing Daily Nudges for Specific Users

**Explanation:**
Some users were not receiving daily nudges despite being active team members. This was due to incorrect logic in determining which users needed nudges.

**Solution:**
1. Review and fix the logic in the `send_daily_nudge` method:
   ```python
   # Get users who haven't added tasks today
   users_without_tasks = self.task_manager.check_users_without_tasks(active_users)
   logger.info(f"Users without tasks today: {users_without_tasks}")
   ```

2. Add detailed logging to track which users are being checked and why they might be excluded

3. Consider adding configuration options to control nudge behavior
