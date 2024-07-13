import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Define public holidays for Kuala Lumpur in 2024
public_holidays = [
    "01/01/2024", "25/01/2024", "01/02/2024", "10/02/2024", "11/02/2024", "12/02/2024", 
    "28/03/2024", "10/04/2024", "11/04/2024", "01/05/2024", "22/05/2024", "03/06/2024",
    "17/06/2024", "07/07/2024", "08/07/2024", "31/08/2024", "16/09/2024", "31/10/2024", 
    "25/12/2024"
]
public_holidays = [datetime.strptime(date, "%d/%m/%Y") for date in public_holidays]

# Adjust public holidays if they fall on rest days
def adjust_public_holidays(holidays, off_days):
    adjusted_holidays = []
    for holiday in holidays:
        if holiday.weekday() in off_days:
            next_day = holiday + timedelta(days=1)
            # Move to the next working day if the next day is also a rest day
            while next_day.weekday() in off_days:
                next_day += timedelta(days=1)
            adjusted_holidays.append(next_day)
        else:
            adjusted_holidays.append(holiday)
    return adjusted_holidays

# Create the Streamlit app interface
st.title("Employee Resignation Calculator")

# Input fields for the app
resignation_type = st.selectbox("Resignation Type", ["Resignation with Notice"])
employee_name = st.text_input("Employee Name", "John Doe")
employee_id = st.text_input("Employee ID", "4200")
notice_accepted_date = st.date_input("Notice Accepted Date", datetime(2024, 7, 12))
notice_period = st.text_input("Notice Period", "1 month")
unused_leave_days = st.number_input("Unused Leave Days", min_value=0, value=50)
last_physical_working_day = st.date_input("Last Physical Working Day", datetime(2024, 7, 25))
off_days = st.multiselect("Off Days", ['saturday', 'sunday'], default=['saturday', 'sunday'])
processor = st.selectbox("Processor", ["Hairul Izwan Mokhti", "Norwana Adnan", "Ainur Nashiha", "Hanis Fudhail"])
processing_date = st.date_input("Processing Date", datetime.today())

# Calculate adjusted public holidays considering rest days
off_days_indexes = [day_to_weekday[day] for day in off_days]
adjusted_public_holidays = adjust_public_holidays(public_holidays, off_days_indexes)

# Perform calculations based on input
# Calculate official last working day
def calculate_last_working_day(accepted_date, period):
    if 'month' in period:
        months = int(period.split()[0])
        return accepted_date + relativedelta(months=months) - timedelta(days=1)
    elif 'day' in period:
        days = int(period.split()[0])
        return accepted_date + timedelta(days=days)

official_last_working_day = calculate_last_working_day(notice_accepted_date, notice_period)

# Calculate last payroll date based on leave extension and adjusted public holidays
def calculate_last_payroll_date(start_date, leave_days, off_days):
    day_count = 0
    current_date = start_date
    while day_count < leave_days:
        if current_date.weekday() not in off_days and current_date not in adjusted_public_holidays:
            day_count += 1
        current_date += timedelta(days=1)
    return current_date - timedelta(days=1)

last_payroll_date = calculate_last_payroll_date(last_physical_working_day + timedelta(days=1), unused_leave_days, off_days_indexes)

# Display calculated results in the app
st.write(f"Official Last Working Day: {official_last_working_day.strftime('%Y-%m-%d')}")
st.write(f"Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%Y-%m-%d')}")

# Create a checklist for HR Ops
st.write("## Checklist for HR Ops")
st.checkbox("Prepare acceptance of resignation with last working day as per the final date.")
st.checkbox("Clarify that no physical presence is required after the last physical working day.")
st.checkbox("Explain continuation of salary and benefits until the last payroll date.")
st.checkbox("Schedule handover of company property for the last physical working day.")
st.checkbox("Arrange for system access and door access termination on the last physical working day.")
st.checkbox("Conduct exit interview as per company policy.")
