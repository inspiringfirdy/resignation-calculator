import streamlit as st
from datetime import datetime, timedelta

# Define Kuala Lumpur public holidays for 2024
public_holidays = [
    '2024-01-01', '2024-02-01', '2024-02-10', '2024-02-11', '2024-04-24', '2024-05-01', 
    '2024-05-24', '2024-05-25', '2024-06-01', '2024-06-02', '2024-08-31', '2024-09-16', 
    '2024-10-27', '2024-12-25'
]

def is_public_holiday(date):
    date_str = date.strftime('%Y-%m-%d')
    return date_str in public_holidays

def adjust_for_public_holidays(holidays):
    adjusted_holidays = set(holidays)
    for holiday in holidays:
        date = datetime.strptime(holiday, '%Y-%m-%d')
        if date.weekday() == 5:  # Saturday
            adjusted_holidays.add((date + timedelta(days=2)).strftime('%Y-%m-%d'))
        elif date.weekday() == 6:  # Sunday
            adjusted_holidays.add((date + timedelta(days=1)).strftime('%Y-%m-%d'))
    return adjusted_holidays

public_holidays_set = adjust_for_public_holidays(public_holidays)

# Function to calculate last working day and leave clearance/extension
def calculate_last_day_and_leave(notice_date, notice_period, total_leave_balance):
    # Assume 23 working days in the notice period for calculation
    leave_utilized_during_notice = 23  # This is assumed, can be adjusted based on company policy

    # Calculate remaining leave balance
    remaining_leave_balance = total_leave_balance - leave_utilized_during_notice

    # Determine original last working day
    notice_date = datetime.strptime(notice_date, '%Y-%m-%d')
    original_last_working_day = notice_date + timedelta(days=notice_period * 30)

    if remaining_leave_balance <= 0:
        return {
            "message": "The employee clears the leave during the notice period.",
            "original_last_working_day": original_last_working_day.strftime('%Y-%m-%d'),
            "extended_last_working_day": None
        }
    else:
        remaining_leave_days = remaining_leave_balance
        extended_last_working_day = original_last_working_day

        while remaining_leave_days > 0:
            extended_last_working_day += timedelta(days=1)
            # Skip weekends (Saturday and Sunday) and public holidays
            if extended_last_working_day.weekday() < 5 and not is_public_holiday(extended_last_working_day):
                remaining_leave_days -= 1

        return {
            "message": "The employee needs to extend the notice period to clear the leave balance.",
            "original_last_working_day": original_last_working_day.strftime('%Y-%m-%d'),
            "extended_last_working_day": extended_last_working_day.strftime('%Y-%m-%d')
        }

# Streamlit app
st.title('Last Working Day and Leave Clearance Calculator')

# Input fields
employee_name = st.text_input('Employee Name', 'Kelly Chew Qiao Wei')
employee_number = st.text_input('Employee Number', 'TC2145')
position = st.text_input('Position', 'Customer Management Executive')
project_department = st.text_input('Project/Department', 'SingtelTV Upsell')
notice_date = st.date_input('Notice Date', datetime(2024, 5, 31))
notice_period = st.number_input('Notice Period (months)', 1, format='%d')
total_leave_balance = st.number_input('Total Leave Balance (days)', 30.50, format='%.2f')

# Calculate button
if st.button('Calculate'):
    result = calculate_last_day_and_leave(
        notice_date.strftime('%Y-%m-%d'),
        notice_period,
        total_leave_balance
    )

    st.write(f"**Message**: {result['message']}")
    st.write(f"**Original Last Working Day**: {result['original_last_working_day']}")
    if result['extended_last_working_day']:
        st.write(f"**Extended Last Working Day**: {result['extended_last_working_day']}")

# Run the app
# To run this app, save the script as `app.py` and execute `streamlit run app.py` in your terminal.
