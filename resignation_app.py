import streamlit as st
from datetime import datetime, timedelta

# Define Kuala Lumpur public holidays for 2023
public_holidays = [
    '2024-01-01', '2024-02-01', '2024-02-10', '2024-02-11', '2024-04-24', '2024-05-01', 
    '2024-05-24', '2024-05-25', '2024-06-01', '2024-06-02', '2024-08-31', '2024-09-16', 
    '2024-10-27', '2024-12-25'
]

def is_public_holiday(date):
    date_str = date.strftime('%Y-%m-%d')
    return date_str in public_holidays

# Function to calculate last working day and leave clearance/extension
def calculate_dates(notice_received_date, notice_period_months, requested_last_working_day, leave_balance):
    # Convert inputs to datetime objects
    notice_received_date = datetime.strptime(notice_received_date, '%Y-%m-%d')
    requested_last_working_day = datetime.strptime(requested_last_working_day, '%Y-%m-%d')

    # Calculate the official last working day based on the company's required notice period
    official_last_working_day = notice_received_date + timedelta(days=notice_period_months * 30 - 1)

    # Calculate the actual notice period given by the employee
    actual_notice_period_days = (requested_last_working_day - notice_received_date).days + 1

    # Calculate total number of days served
    total_days_served = actual_notice_period_days

    # Determine if the notice period is short
    full_notice_period_days = (official_last_working_day - notice_received_date).days + 1
    notice_short = actual_notice_period_days < full_notice_period_days
    short_days = (full_notice_period_days - actual_notice_period_days) if notice_short else 0

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

    updated_leave_balance = leave_balance

    return {
        'official_last_working_day': official_last_working_day,
        'requested_last_working_day': requested_last_working_day,
        'adjusted_last_working_day': adjusted_last_working_day,
        'notice_short': notice_short,
        'short_days': short_days,
        'leave_days_used': leave_days_used,
        'updated_leave_balance': updated_leave_balance
    }

# Streamlit app
st.title('Last Working Day and Notice Period Calculator')

# Input fields
employee_number = st.text_input('Emp No.', 'TC0072')
employee_name = st.text_input('Employee Name', 'Leong Chun Seong')
project = st.text_input('Project', 'SingtelTV')
position = st.text_input('Position', 'Team Leader, Contact Centre Operations')
notice_received_date = st.date_input('Notice Received Date', datetime(2024, 7, 15)).strftime('%Y-%m-%d')
notice_period_months = st.number_input('Notice Period (Months)', 1, format='%d')
requested_last_working_day = st.date_input('Last Working Day Requested', datetime(2024, 8, 2)).strftime('%Y-%m-%d')
leave_balance = st.number_input('Leave Balance (days)', 20, format='%.2f')
employee_off_rest_day = st.selectbox('Employee Off & Rest Day', ['Saturday & Sunday'])

# Convert notice period in months to days
notice_period_days = notice_period_months * 30

# Calculate button
if st.button('Calculate'):
    result = calculate_dates(
        notice_received_date,
        notice_period_days,
        requested_last_working_day,
        leave_balance
    )

    st.write(f"**Official Last Working Day**: {result['official_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Requested Last Working Day**: {result['requested_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Adjusted Last Working Day**: {result['adjusted_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Notice Period Sufficient**: {'No' if result['notice_short'] else 'Yes'}")
    if result['notice_short']:
        st.write(f"**Days Lacking**: {result['short_days']}")
    st.write(f"**Leave Days Used to Offset Notice**: {result['leave_days_used']}")
    st.write(f"**Remaining Leave Balance**: {result['updated_leave_balance']}")

    if result['updated_leave_balance'] > 0:
        st.write("**Option 1**: Clear leave on working days during the notice period.")
        leave_clearance_end_date = result['requested_last_working_day'] - timedelta(days=result['leave_days_used'])
        st.write(f"**Leave to clear on**: {leave_clearance_end_date.strftime('%Y-%m-%d')} to {requested_last_working_day}")
        st.write(f"**Last Physical Date**: {leave_clearance_end_date.strftime('%Y-%m-%d')}")
        st.write(f"**Last Payroll Date**: {requested_last_working_day}")

        st.write("**Option 2**: Extend the last working day starting from the next working day of the requested last working day for days mentioned.")
        st.write(f"**Extended Last Working Day**: {result['adjusted_last_working_day'].strftime('%Y-%m-%d')}")
        st.write(f"**Last Payroll Date**: {result['adjusted_last_working_day'].strftime('%Y-%m-%d')}")

# Run the app
# To run this app, save the script as `app.py` and execute `streamlit run app.py` in your terminal.
