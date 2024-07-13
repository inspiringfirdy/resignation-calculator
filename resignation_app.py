import streamlit as st
from datetime import datetime, timedelta

# Function to check if a date is a workday
def is_workday(date, off_days, public_holidays):
    if date.weekday() in off_days or date in public_holidays:
        return False
    return True

# Function to calculate leave details
def calculate_leave_details(start_date, notice_period_days, requested_last_day, leave_balance, off_days, public_holidays):
    end_of_notice = start_date + timedelta(days=notice_period_days)
    
    # Calculate served notice period
    served_notice_days = (requested_last_day - start_date).days + 1
    
    # Calculate unserved notice period
    unserved_notice_days = (end_of_notice - requested_last_day).days
    
    # Offset leave balance
    offset_leave_balance = min(unserved_notice_days, leave_balance)
    indemnity_in_lieu_of_notice = max(0, unserved_notice_days - leave_balance)
    
    # Remaining leave balance to be cleared during notice period
    remaining_leave_balance = leave_balance - offset_leave_balance
    
    # Calculate the last physical working day
    workdays = []
    current_date = requested_last_day
    while len(workdays) < remaining_leave_balance:
        if is_workday(current_date, off_days, public_holidays):
            workdays.append(current_date)
        current_date -= timedelta(days=1)
    
    last_physical_working_day = workdays[-1] if workdays else requested_last_day

    return {
        "served_notice_days": served_notice_days,
        "unserved_notice_days": unserved_notice_days,
        "offset_leave_balance": offset_leave_balance,
        "indemnity_in_lieu_of_notice": indemnity_in_lieu_of_notice,
        "remaining_leave_balance": remaining_leave_balance,
        "last_physical_working_day": last_physical_working_day.strftime('%Y/%m/%d'),
        "last_payroll_date": requested_last_day.strftime('%Y/%m/%d')
    }

# Public holidays list (example for Kuala Lumpur)
public_holidays = [
    datetime(2024, 1, 1), datetime(2024, 1, 25), datetime(2024, 2, 1),
    datetime(2024, 2, 10), datetime(2024, 2, 11), datetime(2024, 2, 12),
    datetime(2024, 3, 28), datetime(2024, 4, 10), datetime(2024, 4, 11),
    datetime(2024, 5, 1), datetime(2024, 5, 22), datetime(2024, 6, 3),
    datetime(2024, 6, 17), datetime(2024, 7, 7), datetime(2024, 7, 8),
    datetime(2024, 8, 31), datetime(2024, 9, 16), datetime(2024, 10, 31),
    datetime(2024, 12, 25)
]

# Adjust public holidays if they fall on rest days
adjusted_public_holidays = set(public_holidays)
for holiday in public_holidays:
    if holiday.weekday() in {5, 6}:  # Saturday or Sunday
        next_workday = holiday + timedelta(days=1)
        while next_workday.weekday() in {5, 6} or next_workday in public_holidays:
            next_workday += timedelta(days=1)
        adjusted_public_holidays.add(next_workday)

# Streamlit app
st.title("Employee Resignation Calculator")

# Input fields
resignation_date = st.date_input("Resignation Date", datetime(2024, 7, 15))
notice_period = st.number_input("Notice Period (days)", value=30)
requested_last_day = st.date_input("Requested Last Working Day", datetime(2024, 7, 31))
leave_balance = st.number_input("Leave Balance (days)", value=20)

off_days_input = st.text_input("Enter off days (comma-separated, e.g., 'saturday,sunday')", 'saturday,sunday')
off_days_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
off_days = [off_days_map[day.strip().lower()] for day in off_days_input.split(',') if day.strip().lower() in off_days_map]

# Calculate button
if st.button("Calculate"):
    start_date = datetime.strptime(str(resignation_date), '%Y-%m-%d')
    requested_last_day_dt = datetime.strptime(str(requested_last_day), '%Y-%m-%d')
    
    results = calculate_leave_details(start_date, notice_period, requested_last_day_dt, leave_balance, off_days, adjusted_public_holidays)
    
    st.subheader("Results")
    st.write("Served Notice Days:", results["served_notice_days"])
    st.write("Unserved Notice Days:", results["unserved_notice_days"])
    st.write("Offset Leave Balance:", results["offset_leave_balance"])
    st.write("Indemnity in Lieu of Notice:", results["indemnity_in_lieu_of_notice"])
    st.write("Remaining Leave Balance:", results["remaining_leave_balance"])
    st.write("Last Physical Working Day:", results["last_physical_working_day"])
    st.write("Last Payroll Date:", results["last_payroll_date"])
