import streamlit as st
from datetime import datetime, timedelta

# Function to check if a date is a weekend
def is_weekend(date):
    return date.weekday() >= 5

# Function to calculate the last working day and handle notice period and leave balance
def calculate_last_working_day(resignation_date, notice_given, company_notice, leave_balance):
    # Calculate the original last working day based on the resignation date and notice given
    resignation_date = datetime.strptime(resignation_date, '%Y-%m-%d')
    original_last_working_day = resignation_date + timedelta(days=notice_given)

    # Adjust the original last working day to skip weekends
    while is_weekend(original_last_working_day):
        original_last_working_day += timedelta(days=1)

    # Determine if the notice period is short
    notice_short = notice_given < company_notice
    short_days = max(0, company_notice - notice_given)

    # Calculate leave days used to offset the notice period
    leave_days_used = min(short_days, leave_balance)
    remaining_leave_balance = leave_balance - leave_days_used

    # Adjust the last working day for the short notice period
    adjusted_last_working_day = original_last_working_day
    if leave_days_used > 0:
        adjusted_last_working_day += timedelta(days=leave_days_used)
        while is_weekend(adjusted_last_working_day):
            adjusted_last_working_day += timedelta(days=1)

    return {
        'original_last_working_day': original_last_working_day,
        'adjusted_last_working_day': adjusted_last_working_day,
        'notice_short': notice_short,
        'short_days': short_days,
        'leave_days_used': leave_days_used,
        'remaining_leave_balance': remaining_leave_balance
    }

# Streamlit app
st.title('Last Working Day and Notice Period Calculator')

# Input fields
resignation_date = st.date_input('Resignation Date', datetime.today()).strftime('%Y-%m-%d')
notice_given = st.number_input('Notice Period Given by Employee (days)', min_value=0, value=30, step=1)
company_notice = st.number_input('Company Required Notice Period (days)', min_value=0, value=30, step=1)
leave_balance = st.number_input('Employee\'s Current Leave Balance (days)', min_value=0.0, value=10.0, step=0.5)

# Calculate button
if st.button('Calculate'):
    result = calculate_last_working_day(resignation_date, notice_given, company_notice, leave_balance)

    st.write(f"**Original Last Working Day**: {result['original_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Adjusted Last Working Day**: {result['adjusted_last_working_day'].strftime('%Y-%m-%d')}")
    st.write(f"**Notice Period Sufficient**: {'No' if result['notice_short'] else 'Yes'}")
    if result['notice_short']:
        st.write(f"**Days Lacking**: {result['short_days']}")
    st.write(f"**Leave Days Used to Offset Notice**: {result['leave_days_used']}")
    st.write(f"**Remaining Leave Balance**: {result['remaining_leave_balance']}")

# Run the app
# To run this app, save the script as `app.py` and execute `streamlit run app.py` in your terminal.
