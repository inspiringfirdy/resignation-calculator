import streamlit as st
from datetime import datetime, timedelta

# Function to adjust public holidays
def adjust_public_holidays(public_holidays, rest_days):
    adjusted_holidays = []
    for holiday in public_holidays:
        while holiday.weekday() in rest_days:
            holiday += timedelta(days=1)
        adjusted_holidays.append(holiday)
    return adjusted_holidays

# Function to calculate leave details
def calculate_leave_details(start_of_leave, unused_leave_days, off_days_indexes, public_holidays):
    end_of_leave = start_of_leave
    while unused_leave_days > 0:
        end_of_leave += timedelta(days=1)
        if end_of_leave.weekday() not in off_days_indexes and end_of_leave not in public_holidays:
            unused_leave_days -= 1
    return end_of_leave

st.title("Employee Resignation Calculator")

resignation_type = st.selectbox("Resignation Type", ["Resignation with Notice", "Resignation without Notice", "Dismissal due to Misconduct"])
employee_name = st.text_input("Employee Name", "John Doe")
employee_id = st.text_input("Employee ID", "4200")
notice_accepted_date = st.date_input("Notice Accepted Date", datetime.today())
notice_period = st.selectbox("Notice Period", ["1 month", "2 weeks", "3 months", "Other"])
unused_leave_days = st.number_input("Unused Leave Days", min_value=0, value=0, step=1)
last_physical_working_day = st.date_input("Last Physical Working Day", datetime.today())
off_days = st.multiselect("Rest Days and Off Days", ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], ["saturday", "sunday"])
processor = st.text_input("Processor", "Hairul Izwan Mokhti")
processing_date = st.date_input("Processing Date", datetime.today())

# Define public holidays
public_holidays = [
    datetime(2024, 1, 1), datetime(2024, 1, 25), datetime(2024, 2, 1),
    datetime(2024, 2, 10), datetime(2024, 2, 11), datetime(2024, 2, 12),
    datetime(2024, 3, 28), datetime(2024, 4, 10), datetime(2024, 4, 11),
    datetime(2024, 5, 1), datetime(2024, 5, 22), datetime(2024, 6, 3),
    datetime(2024, 6, 17), datetime(2024, 7, 7), datetime(2024, 7, 8),
    datetime(2024, 8, 31), datetime(2024, 9, 16), datetime(2024, 9, 16),
    datetime(2024, 10, 31), datetime(2024, 12, 25)
]

# Map days to weekdays
day_to_weekday = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

# Convert off days to weekday indices
off_days_indexes = [day_to_weekday[day] for day in off_days]

# Adjust public holidays to consider rest days
adjusted_public_holidays = adjust_public_holidays(public_holidays, off_days_indexes)

# Calculate official last working day
if notice_period == "1 month":
    notice_end_date = notice_accepted_date + timedelta(days=30)
elif notice_period == "2 weeks":
    notice_end_date = notice_accepted_date + timedelta(days=14)
elif notice_period == "3 months":
    notice_end_date = notice_accepted_date + timedelta(days=90)
else:
    notice_end_date = st.date_input("Specify Notice End Date")

official_last_working_day = notice_end_date

# Calculate the number of workdays during the notice period
workdays_during_notice = 0
current_date = notice_accepted_date
while current_date <= last_physical_working_day:
    if current_date.weekday() not in off_days_indexes and current_date not in adjusted_public_holidays:
        workdays_during_notice += 1
    current_date += timedelta(days=1)

# Calculate remaining leave days to extend last physical working day
remaining_leave_days = unused_leave_days - workdays_during_notice
if remaining_leave_days < 0:
    remaining_leave_days = 0

# Calculate the last physical working day with remaining leave days
final_physical_working_day = calculate_leave_details(last_physical_working_day, remaining_leave_days, off_days_indexes, adjusted_public_holidays)

# Calculate short notice to be paid
short_notice_days = (official_last_working_day - final_physical_working_day).days

# Calculate the last payroll date
last_payroll_date = official_last_working_day

# Display results
st.markdown(f"**Official Last Working Day:** {official_last_working_day.strftime('%Y-%m-%d')}")
st.markdown(f"**Last Payroll Date (Salary paid up to):** {last_payroll_date.strftime('%Y-%m-%d')}")
st.markdown(f"**Short Notice to be Paid:** {short_notice_days} days")

# Email template generation
st.markdown("### Email Template")
email_template = f"""
**Subject:** Resignation and Final Employment Details

**Dear {employee_name},**

This email is to confirm the details of your resignation and the final calculations for your last working day, leave balance, and payroll.

**Employee Name:** {employee_name}  
**Employee ID:** {employee_id}

**Resignation Details:**
- Resignation Type: {resignation_type}
- Notice Accepted Date: {notice_accepted_date.strftime('%Y/%m/%d')}
- Notice Required as per Employment Contract: {notice_period}
- Official Last Working Day: {official_last_working_day.strftime('%Y/%m/%d')}
- Last Working Day Requested: {last_physical_working_day.strftime('%Y/%m/%d')}

**Leave and Payroll Details:**
- Leave Balance: {unused_leave_days} days
- Number of Leave Days Used to Offset Short Notice: {workdays_during_notice}
- Number of Leave Days Used to be Cleared During Workdays Throughout Notice Period: {workdays_during_notice}
- Number of Leave Days Used to Extend the Last Physical Working Date: {remaining_leave_days}
- Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%Y/%m/%d')}
- **Short Notice to be Paid:** {short_notice_days} days

You are required to ensure the clearances/actions below are fulfilled to ensure a smooth process:

**Checklist for Resigning Staff:**
- Schedule handover of company property for {last_physical_working_day.strftime('%Y/%m/%d')}
- Return all company property including access cards, keys, and devices
- Ensure all work documents are handed over to the relevant department
- Complete the exit interview as per company policy
- Provide forwarding contact information and address for future correspondence
- Any other questions or clarifications can be sent to hr@telecontinent.com.my

Please let us know if you have any questions or need further clarification.

**Best regards,**

Hairul Izwan Mokhti  
Date Processed: {processing_date.strftime('%Y/%m/%d')}

**Checklist for HR Ops:**
- Prepare acceptance of resignation with last working date as per the final date.
- Clarify that no physical presence is required after {last_physical_working_day.strftime('%Y/%m/%d')}
- Explain continuation of salary and benefits until {last_payroll_date.strftime('%Y/%m/%d')}
- Schedule handover of company property for {last_physical_working_day.strftime('%Y/%m/%d')}
- Arrange for system access and door access termination on {last_physical_working_day.strftime('%Y/%m/%d')}
- Conduct exit interview as per company policy
"""

st.text_area("Generated Email Template", email_template)
