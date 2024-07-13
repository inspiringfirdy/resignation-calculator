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

# Map days to their respective weekday numbers
day_to_weekday = {
    'sunday': 6,
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5
}

# Adjust public holidays if they fall on rest days
def adjust_public_holidays(holidays, rest_days):
    adjusted_holidays = []
    for holiday in holidays:
        if holiday.weekday() in rest_days:
            while holiday.weekday() in rest_days:
                holiday += timedelta(days=1)
        adjusted_holidays.append(holiday)
    return adjusted_holidays

# Create the Streamlit app interface
st.title("Employee Resignation Calculator")

# Input fields for the app
resignation_type = st.selectbox("Resignation Type", ["Resignation with Notice"], key="resignation_type")
employee_name = st.text_input("Employee Name", "John Doe", key="employee_name")
employee_id = st.text_input("Employee ID", "4200", key="employee_id")
notice_accepted_date = st.date_input("Notice Accepted Date", datetime(2024, 7, 12), key="notice_accepted_date")
notice_period = st.text_input("Notice Period", "1 month", key="notice_period")
unused_leave_days = st.number_input("Unused Leave Days", min_value=0, value=50, key="unused_leave_days")
last_physical_working_day = st.date_input("Last Physical Working Day", datetime(2024, 7, 25), key="last_physical_working_day")
off_days = st.multiselect("Off Days", ['saturday', 'sunday'], default=['saturday', 'sunday'], key="off_days")
processor = st.selectbox("Processor", ["Hairul Izwan Mokhti", "Norwana Adnan", "Ainur Nashiha", "Hanis Fudhail"], key="processor")
processing_date = st.date_input("Processing Date", datetime.today(), key="processing_date")

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

# Calculate the number of leave days used during the notice period
leave_used_to_clear_during_notice = min((last_physical_working_day - notice_accepted_date).days + 1, unused_leave_days)

# Calculate the number of leave days used to extend the last working date
leave_days_to_extend = unused_leave_days - leave_used_to_clear_during_notice
final_employment_date = last_physical_working_day + timedelta(days=leave_days_to_extend)

# Calculate the final payroll date
last_payroll_date = calculate_last_payroll_date(last_physical_working_day + timedelta(days=1), leave_days_to_extend, off_days_indexes)

# Display calculated results in the app
st.write(f"Official Last Working Day: {official_last_working_day.strftime('%Y-%m-%d')}")
st.write(f"Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%Y-%m-%d')}")

# Email Template
email_template = f"""
Subject: Resignation and Final Employment Details

Dear {employee_name},

This email is to confirm the details of your resignation and the final calculations for your last working day, leave balance, and payroll.

Employee Name: {employee_name}
Employee ID: {employee_id}

Resignation Details:
- Resignation Type: {resignation_type}
- Notice Accepted Date: {notice_accepted_date.strftime('%d/%m/%Y')}
- Notice Required as per Employment Contract: {notice_period}
- Official Last Working Day: {official_last_working_day.strftime('%d/%m/%Y')}
- Last Working Day Requested: {last_physical_working_day.strftime('%d/%m/%Y')}

Leave and Payroll Details:
LEAVE BALANCE: {unused_leave_days} days
Number of Leave Days Used to Offset Short Notice: 17
Number of Leave Days Used to be Cleared During Workdays Throughout Notice Period: {leave_used_to_clear_during_notice}
Number of Leave Days Used to Extend the Last PHYSICAL Working Date: {leave_days_to_extend}
Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%d/%m/%Y')}

You are required to ensure the clearances/actions below are fulfilled to ensure a smooth process:

Checklist for Resigning Staff:
- Schedule handover of company property for {last_physical_working_day.strftime('%d/%m/%Y')}
- Return all company property including access cards, keys, and devices
- Ensure all work documents are handed over to the relevant department
- Complete the exit interview as per company policy
- Provide forwarding contact information and address for future correspondence
- Any other questions or clarifications can be sent to hr@telecontinent.com.my

Please let us know if you have any questions or need further clarification.

Best regards,

{processor}
Date Processed: {processing_date.strftime('%Y-%m-%d')}
"""

# Display the email template
st.subheader("Email Template:")
st.text_area("Email Content", email_template, height=300)

# Checklist for HR Ops
st.subheader("Checklist for HR Ops:")
st.checkbox("Prepare acceptance of resignation with last working date as per the final date.")
st.checkbox("Clarify that no physical presence is required after the last physical working day.")
st.checkbox("Explain continuation of salary and benefits until the last payroll date.")
st.checkbox("Schedule handover of company property for the last physical working day.")
st.checkbox("Arrange for system access and door access termination on the last physical working day.")
st.checkbox("Conduct exit interview as per company policy.")
