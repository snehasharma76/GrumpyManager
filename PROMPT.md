# InternBot Project Prompt

## Project Overview

Create a Telegram bot called "InternBot" designed to help teams manage tasks, track objectives and key results (OKRs), and maintain accountability. The bot will integrate with Google Sheets as its database and provide daily reminders, task management, and progress tracking for team members.

## Core Features

1. **Task Management**
   - Add tasks with priority levels (P1, P2, P3), categories, due dates, and assignees
   - View personal tasks and team-wide tasks
   - Mark tasks as complete with optional completion links
   - View tasks sorted by due date

2. **OKR Tracking**
   - Sync OKRs from a Google Sheet
   - Update OKR progress through the bot
   - Receive intelligent feedback on progress toward goals
   - View OKR summaries

3. **Daily Workflow**
   - Morning planning reminder (10:00 AM IST)
   - Daily nudge for users who haven't added tasks (11:00 AM IST)
   - Midday check-in on task progress (3:00 PM IST)
   - End-of-day summary of completed and pending tasks (7:00 PM IST)

4. **Interactive Commands**
   - `/start` - Introduction to the bot
   - `/help` - List available commands
   - `/task` - Add a new task
   - `/mytasks` - View your assigned tasks
   - `/alltasks` - View all open tasks
   - `/duetasks` - View tasks sorted by due date
   - `/syncokrs` - Sync OKRs from Google Sheet

## Technical Requirements

1. **Programming Language and Libraries**
   - Python 3.9+
   - python-telegram-bot (version 13.7)
   - gspread (version 5.7.2)
   - oauth2client (version 4.1.3)
   - APScheduler (version 3.6.3)
   - pytz (version 2022.7.1)
   - python-dotenv (version 1.0.0)

2. **External Services**
   - Telegram Bot API
   - Google Sheets API

3. **Environment Variables**
   - `TELEGRAM_BOT_TOKEN` - Token from @BotFather
   - `TELEGRAM_GROUP_CHAT_ID` - ID of the group chat
   - `GOOGLE_SHEET_ID` - ID of the Google Sheet
   - `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to Google service account JSON file

4. **Google Sheet Structure**
   - Sheet 1: "Task_Log" with columns for task details
   - Sheet 2: "OKR_Log" with columns for OKR tracking
   - Sheet 3: "Daily_Progress_Log" for OKR updates

## Project Structure

```
InternBot/
├── config/
│   ├── config.py
│   └── credentials.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── bot.py
│   ├── task_manager.py
│   ├── sheets_manager.py
│   ├── okr_manager.py
│   └── logs/
│       └── bot.log
├── .env.example
├── requirements.txt
├── README.md
├── TROUBLESHOOTING.md
└── documentation.md
```

## Detailed Requirements

### 1. Bot Class (bot.py)

Create a main `InternBot` class that:
- Initializes connections to Telegram API and Google Sheets
- Registers command handlers
- Sets up scheduled tasks using APScheduler
- Handles user interactions and button callbacks
- Sends scheduled messages for daily planning, nudges, check-ins, and summaries

### 2. Task Manager (task_manager.py)

Create a `TaskManager` class that:
- Parses task commands with format: `/task [Priority] [Description] -c [Category] -d [Due Date] -a [Assignee]`
- Adds tasks to the Google Sheet
- Retrieves and formats task lists for users
- Marks tasks as complete
- Generates end-of-day summaries with tasks grouped by priority
- Checks which users haven't added tasks today

### 3. Sheets Manager (sheets_manager.py)

Create a `SheetsManager` class that:
- Connects to Google Sheets API
- Initializes worksheet tabs if they don't exist
- Provides methods to add, retrieve, and update tasks
- Manages OKR data and progress tracking
- Handles all direct interactions with the Google Sheets

### 4. OKR Manager (okr_manager.py)

Create an `OKRManager` class that:
- Syncs OKRs from the Google Sheet
- Creates inline keyboards for OKR updates
- Generates OKR summaries
- Calculates progress feedback based on targets and timelines
- Updates OKR progress in the Google Sheet

### 5. Main Application (main.py)

Create a main application that:
- Loads environment variables
- Validates required configuration
- Initializes the bot
- Provides a test mode for checking scheduled tasks
- Handles startup and logging

## Special Requirements and Edge Cases

1. **Error Handling**
   - Implement comprehensive error handling for API calls
   - Log errors with detailed information
   - Provide user-friendly error messages

2. **Message Formatting**
   - Use Markdown for most messages, but handle entity parsing errors
   - For problematic messages like `/alltasks`, strip formatting characters and send without parse_mode
   - Use emojis for priority levels: 🔴 (P1), 🟡 (P2), 🔵 (P3)

3. **Priority Normalization**
   - Normalize priority values to handle variations (e.g., "P1", "1", "p1")
   - Add detailed logging for priority parsing
   - Handle potential spacing issues in Google Sheet column headers

4. **Timezone Handling**
   - Use IST (Asia/Kolkata) timezone for all scheduled tasks
   - Format dates consistently across the application

5. **Test Mode**
   - Implement a test mode that runs scheduled tasks without connecting to Telegram API
   - Enable testing via command-line flag: `python main.py --test`

## Implementation Notes

1. **Task Priority Display**
   - Ensure task priorities are correctly retrieved from Google Sheets
   - Normalize priority values to handle variations
   - Group tasks by priority in end-of-day summaries

2. **Message Formatting**
   - For the `/alltasks` command, remove Markdown formatting and send without parse_mode
   - For other messages, use appropriate parse modes based on content

3. **Scheduled Tasks**
   - Configure APScheduler with proper timezone and misfire grace time
   - Log scheduled job information for debugging
   - Handle potential API rate limits

4. **OKR Progress Calculation**
   - Calculate progress based on start value, target value, and days remaining
   - Provide intelligent feedback on progress and adjusted daily targets
   - Handle edge cases like first day, last day, and calculation errors

5. **Google Sheets Integration**
   - Initialize worksheets with headers if they don't exist
   - Handle potential API errors and retry mechanisms
   - Optimize sheet operations to minimize API calls

## Security Considerations

1. Store sensitive information in environment variables, not in code
2. Use service account authentication for Google Sheets API
3. Validate user inputs to prevent injection attacks
4. Implement proper error handling to avoid exposing sensitive information

## Testing Strategy

1. Implement a test mode to verify scheduled tasks
2. Add comprehensive logging for debugging
3. Create utility scripts for testing specific components
4. Validate edge cases like missing data or API failures

## Prompt Engineering Guide for New Projects

If you're starting with just a high-level idea and want to create an effective prompt that will help you build a robust application while minimizing errors, follow this structured approach:

### 1. Define Your Core Concept

Start with a clear, concise statement of what your application will do:

```
Create a [type of application] that helps [target users] to [primary function] by [key mechanism].

Example: Create a Telegram bot that helps intern teams track tasks and objectives by integrating with Google Sheets and providing daily reminders.
```

### 2. Outline Key Features (Must-Haves vs. Nice-to-Haves)

List the essential features first, then secondary features:

```
Essential Features:
- Feature 1: [Brief description]
- Feature 2: [Brief description]

Nice-to-Have Features:
- Feature 3: [Brief description]
- Feature 4: [Brief description]
```

### 3. Specify Technical Constraints and Preferences

Clearly state any technical requirements or preferences:

```
Technical Requirements:
- Programming Language: [language]
- Framework/Libraries: [if you have preferences]
- External Services: [APIs, databases, etc.]
- Deployment Environment: [where will this run?]
```

### 4. Define User Interactions and Workflows

Describe the main ways users will interact with your application:

```
Key User Workflows:
1. User does X → System responds with Y → User completes Z
2. [Another workflow]
```

### 5. Request Architectural Guidance

Ask for recommendations on project structure and architecture:

```
Please recommend:
- A suitable project structure
- Key components/classes needed
- Data models and relationships
- Error handling strategies
```

### 6. Ask for Potential Challenges and Mitigations

Request proactive identification of potential issues:

```
Please identify potential technical challenges in this project and suggest mitigation strategies for each.
```

### 7. Request Implementation Plan

Ask for a phased approach to building the application:

```
Please provide a step-by-step implementation plan, starting with a minimal viable product and then adding features incrementally.
```

### Example Prompt Template

```markdown
# [Project Name] Development Request

## Core Concept
Create a [type] application that [main purpose].

## Essential Features
- Feature 1: [description]
- Feature 2: [description]
- Feature 3: [description]

## Technical Preferences
- Language: [preference if any, or "please recommend"]
- External Services: [any APIs or services you plan to use]
- Deployment: [where this will run]

## User Workflows
[Describe 1-3 key ways users will interact with your application]

## Questions and Requests
1. What project structure would you recommend?
2. What are the potential technical challenges and how can I mitigate them?
3. Please provide a step-by-step implementation plan.
4. What testing strategies would be most effective for this application?
```

### Tips for Error Prevention

1. **Start Small**: Request a minimal viable product first, then expand
2. **Ask for Logging**: Request comprehensive logging strategies early in development
3. **Request Error Handling**: Ask for robust error handling patterns for external services
4. **Environment Configuration**: Request guidance on environment variables and configuration management
5. **Request Documentation**: Ask for inline documentation of complex logic
6. **Edge Cases**: Ask to identify potential edge cases and how to handle them
7. **Testing Approach**: Request suggestions for testing critical components
