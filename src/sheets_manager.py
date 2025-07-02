import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid
import os
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# Get the absolute path to the credentials file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(base_dir, 'config', 'credentials.json')

# Define sheet tab names
TASK_LOG_SHEET = 'Task_Log'
OKR_LOG_SHEET = 'OKR_Log'
DAILY_PROGRESS_LOG_SHEET = 'Daily_Progress_Log'

# Define timezone
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

class SheetsManager:
    """
    Handles all interactions with Google Sheets API for the InternBot.
    """
    def __init__(self):
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        # Authenticate using the service account credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_SERVICE_ACCOUNT_FILE, scope)
        
        # Create a gspread client
        self.client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        self.spreadsheet = self.client.open_by_key(GOOGLE_SHEET_ID)
        
        # Get all worksheet tabs
        self.task_log = self.spreadsheet.worksheet(TASK_LOG_SHEET)
        self.okr_log = self.spreadsheet.worksheet(OKR_LOG_SHEET)
        self.daily_progress_log = self.spreadsheet.worksheet(DAILY_PROGRESS_LOG_SHEET)
        
        # Initialize worksheets if they don't exist or are empty
        self._initialize_worksheets()
    
    def _initialize_worksheets(self):
        """Initialize worksheets with headers if they are empty."""
        # Task Log headers
        task_headers = [
            'Task_ID', 'Task_Description', 'Assigned_To_User', 'Priority', 
            'Category', 'Date_Created', 'Status', 'Date_Completed', 'Due_Date'
        ]
        
        # OKR Log headers
        okr_headers = [
            'OKR_ID', 'Goal_Name', 'Target_Value', 'Start_Value', 
            'Period_Start_Date', 'Period_End_Date'
        ]
        
        # Daily Progress Log headers
        progress_headers = [
            'Date', 'User_Who_Updated', 'OKR_Name', 'Updated_Value'
        ]
        
        # Check and initialize Task Log
        if not self.task_log.get_all_values():
            self.task_log.append_row(task_headers)
        
        # Check and initialize OKR Log
        if not self.okr_log.get_all_values():
            self.okr_log.append_row(okr_headers)
        
        # Check and initialize Daily Progress Log
        if not self.daily_progress_log.get_all_values():
            self.daily_progress_log.append_row(progress_headers)
    
    def add_task(self, task_description, assigned_to, priority, category="General", due_date=None):
        """
        Add a new task to the Task_Log sheet.
        
        Args:
            task_description (str): Description of the task
            assigned_to (str): Telegram username of the person assigned to the task
            priority (str): Priority level (P1, P2, P3)
            category (str, optional): Task category. Defaults to "General".
            due_date (str, optional): Due date for the task in YYYY-MM-DD format. Defaults to None.
        
        Returns:
            str: The ID of the newly created task
        """
        # Generate a unique task ID
        task_id = str(uuid.uuid4())[:8]
        
        # Get current date in IST
        current_date = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepare the row data
        row_data = [
            task_id,
            task_description,
            assigned_to,
            priority,
            category,
            current_date,
            'Open',  # Initial status is always Open
            '',      # Date_Completed is empty initially
            due_date if due_date else ''  # Due date (can be empty)
        ]
        
        # Append the new task to the sheet
        self.task_log.append_row(row_data)
        
        return task_id
    
    def get_user_tasks(self, username, status='Open'):
        """
        Get all tasks for a specific user with a specific status.
        
        Args:
            username (str): Telegram username of the user
            status (str, optional): Task status to filter by. Defaults to 'Open'.
        
        Returns:
            list: List of tasks matching the criteria with all required keys
        """
        try:
            # Log the request for debugging
            import logging
            logging.info(f"Getting {status} tasks for user: {username}")
            
            # Get all tasks
            all_tasks = self.task_log.get_all_records()
            logging.info(f"Total tasks in sheet: {len(all_tasks)}")
            
            # Get column headers to understand the data structure
            headers = self.task_log.row_values(1)
            logging.info(f"Sheet headers: {headers}")
            
            # Filter tasks by username and status and ensure all required keys exist
            user_tasks = []
            required_keys = ['Task_ID', 'Priority', 'Task_Description', 'Category', 'Status', 'Assigned_To_User']
            
            for task in all_tasks:
                try:
                    # Check if this task belongs to the user and has the right status
                    if task.get('Assigned_To_User') == username and task.get('Status') == status:
                        # Create a clean task with all required keys and default values
                        clean_task = {
                            'Task_ID': task.get('Task_ID', f"unknown_{len(user_tasks)}"),
                            'Priority': task.get('Priority', 'P3'),
                            'Task_Description': task.get('Task_Description', 'Untitled Task'),
                            'Category': task.get('Category', 'General'),
                            'Status': task.get('Status', status),
                            'Assigned_To_User': task.get('Assigned_To_User', username),
                            'Date_Added': task.get('Date_Added', ''),
                            'Date_Completed': task.get('Date_Completed', ''),
                            'Due_Date': task.get('Due_Date', '')
                        }
                        user_tasks.append(clean_task)
                except Exception as e:
                    logging.error(f"Error processing task: {e}. Task: {task}")
                    continue
            
            logging.info(f"Found {len(user_tasks)} {status} tasks for {username}")
            return user_tasks
            
        except Exception as e:
            logging.error(f"Error in get_user_tasks: {str(e)}")
            # Return empty list instead of raising exception
            return []
    
    def get_all_open_tasks(self):
        """
        Get all open tasks for all users.
        
        Returns:
            list: List of all open tasks with all required keys
        """
        try:
            import logging
            logging.info("Getting all open tasks")
            
            # Get all tasks
            all_tasks = self.task_log.get_all_records()
            logging.info(f"Total tasks in sheet: {len(all_tasks)}")
            
            # Debug: Log the column headers
            headers = self.task_log.get_all_values()[0] if self.task_log.get_all_values() else []
            logging.info(f"Sheet headers: {headers}")
            
            # Debug: Log a few tasks to see the raw data
            for i, task in enumerate(all_tasks[:3]):
                logging.info(f"Raw task {i+1} data: {task}")
                logging.info(f"Priority in raw data: '{task.get('Priority', 'NOT_FOUND')}'")

            
            # Filter tasks by status and ensure all required keys exist
            open_tasks = []
            
            for task in all_tasks:
                try:
                    # Check if this task has 'Open' status
                    if task.get('Status') == 'Open':
                        # Debug: Log the raw priority value
                        raw_priority = task.get('Priority', 'NOT_FOUND')
                        logging.info(f"Task: {task.get('Task_Description')} - Raw Priority: '{raw_priority}'")
                        
                        # Create a clean task with all required keys and default values
                        username = task.get('Assigned_To_User', 'unassigned')
                        clean_task = {
                            'Task_ID': task.get('Task_ID', f"unknown_{len(open_tasks)}"),
                            'Priority': task.get('Priority', 'P3'),
                            'Task_Description': task.get('Task_Description', 'Untitled Task'),
                            'Category': task.get('Category', 'General'),
                            'Status': 'Open',
                            'Assigned_To_User': username,
                            'Date_Added': task.get('Date_Added', ''),
                            'Date_Completed': task.get('Date_Completed', ''),
                            'Due_Date': task.get('Due_Date', '')
                        }
                        
                        # Debug: Log the clean task priority
                        logging.info(f"Clean task priority: '{clean_task['Priority']}'")
                        open_tasks.append(clean_task)
                except Exception as e:
                    logging.error(f"Error processing task: {e}. Task: {task}")
                    continue
            
            logging.info(f"Found {len(open_tasks)} open tasks")
            
            # Debug: Log priorities of all open tasks
            priorities = [task.get('Priority', 'NONE') for task in open_tasks]
            logging.info(f"All task priorities: {priorities}")
            
            return open_tasks
            
        except Exception as e:
            logging.error(f"Error in get_all_open_tasks: {str(e)}")
            # Return empty list instead of raising exception
            return []
    
    def mark_task_as_done(self, task_id, completion_link=None):
        """
        Mark a task as done in the Task_Log sheet with an optional completion link.
        
        Args:
            task_id (str): ID of the task to mark as done
            completion_link (str, optional): URL to the completed work. Defaults to None.
        
        Returns:
            bool: True if successful, False otherwise
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"SheetsManager: Marking task {task_id} as done in Google Sheets")
        
        # Find the task row
        all_tasks = self.task_log.get_all_records()
        task_row = None
        
        for i, task in enumerate(all_tasks):
            if task['Task_ID'] == task_id:
                # Add 2 to account for header row and 0-indexing
                task_row = i + 2
                break
        
        if task_row:
            # Update the status to 'Done'
            self.task_log.update_cell(task_row, 7, 'Done')
            
            # Update the completion date
            completion_date = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
            self.task_log.update_cell(task_row, 8, completion_date)
            
            # Add completion link if provided
            if completion_link:
                logger.info(f"Processing completion link for task {task_id}")
                # Check if Completion_Link column exists, if not, add it
                headers = self.task_log.row_values(1)
                if 'Completion_Link' not in headers:
                    logger.info("Creating 'Completion_Link' column in Google Sheet")
                    # Add the new column header
                    self.task_log.update_cell(1, len(headers) + 1, 'Completion_Link')
                    logger.info("'Completion_Link' column created successfully")
                else:
                    logger.info("'Completion_Link' column already exists")
                
                # Find the column index for Completion_Link
                completion_link_col = headers.index('Completion_Link') + 1 if 'Completion_Link' in headers else len(headers) + 1
                logger.info(f"Completion_Link column index: {completion_link_col}")
                
                # Update the completion link
                logger.info(f"Storing completion link in cell ({task_row}, {completion_link_col})")
                self.task_log.update_cell(task_row, completion_link_col, completion_link)
                logger.info(f"Completion link stored successfully for task {task_id}")
            
            return True
        
        return False
    
    def get_tasks_completed_today(self):
        """
        Get all tasks that were completed today.
        
        Returns:
            list: List of tasks completed today
        """
        # Get all tasks
        all_tasks = self.task_log.get_all_records()
        
        # Get today's date in IST
        today = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d')
        
        # Filter tasks completed today
        completed_today = [
            task for task in all_tasks 
            if task['Status'] == 'Done' and task['Date_Completed'].startswith(today)
        ]
        
        return completed_today
    
    def get_all_okrs(self):
        """
        Get all OKRs from the OKR_Log sheet.
        
        Returns:
            list: List of all OKRs
        """
        return self.okr_log.get_all_records()
    
    def add_okr_progress(self, username, okr_name, updated_value):
        """
        Add a new OKR progress entry to the Daily_Progress_Log sheet.
        
        Args:
            username (str): Telegram username of the person updating the OKR
            okr_name (str): Name of the OKR being updated
            updated_value (str): New value for the OKR
        
        Returns:
            bool: True if successful
        """
        # Get current date in IST
        current_date = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d')
        
        # Prepare the row data
        row_data = [
            current_date,
            username,
            okr_name,
            updated_value
        ]
        
        # Append the new progress entry to the sheet
        self.daily_progress_log.append_row(row_data)
        
        return True
    
    def get_okr_progress(self, okr_name):
        """
        Get the progress history for a specific OKR.
        
        Args:
            okr_name (str): Name of the OKR
        
        Returns:
            list: List of progress entries for the OKR
        """
        # Get all progress entries
        all_progress = self.daily_progress_log.get_all_records()
        
        # Filter by OKR name
        okr_progress = [
            entry for entry in all_progress 
            if entry['OKR_Name'] == okr_name
        ]
        
        return okr_progress
