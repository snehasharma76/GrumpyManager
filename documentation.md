# InternBot: Startup Accountability Partner

## Overview
InternBot is a Telegram-based accountability bot designed for small startup teams. It helps manage daily tasks, track OKRs (Objectives and Key Results), and maintain team accountability through scheduled reminders and updates.

## Table of Contents
1. [Core Features](#core-features)
2. [Implementation Status](#implementation-status)
3. [Technical Architecture](#technical-architecture)
4. [Setup and Configuration](#setup-and-configuration)
5. [Usage Guide](#usage-guide)
6. [Future Improvements](#future-improvements)
7. [Known Issues](#known-issues)

## Core Features

### Task Management
- **Task Creation**: Add tasks with priority levels (P1, P2, P3), categories, and due dates
- **Task Viewing**: View personal tasks or all team tasks with due dates
- **Task Completion**: Mark tasks as done with inline buttons
- **Task Summaries**: End-of-day summaries of completed and pending tasks

### OKR Tracking
- **OKR Syncing**: Sync OKRs from Google Sheets
- **Progress Updates**: Update OKR progress interactively
- **Progress Feedback**: Receive motivational and actionable feedback based on progress
- **History Tracking**: Track OKR progress history over time

### Scheduled Reminders
- **Daily Planning** (10:00 AM IST): Morning reminder to plan the day
- **Missing Tasks Check** (11:00 AM IST): Nudge for users without tasks
- **Mid-day Progress** (3:00 PM IST): Check-in on daily progress
- **End-of-day Summary** (7:00 PM IST): Summary of completed tasks and OKR updates

### Integrations
- **Telegram**: User interaction via Telegram bot
- **Google Sheets**: Data storage and retrieval

## Implementation Status

### Completed Features
- ✅ **Bot Framework**: Basic bot setup with command handling
- ✅ **Task Management**:
  - Task creation with priority and category
  - Viewing personal tasks
  - Marking tasks as complete
  - End-of-day task summaries
- ✅ **OKR Tracking**:
  - OKR syncing from Google Sheets
  - Interactive OKR progress updates
  - Progress feedback with motivational messages
- ✅ **Scheduled Messages**:
  - All scheduled messages (10 AM, 11 AM, 3 PM, 7 PM IST)
- ✅ **Error Handling**:
  - Robust error handling for missing data fields
  - Detailed logging for debugging

### In Progress Features
- 🔄 **Testing**: Comprehensive testing of all bot commands and flows
- 🔄 **Documentation**: User guide and developer documentation

### Pending Features
- ✅ **Task Due Dates**: Adding and tracking task due dates
- ❌ **Task Editing**: Ability to edit existing tasks
- ❌ **Task Delegation**: Reassigning tasks to other team members
- ❌ **OKR Creation**: Creating new OKRs via bot commands
- ❌ **Analytics Dashboard**: Visual reports of task completion and OKR progress

## Technical Architecture

### Core Components
1. **bot.py**: Main bot logic, command handlers, and message scheduling
2. **task_manager.py**: Task-related functionality (parsing, adding, listing)
3. **okr_manager.py**: OKR-related functionality (syncing, updating, feedback)
4. **sheets_manager.py**: Google Sheets integration for data storage
5. **main.py**: Entry point that initializes the bot

### Data Structure
1. **Task_Log Sheet**:
   - Task_ID
   - Priority (P1, P2, P3)
   - Task_Description
   - Category
   - Status (Open, Done)
   - Assigned_To_User
   - Date_Added
   - Date_Completed
   - Due_Date

2. **OKR_Log Sheet**:
   - OKR_ID
   - Objective
   - Key_Result
   - Owner
   - Current_Value
   - Target_Value
   - Start_Date
   - Target_Date

### Dependencies
- python-telegram-bot
- gspread
- oauth2client
- python-dotenv
- apscheduler
- pytz

## Setup and Configuration

### Prerequisites
- Python 3.7+
- Telegram Bot Token (from BotFather)
- Google Service Account with access to Google Sheets

### Environment Variables
Create a `.env` file with the following variables:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=your_group_id
GOOGLE_SHEET_ID=your_sheet_id
```

### Google Sheets Setup
1. Create a Google Sheet with two worksheets:
   - Task_Log
   - OKR_Log
2. Set up the columns as described in the Data Structure section
3. Share the sheet with your Google Service Account email

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Place Google service account credentials in `config/credentials.json`
4. Run the bot: `python src/main.py`

## Usage Guide

### Bot Commands
- `/start`: Start the bot and get a welcome message
- `/help`: Display available commands
- `/task [Priority] [Description] -c [Category] -d [YYYY-MM-DD] -a [Assignee]`: Add a new task
  - Example: `/task P1 Draft investor email -c Partnerships -d 2025-07-15 -a teammate`
- `/mytasks`: View your open tasks
- `/alltasks`: View all team members' tasks
- `/duetasks`: View tasks sorted by due date
- `/syncokrs`: Sync OKRs from Google Sheet

### Task Management
1. **Adding Tasks**:
   - Use the `/task` command with priority (P1, P2, P3)
   - Add a category with the `-c` flag (optional, defaults to "General")
   - Add a due date with the `-d` flag in YYYY-MM-DD format (optional)
   - Assign tasks to teammates with the `-a` flag (optional, defaults to yourself)
   - Example: `/task P1 Update website content -c Marketing -d 2025-07-10 -a teammate`

2. **Viewing Tasks**:
   - Use `/mytasks` to see your open tasks
   - Use `/alltasks` to see tasks for all team members
   - Use `/duetasks` to see tasks sorted by upcoming due dates
   - Tasks in `/mytasks` and `/alltasks` are sorted by priority (P1 first)
   - Tasks in `/duetasks` are grouped by due date (earliest first)
   - Each task has a "Mark as Done" button

3. **Completing Tasks**:
   - Click the "Mark as Done" button on any task
   - You'll be prompted to provide a link to your completed work
   - Enter a URL to your document, presentation, or other deliverable
   - If there's no link to share, simply type 'none'
   - The task will be updated in Google Sheets with completion status and link
   - The message will be edited to show completion

### OKR Management
1. **Syncing OKRs**:
   - Use `/syncokrs` to sync OKRs from Google Sheets
   - The bot will confirm successful syncing

2. **Updating OKR Progress**:
   - During end-of-day summary, you'll see OKR update buttons
   - Click on an OKR to update its progress
   - Enter the new progress value when prompted
   - Receive feedback on your progress

## Future Improvements

### Short-term Improvements
1. **Task Enhancements**:
   - Add due dates to tasks
   - Add task priority editing
   - Add task description editing
   - Implement task delegation

2. **OKR Enhancements**:
   - Create OKRs via bot commands
   - Add OKR visualization
   - Implement weekly OKR summaries

3. **User Experience**:
   - Improve error messages
   - Add confirmation messages for actions
   - Implement user settings for notification preferences

### Long-term Vision
1. **Analytics and Insights**:
   - Task completion trends
   - OKR progress visualization
   - Team productivity metrics

2. **Integration Expansions**:
   - Calendar integration for task scheduling
   - Slack/Discord integration
   - Project management tool integration (Asana, Trello, etc.)

3. **Advanced Features**:
   - AI-powered task prioritization suggestions
   - Automated progress reports
   - Team performance analytics

## Known Issues
1. **Error Handling**:
   - Some edge cases in Google Sheets data structure may cause errors
   - Fixed: Missing 'Priority' key in task data now handled properly

2. **Limitations**:
   - No task editing functionality
   - No task due dates
   - OKRs can only be created in Google Sheets, not via bot

3. **Performance**:
   - Large number of tasks or OKRs may slow down response time
   - Google Sheets API rate limits may affect performance during heavy usage

---

*Last Updated: June 28, 2025*
