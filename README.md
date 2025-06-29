# InternBot - Startup Accountability Partner

A Telegram bot designed to act as an accountability partner for a two-person startup team. The bot manages daily tasks with prioritization, tracks long-term goals (OKRs) synced from a Google Sheet, and logs all activity back to that sheet.

## Features

- **Daily Task Planning**: Automatic morning reminders and task collection
- **Task Management**: Add, view, and complete tasks with priority levels
- **Task Assignment**: Assign tasks to teammates for better collaboration
- **Link Submission**: Include links to completed work when marking tasks as done
- **Progress Tracking**: Mid-day and end-of-day check-ins
- **OKR Integration**: Track objectives and key results with Google Sheets
- **Timezone Support**: All scheduled messages in IST (Indian Standard Time)

## Setup Instructions

### Prerequisites

1. Python 3.7+
2. A Telegram Bot Token (obtained from [@BotFather](https://t.me/botfather))
3. Google Cloud Platform service account with Google Sheets API enabled

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your Telegram Bot Token and other required credentials

### Google Sheets Setup

1. Create a new Google Sheet with the following tabs:
   - `Task_Log`: For tracking daily tasks
   - `OKR_Log`: For storing objectives and key results
   - `Daily_Progress_Log`: For tracking daily progress on OKRs
2. Share the Google Sheet with the email address from your service account JSON file

### Running the Bot

```
python src/main.py
```

## Usage

- `/task [Priority] [Task Description] -c [Category] -d [YYYY-MM-DD] -a [Assignee]`: Add a new task
  - Priority: P1 (High), P2 (Medium), P3 (Low)
  - Category: Optional task category (defaults to "General")
  - Due Date: Optional due date in YYYY-MM-DD format
  - Assignee: Optional username to assign the task to (defaults to yourself)
  - Example: `/task P1 Draft new investor email -c Partnerships -d 2025-07-15 -a teammate`
- `/mytasks`: View your open tasks
- `/alltasks`: View all team members' tasks
- `/duetasks`: View tasks sorted by due date
- `/syncokrs`: Sync OKRs from the Google Sheet and display a summary of current progress

## Task Completion

When you click the "Mark as Done" button on a task, you'll be presented with two options:

1. **Mark as Done (No Link)** - Choose this option to complete the task without providing a link

2. **Add Link to Completed Work** - Choose this option if you want to include a link to your work:
   - Enter a valid URL starting with http:// or https://
   - The link will be validated and stored with your completed task
   - You'll receive a confirmation message with your task details

This flexible approach allows you to quickly mark tasks as done or provide documentation of your completed work.

## OKR Management

### Syncing and Viewing OKRs

Use the `/syncokrs` command to:
1. Sync the latest OKR data from your Google Sheet
2. View a comprehensive summary of all active OKRs

The summary includes:
- OKRs grouped by owner
- Complete progress journey for each OKR (start value → current value → target value)
- Progress percentage calculation based on progress from start value to target value
- Timestamp of when the data was last updated

### OKR Structure in Google Sheets

Your OKR sheet should include the following columns:
- `OKR_ID`: Unique identifier for each OKR
- `Goal_Name`: Name or description of the objective
- `Owner`: Person responsible for the OKR
- `Start_Value`: Initial value at the beginning of the period
- `Current_Value`: Current progress value
- `Target_Value`: Target value to achieve
- `Period_Start_Date`: Start date in YYYY-MM-DD format
- `Period_End_Date`: End date in YYYY-MM-DD format

## Scheduled Messages

- **10:00 AM IST**: Daily task planning reminder
- **11:00 AM IST**: Nudge for users who haven't added tasks
- **3:00 PM IST**: Mid-day progress check
- **7:00 PM IST**: End-of-day summary and OKR progress update
