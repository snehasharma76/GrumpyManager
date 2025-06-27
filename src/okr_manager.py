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
        # Get all OKRs from the sheet
        all_okrs = self.sheets_manager.get_all_okrs()
        
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
                continue
        
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
