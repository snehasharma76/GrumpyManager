# Troubleshooting Guide for InternBot

This document contains common errors encountered during setup and operation of InternBot, along with their solutions.

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
