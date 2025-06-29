from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytz

# Define timezone
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

class OKRManager:
    """
    Handles all OKR-related operations for the InternBot.
    """
    def __init__(self, sheets_manager):
        """
        Initialize the OKRManager with a SheetsManager instance.
        
        Args:
            sheets_manager: An instance of SheetsManager for Google Sheets operations
        """
        self.sheets_manager = sheets_manager
        self.active_okrs = []
        self.sync_okrs()
    
    def sync_okrs(self):
        """
        Sync OKRs from the Google Sheet.
        
        Returns:
            bool: True if successful
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Syncing OKRs from Google Sheet")
        
        # Get all OKRs from the sheet
        all_okrs = self.sheets_manager.get_all_okrs()
        logger.info(f"Retrieved {len(all_okrs)} OKRs from Google Sheet")
        
        # Debug: Print all column names from the first OKR
        if all_okrs:
            logger.info(f"Available columns in OKR sheet: {list(all_okrs[0].keys())}")
            for okr in all_okrs:
                logger.info(f"OKR data: {okr}")
        else:
            logger.warning("No OKRs found in the sheet")
        
        # Filter for active OKRs (current date is between start and end date)
        today = datetime.now(IST_TIMEZONE).date()
        
        self.active_okrs = []
        for okr in all_okrs:
            try:
                start_date = datetime.strptime(okr['Period_Start_Date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(okr['Period_End_Date'], '%Y-%m-%d').date()
                
                if start_date <= today <= end_date:
                    self.active_okrs.append(okr)
            except (ValueError, KeyError):
                # Skip OKRs with invalid date formats
                logger.warning(f"Skipping OKR with invalid date format: {okr.get('Goal_Name', 'Unknown')}")
                continue
        
        logger.info(f"Found {len(self.active_okrs)} active OKRs")
        return True
    
    def get_okr_update_keyboard(self):
        """
        Get an inline keyboard for updating OKRs.
        
        Returns:
            tuple: (message_text, inline_keyboard_markup)
        """
        if not self.active_okrs:
            return "No active OKRs found. Use /syncokrs to refresh from the sheet.", None
        
        # Create message text
        message = "📊 *OKR Progress Update*\n\n"
        message += "Please click on an OKR to update its progress:\n\n"
        
        # Create inline keyboard buttons
        keyboard = []
        
        for okr in self.active_okrs:
            goal_name = okr['Goal_Name']
            target_value = okr['Target_Value']
            
            button_text = f"Update: {goal_name} (Target: {target_value})"
            keyboard.append([
                InlineKeyboardButton(
                    button_text, 
                    callback_data=f"okr_{okr['OKR_ID']}"
                )
            ])
        
        return message, InlineKeyboardMarkup(keyboard)
    
    def generate_okr_summary(self):
        """
        Generate a summary of all active OKRs.
        
        Returns:
            str: Formatted summary of active OKRs
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.active_okrs:
            return "No active OKRs found. Please check the Google Sheet."
        
        # Group OKRs by owner
        okrs_by_owner = {}
        for okr in self.active_okrs:
            owner = okr.get('Owner', 'Unassigned')
            if owner not in okrs_by_owner:
                okrs_by_owner[owner] = []
            okrs_by_owner[owner].append(okr)
        
        # Generate summary
        summary = "📊 *OKR Summary* 📊\n\n"
        
        for owner, okrs in okrs_by_owner.items():
            summary += f"👤 *{owner}*\n"
            
            for okr in okrs:
                # Extract values using the exact column names from the Google Sheet as seen in the screenshot
                goal_name = okr.get('Goal_Name', 'Unnamed Goal')
                # The screenshot shows Target_Value, not Current_Value
                current_value = okr.get('Current_Value', '0')  # We'll need to add this column
                target_value = okr.get('Target_Value', '0')
                start_value = okr.get('Start_Value', '0')
                
                # Log the values for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"OKR values - Goal: {goal_name}, Start: {start_value}, Current: {current_value}, Target: {target_value}")
                
                # Calculate progress percentage based on the difference between current and start values
                # relative to the difference between target and start values
                try:
                    current = float(current_value)
                    target = float(target_value)
                    start = float(start_value)
                    
                    # Calculate the total change needed
                    total_change_needed = target - start
                    
                    # Calculate the change achieved so far
                    change_achieved = current - start
                    
                    if total_change_needed != 0:  # Avoid division by zero
                        progress = (change_achieved / total_change_needed) * 100
                        progress_str = f"{progress:.1f}%"
                    else:
                        progress_str = "N/A"
                except (ValueError, TypeError):
                    progress_str = "N/A"
                
                summary += f"  • {goal_name}: {start_value} → {current_value} → {target_value} ({progress_str})\n"
            
            summary += "\n"
        
        # Add timestamp
        now = datetime.now(IST_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        summary += f"_Last updated: {now}_"
        
        logger.info("Generated OKR summary")
        return summary
    
    def get_okr_by_id(self, okr_id):
        """
        Get an OKR by its ID.
        
        Args:
            okr_id (str): ID of the OKR
        
        Returns:
            dict: OKR data or None if not found
        """
        for okr in self.active_okrs:
            if okr['OKR_ID'] == okr_id:
                return okr
        return None
    
    def calculate_progress_feedback(self, okr, new_value):
        """
        Calculate progress feedback for an OKR update.
        
        Args:
            okr (dict): OKR data
            new_value (float): New value for the OKR
        
        Returns:
            str: Feedback message
        """
        try:
            # Parse values
            target_value = float(okr['Target_Value'])
            start_value = float(okr['Start_Value'])
            current_value = float(new_value)
            
            # Calculate dates
            start_date = datetime.strptime(okr['Period_Start_Date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(okr['Period_End_Date'], '%Y-%m-%d').date()
            today = datetime.now(IST_TIMEZONE).date()
            
            # Calculate progress
            total_days = (end_date - start_date).days
            days_passed = (today - start_date).days
            days_remaining = (end_date - today).days
            
            if days_passed <= 0:
                return f"Great! You're starting with {current_value} for '{okr['Goal_Name']}'."
            
            # Get previous value (most recent update)
            okr_progress = self.sheets_manager.get_okr_progress(okr['Goal_Name'])
            
            if okr_progress:
                # Sort by date (most recent first)
                okr_progress.sort(key=lambda x: x['Date'], reverse=True)
                prev_value = float(okr_progress[0]['Updated_Value'])
                daily_change = current_value - prev_value
            else:
                # If no previous updates, compare with start value
                prev_value = start_value
                daily_change = current_value - prev_value
            
            # Calculate required daily progress
            total_required_change = target_value - start_value
            required_daily_change = total_required_change / total_days
            
            # Calculate today's target
            expected_progress = start_value + (required_daily_change * days_passed)
            
            # Generate feedback
            if daily_change >= 0:
                change_text = f"gained {daily_change:.1f}"
            else:
                change_text = f"lost {abs(daily_change):.1f}"
            
            feedback = f"Great, you {change_text} for '{okr['Goal_Name']}' today. "
            
            if days_remaining > 0:
                # Calculate deficit/surplus
                current_deficit = expected_progress - current_value
                
                if current_deficit > 0:
                    # Behind target
                    new_daily_target = (target_value - current_value) / days_remaining
                    feedback += f"The daily target was {required_daily_change:.1f}. "
                    feedback += f"The deficit of {current_deficit:.1f} will be distributed over the remaining {days_remaining} days. "
                    feedback += f"New daily target: {new_daily_target:.1f}. Keep pushing!"
                else:
                    # Ahead of target
                    feedback += f"You're ahead of schedule by {abs(current_deficit):.1f}! "
                    feedback += f"Keep up the good work!"
            else:
                # Last day
                if current_value >= target_value:
                    feedback += f"Congratulations! You've reached your target of {target_value}!"
                else:
                    feedback += f"The period has ended. Final value: {current_value} / Target: {target_value}"
            
            return feedback
            
        except (ValueError, KeyError, ZeroDivisionError):
            # Fallback for any calculation errors
            return f"Progress updated for '{okr['Goal_Name']}'. New value: {new_value}"
    
    def update_okr_progress(self, username, okr_id, new_value):
        """
        Update the progress of an OKR.
        
        Args:
            username (str): Telegram username of the user
            okr_id (str): ID of the OKR
            new_value (str): New value for the OKR
        
        Returns:
            tuple: (success, feedback_message)
        """
        # Get the OKR
        okr = self.get_okr_by_id(okr_id)
        
        if not okr:
            return False, "OKR not found. Please use /syncokrs to refresh from the sheet."
        
        try:
            # Validate the new value
            float_value = float(new_value)
            
            # Add the progress to the sheet
            self.sheets_manager.add_okr_progress(username, okr['Goal_Name'], new_value)
            
            # Calculate feedback
            feedback = self.calculate_progress_feedback(okr, float_value)
            
            return True, feedback
            
        except ValueError:
            return False, "Please provide a valid number for the OKR value."
