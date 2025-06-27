# InternBot - Startup Accountability Partner

A Telegram bot designed to act as an accountability partner for a two-person startup team. The bot manages daily tasks with prioritization, tracks long-term goals (OKRs) synced from a Google Sheet, and logs all activity back to that sheet.

## Features

- **Daily Task Planning**: Automatic morning reminders and task collection
- **Task Management**: Add, view, and complete tasks with priority levels
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

- `/task [Priority] [Task Description] -c [Category]`: Add a new task
  - Priority: P1 (High), P2 (Medium), P3 (Low)
  - Example: `/task P1 Draft new investor email -c Partnerships`
- `/mytasks`: View your open tasks
- `/syncokrs`: Sync OKRs from the Google Sheet

## Scheduled Messages

- **10:00 AM IST**: Daily task planning reminder
- **11:00 AM IST**: Nudge for users who haven't added tasks
- **3:00 PM IST**: Mid-day progress check
- **7:00 PM IST**: End-of-day summary and OKR progress update
