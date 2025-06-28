import re
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytz

# Define task priorities
TASK_PRIORITIES = {
    'P1': '🔴',  # High priority
    'P2': '🟡',  # Medium priority
    'P3': '🔵',  # Low priority
}

# Define timezone
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

class TaskManager:
    """
    Handles all task-related operations for the InternBot.
    """
    def __init__(self, sheets_manager):
        """
        Initialize the TaskManager with a SheetsManager instance.
        
        Args:
            sheets_manager: An instance of SheetsManager for Google Sheets operations
        """
        self.sheets_manager = sheets_manager
    
    def parse_task_command(self, command_text):
        """
        Parse a task command to extract priority, description, category, and due date.
        Format: /task [Priority] [Task Description] -c [Category] -d [Due Date]
        
        Args:
            command_text (str): The full command text
        
        Returns:
            tuple: (priority, description, category, due_date) or None if invalid format
        """
        # Remove the '/task' command prefix
        text = command_text.replace('/task', '', 1).strip()
        
        # Extract due date if present
        due_date = None
        due_date_match = re.search(r'-d\s+(\d{4}-\d{2}-\d{2})', text)
        if due_date_match:
            due_date = due_date_match.group(1)
            # Remove the due date part from the text
            text = re.sub(r'-d\s+\d{4}-\d{2}-\d{2}', '', text).strip()
        
        # Check if the text starts with a valid priority
        priority_match = re.match(r'^(P[123])\s+(.+?)(?:\s+-c\s+(.+))?$', text)
        
        if not priority_match:
            return None
        
        priority = priority_match.group(1)
        description = priority_match.group(2).strip()
        category = priority_match.group(3) if priority_match.group(3) else "General"
        
        return priority, description, category, due_date
    
    def add_task(self, username, command_text):
        """
        Add a new task for a user.
        
        Args:
            username (str): Telegram username of the user
            command_text (str): The full command text
        
        Returns:
            tuple: (success, message)
        """
        # Parse the command
        parsed = self.parse_task_command(command_text)
        
        if not parsed:
            return False, "Invalid format. Please use: `/task [Priority] [Description] -c [Category] -d [YYYY-MM-DD]`\nPriority must be P1, P2, or P3."
        
        priority, description, category, due_date = parsed
        
        # Add the task to the sheet
        task_id = self.sheets_manager.add_task(description, username, priority, category, due_date)
        
        # Return success message
        priority_emoji = TASK_PRIORITIES.get(priority, '')
        due_date_msg = f" (Due: {due_date})" if due_date else ""
        return True, f"Task added: {priority_emoji} {description} (Category: {category}){due_date_msg}"
    
    def get_user_tasks_message(self, username):
        """
        Get a formatted message with all open tasks for a user.
        
        Args:
            username (str): Telegram username of the user
        
        Returns:
            tuple: (message_text, inline_keyboard_markup)
        """
        try:
            import logging
            # Validate username
            if not username or not isinstance(username, str):
                return f"Invalid username: {username}. Please set a username in your Telegram settings.", None
                
            # Get all open tasks for the user
            tasks = self.sheets_manager.get_user_tasks(username, status='Open')
            
            if not tasks:
                return f"You (@{username}) have no open tasks.", None
            
            # Create message text
            message = f"📋 *Tasks for @{username}*\n\n"
            
            # Create inline keyboard buttons
            keyboard = []
            
            # Sort tasks by priority (P1 first) with safe handling
            sorted_tasks = []
            for task in tasks:
                # Ensure all required keys exist
                if 'Task_ID' not in task:
                    logging.error(f"Missing Task_ID in task: {task}")
                    continue
                    
                # Set default values for missing keys
                task_id = task.get('Task_ID', 'unknown')
                priority = task.get('Priority', 'P3')
                description = task.get('Task_Description', 'Untitled Task')
                category = task.get('Category', 'General')
                due_date = task.get('Due_Date', '')
                
                # Add to sorted list with priority and due date
                sorted_tasks.append((priority, task_id, description, category, due_date))
            
            # Sort by priority
            sorted_tasks.sort(key=lambda x: x[0])
            
            # Process sorted tasks
            for priority, task_id, description, category, due_date in sorted_tasks:
                priority_emoji = TASK_PRIORITIES.get(priority, '⚪')
                task_text = f"{priority_emoji} {description}"
                
                # Add due date if available
                due_date_text = f" (Due: {due_date})" if due_date else ""
                
                message += f"• {task_text} _{category}_{due_date_text}\n"
                
                # Truncate description if too long
                if len(description) > 20:
                    display_desc = description[:20] + '...'
                else:
                    display_desc = description
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Mark '{display_desc}' as Done", 
                        callback_data=f"done_{task_id}"
                    )
                ])
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            import logging
            logging.error(f"Error in get_user_tasks_message: {str(e)}")
            return f"Error retrieving tasks: {str(e)}", None
    
    def get_due_tasks_message(self):
        """
        Get a formatted message with all open tasks sorted by due date.
        
        Returns:
            tuple: (message_text, inline_keyboard_markup)
        """
        try:
            import logging
            from datetime import datetime
            
            # Get all open tasks
            tasks = self.sheets_manager.get_all_open_tasks()
            
            if not tasks:
                return "There are no open tasks with due dates.", None
            
            # Filter tasks with due dates and sort them
            due_tasks = [task for task in tasks if task.get('Due_Date')]
            
            if not due_tasks:
                return "There are no tasks with due dates set.", None
            
            # Sort tasks by due date (closest first)
            try:
                # Convert string dates to datetime objects for sorting
                for task in due_tasks:
                    if task['Due_Date']:
                        try:
                            task['_due_date_obj'] = datetime.strptime(task['Due_Date'], '%Y-%m-%d')
                        except ValueError:
                            task['_due_date_obj'] = datetime.max  # Far future for invalid dates
                    else:
                        task['_due_date_obj'] = datetime.max  # Far future for tasks with no due date
                
                # Sort by due date
                due_tasks.sort(key=lambda x: x['_due_date_obj'])
            except Exception as e:
                logging.error(f"Error sorting tasks by due date: {str(e)}")
                # If sorting fails, continue with unsorted tasks
            
            # Create message text
            message = "*Tasks By Due Date*\n\n"
            
            # Create inline keyboard buttons
            keyboard = []
            
            # Group tasks by due date
            current_date = None
            for task in due_tasks:
                due_date = task.get('Due_Date', '')
                
                # Add date header if it's a new date
                if due_date != current_date:
                    current_date = due_date
                    message += f"\n*Due: {due_date}*\n"
                
                # Get task details
                username = task.get('Assigned_To_User', 'unassigned')
                priority = task.get('Priority', 'P3')
                description = task.get('Task_Description', 'Untitled Task')
                category = task.get('Category', 'General')
                task_id = task.get('Task_ID', 'unknown')
                
                # Format task
                priority_emoji = TASK_PRIORITIES.get(priority, '⚪')
                task_text = f"{priority_emoji} {description}"
                message += f"• {task_text} (@{username}) _{category}_\n"
                
                # Truncate description if too long
                if len(description) > 15:
                    display_desc = description[:15] + '...'
                else:
                    display_desc = description
                
                # Add a button to mark the task as done
                keyboard.append([
                    InlineKeyboardButton(
                        f"✓ {display_desc} ({username})",
                        callback_data=f"done:{task_id}"
                    )
                ])
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            import logging
            logging.error(f"Error in get_due_tasks_message: {str(e)}")
            return f"Error retrieving tasks by due date: {str(e)}", None
    
    def get_all_open_tasks_message(self):
        """
        Get a formatted message with all open tasks for all users.
        
        Returns:
            tuple: (message_text, inline_keyboard_markup)
        """
        try:
            import logging
            # Get all open tasks
            tasks = self.sheets_manager.get_all_open_tasks()
            
            if not tasks:
                return "There are no open tasks.", None
            
            # Group tasks by user with safe handling
            user_tasks = {}
            for task in tasks:
                # Ensure all required keys exist
                if 'Task_ID' not in task:
                    logging.error(f"Missing Task_ID in task: {task}")
                    continue
                    
                # Set default values for missing keys
                task_id = task.get('Task_ID', 'unknown')
                username = task.get('Assigned_To_User', 'unassigned')
                priority = task.get('Priority', 'P3')
                description = task.get('Task_Description', 'Untitled Task')
                category = task.get('Category', 'General')
                due_date = task.get('Due_Date', '')
                
                # Create a clean task object with defaults
                clean_task = {
                    'Task_ID': task_id,
                    'Assigned_To_User': username,
                    'Priority': priority,
                    'Task_Description': description,
                    'Category': category,
                    'Due_Date': due_date
                }
                
                if username not in user_tasks:
                    user_tasks[username] = []
                user_tasks[username].append(clean_task)
            
            # Sort users alphabetically
            sorted_users = sorted(user_tasks.keys())
            
            # Create message text
            message = "**All Open Tasks**\n\n"
            
            # Create inline keyboard buttons
            keyboard = []
            
            for username in sorted_users:
                # Use a more reliable formatting for usernames
                message += f"\n**@{username}**:\n"
                
                # Sort tasks by priority (P1 first)
                user_tasks[username].sort(key=lambda x: x['Priority'])
                
                for task in user_tasks[username]:
                    priority_emoji = TASK_PRIORITIES.get(task['Priority'], '⚪')
                    task_text = f"{priority_emoji} {task['Task_Description']}"
                    
                    # Add due date if available
                    due_date_text = f" (Due: {task['Due_Date']})" if task['Due_Date'] else ""
                    
                    # Escape any potential problematic characters in task description and category
                    # Use proper Markdown formatting with clear boundaries
                    message += f"• {task_text} _{task['Category']}_"
                    message += f"{due_date_text}\n"
                    
                    # Truncate description if too long
                    description = task['Task_Description']
                    if len(description) > 15:
                        display_desc = description[:15] + '...'
                    else:
                        display_desc = description
                    
                    # Add a button to mark the task as done
                    keyboard.append([
                        InlineKeyboardButton(
                            f"✓ {display_desc} ({username})", 
                            callback_data=f"done:{task['Task_ID']}"
                        )
                    ])
                
                message += "\n"
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logging.error(f"Error in get_all_open_tasks_message: {str(e)}")
            return f"Error retrieving all tasks: {str(e)}", None
    
    def mark_task_as_done(self, task_id):
        """
        Mark a task as done.
        
        Args:
            task_id (str): ID of the task to mark as done
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.sheets_manager.mark_task_as_done(task_id)
    
    def get_end_of_day_summary(self):
        """
        Generate an end-of-day summary message.
        
        Returns:
            str: Formatted end-of-day summary message
        """
        # Get tasks completed today
        completed_tasks = self.sheets_manager.get_tasks_completed_today()
        
        # Get all open tasks
        open_tasks = self.sheets_manager.get_all_open_tasks()
        
        # Group open tasks by priority
        p1_tasks = [t for t in open_tasks if t['Priority'] == 'P1']
        p2_tasks = [t for t in open_tasks if t['Priority'] == 'P2']
        p3_tasks = [t for t in open_tasks if t['Priority'] == 'P3']
        
        # Create the summary message
        message = "🌙 *End of Day Summary* 🌙\n\n"
        
        # Add completed tasks section
        message += "*✅ Tasks Achieved Today:*\n"
        if completed_tasks:
            for task in completed_tasks:
                priority_emoji = TASK_PRIORITIES.get(task['Priority'], '')
                message += f"• @{task['Assigned_To_User']}: {priority_emoji} {task['Task_Description']}\n"
        else:
            message += "No tasks were completed today.\n"
        
        message += "\n*📝 PENDING TASKS (By Priority):*\n"
        
        # Add P1 tasks
        message += "\n*🔴 High-Priority (P1):*\n"
        if p1_tasks:
            for task in p1_tasks:
                message += f"• @{task['Assigned_To_User']}: {task['Task_Description']}\n"
        else:
            message += "No high-priority tasks pending.\n"
        
        # Add P2 tasks
        message += "\n*🟡 Medium-Priority (P2):*\n"
        if p2_tasks:
            for task in p2_tasks:
                message += f"• @{task['Assigned_To_User']}: {task['Task_Description']}\n"
        else:
            message += "No medium-priority tasks pending.\n"
        
        # Add P3 tasks
        message += "\n*🔵 Low-Priority (P3):*\n"
        if p3_tasks:
            for task in p3_tasks:
                message += f"• @{task['Assigned_To_User']}: {task['Task_Description']}\n"
        else:
            message += "No low-priority tasks pending.\n"
        
        message += "\n*OKR Progress Update:* Please provide updates for our goals."
        
        return message
    
    def check_users_without_tasks(self, user_list):
        """
        Check which users haven't added tasks today.
        
        Args:
            user_list (list): List of usernames to check
        
        Returns:
            list: List of usernames who haven't added tasks today
        """
        # Get today's date in IST
        today = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d')
        
        # Get all tasks
        all_tasks = self.sheets_manager.task_log.get_all_records()
        
        # Find users who have added tasks today
        users_with_tasks = set()
        for task in all_tasks:
            if task['Date_Created'].startswith(today) and task['Assigned_To_User'] in user_list:
                users_with_tasks.add(task['Assigned_To_User'])
        
        # Return users who haven't added tasks
        return [user for user in user_list if user not in users_with_tasks]
