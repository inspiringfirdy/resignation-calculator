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

# Function to calculate last working day and payroll details
def calculate_last_day_and_payroll(notice_date, notice_period, basic_salary, total_leave_balance):
    # Assume full leave utilization during notice period
    leave_utilized_during_notice = 23  # Assuming 23 working days in the notice period
    workdays_per_month = 26
    calendar_days_in_month_june = 30
    calendar_days_in_month_july = 31

    # Calculate remaining leave balance
    remaining_leave_balance = total_leave_balance - leave_utilized_during_notice

    # Calculate daily rates
    daily_rate_encashment = basic_salary / workdays_per_month
    daily_rate_pro_rated = basic_salary / calendar_days_in_month_july

    # Calculate leave encashment amount
    leave_encashment_amount = daily_rate_encashment * remaining_leave_balance

    # Determine original last working day
    notice_date = datetime.strptime(notice_date, '%Y-%m-%d')
    original_last_working_day = notice_date + timedelta(days=notice_period * 30)

    # Extend last working day if necessary
    remaining_leave_days = remaining_leave_balance
    extended_last_working_day = original_last_working_day

    while remaining_leave_days > 0:
        extended_last_working_day += timedelta(days=1)
        # Skip weekends (Saturday and Sunday) and public holidays
        if extended_last_working_day.weekday() < 5 and not is_public_holiday(extended_last_working_day):
            remaining_leave_days -= 1

    # Calculate pro-rated salary for extended period
    extended_days = (extended_last_working_day - original_last_working_day).days
    pro_rated_salary = daily_rate_pro_rated * extended_days

    # Calculate total payment
    total_payment_encashment = basic_salary + leave_encashment_amount
    total_payment_extended = basic_salary + pro_rated_salary

    return {
        "original_last_working_day": original_last_working_day.strftime('%Y-%m-%d'),
        "extended_last_working_day": extended_last_working_day.strftime('%Y-%m-%d'),
        "leave_encashment_amount": leave_encashment_amount,
        "pro_rated_salary": pro_rated_salary,
        "total_payment_encashment": total_payment_encashment,
        "total_payment_extended": total_payment_extended
    }

# Streamlit app
st.title('Last Working Day and Payroll Calculator')

# Input fields
employee_name = st.text_input('Employee Name', 'Kelly Chew Qiao Wei')
employee_number = st.text_input('Employee Number', 'TC2145')
position = st.text_input('Position', 'Customer Management Executive')
project_department = st.text_input('Project/Department', 'SingtelTV Upsell')
notice_date = st.date_input('Notice Date', datetime(2024, 5, 31))
notice_period = st.number_input('Notice Period (months)', 1, format='%d')
basic_salary = st.number_input('Basic Salary (RM)', 3161.09, format='%.2f')
total_leave_balance = st.number_input('Total Leave Balance (days)', 30.50, format='%.2f')

# Calculate button
if st.button('Calculate'):
    result = calculate_last_day_and_payroll(
        notice_date.strftime('%Y-%m-%d'),
        notice_period,
        basic_salary,
        total_leave_balance
    )

    st.write(f"**Original Last Working Day**: {result['original_last_working_day']}")
    st.write(f"**Extended Last Working Day**: {result['extended_last_working_day']}")
    st.write(f"**Leave Encashment Amount**: RM {result['leave_encashment_amount']:.2f}")
    st.write(f"**Pro-rated Salary for Extended Period**: RM {result['pro_rated_salary']:.2f}")
    st.write(f"**Total Payment (Encashment)**: RM {result['total_payment_encashment']:.2f}")
    st.write(f"**Total Payment (Extended)**: RM {result['total_payment_extended']:.2f}")

# Run the app
# To run this app, save the script as `app.py` and execute `streamlit run app.py` in your terminal.
