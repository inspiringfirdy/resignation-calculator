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

def calculate_last_working_day(resignation_date, notice_period_days, requested_last_working_day, leave_balance):
    # Convert inputs to datetime objects
    resignation_date = datetime.strptime(resignation_date, '%Y-%m-%d')
    requested_last_working_day = datetime.strptime(requested_last_working_day, '%Y-%m-%d')

    # Calculate the official last working day based on the company's required notice period
    official_last_working_day = resignation_date + timedelta(days=notice_period_days - 1)

    # Calculate the actual notice period given by the employee
    actual_notice_period_days = (requested_last_working_day - resignation_date).days + 1

    # Determine if the notice period is short
    notice_short = actual_notice_period_days < notice_period_days
    short_days = (notice_period_days - actual_notice_period_days) if notice_short else 0

    # Calculate leave days used to offset the notice period (leave clearance follows working days)
    leave_days_used = 0
    if notice_short:
        remaining_short_days = short_days
        current_date = requested_last_working_day
        while remaining_short_days > 0 and leave_balance > 0:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5 and not is_public_holiday(current_date):
                leave_days_used += 1
                remaining_short_days -= 1
                leave_balance -= 1

    # Adjust the last working day for the short notice period
    adjusted_last_working_day = requested_last_working_day
    if leave_days_used > 0:
        adjusted_last_working_day += timedelta(days=leave_days_used)
        while adjusted_last_working_day.weekday() >= 5 or is_public_holiday(adjusted_last_working_day):
            adjusted_last_working_day += timedelta(days=1)

    return {
        'official_last_working_day': official_last_working_day,
        'requested_last_working_day': requested_last_working_day,
        'adjusted_last_working_day': adjusted_last_working_day,
        'notice_short': notice_short,
        'short_days': short_days,
        'leave_days_used': leave_days_used,
        'remaining_leave_balance': leave_balance
    }

# Streamlit app
st.title('Last Working Day and Notice Period Calculator')

# Input fields as per the provided data
employee_number = st.text_input('Emp No.', 'TC0072')
employee_name = st.text_input('Employee Name', 'Leong Chun Seong')
project = st.text_input('Project', 'SingtelTV')
position = st.text_input('Position', 'Team Leader, Contact Centre Operations')
notice_tendered_on = st.date_input('Notice Tendered on', datetime(2024, 4, 1)).strftime('%Y-%m-%d')
notice_period_months = st.number_input('Notice Period (Months)', 1, format='%d')
last_working_day_requested = st.date_input('Last Working Day Requested', datetime(2024, 5, 28)).strftime('%Y-%m-%d')
leave_balance = st.number_input('Leave Balance (days)', 5.00, format='%.2f')

# Convert notice period in months to days
notice_period_days = notice_period_months * 30

# Calculate button
if st.button('Calculate'):
    result = calculate_last_working_day(
        notice_tendered_on,
        notice_period_days,
        last_working_day_requested,
        leave_balance
    )

    st.write(f"**Official Last Working Day**: {result['official_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Requested Last Working Day**: {result['requested_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Adjusted Last Working Day**: {result['adjusted_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Notice Period Sufficient**: {'No' if result['notice_short'] else 'Yes'}")
    if result['notice_short']:
        st.write(f"**Days Lacking**: {result['short_days']}")
    st.write(f"**Leave Days Used to Offset Notice**: {result['leave_days_used']}")
    st.write(f"**Remaining Leave Balance**: {result['remaining_leave_balance']}")

# Run the app
# To run this app, save the script as `app.py` and execute `streamlit run app.py` in your terminal.
