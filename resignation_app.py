from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st

# Define public holidays for Kuala Lumpur in 2024
public_holidays = [
    "01/01/2024", "22/01/2024", "23/01/2024", "01/02/2024", "08/02/2024", "29/03/2024",
    "19/04/2024", "01/05/2024", "20/05/2024", "06/06/2024", "22/08/2024", "31/08/2024",
    "16/09/2024", "14/10/2024", "11/11/2024", "25/12/2024"
]
public_holidays = [datetime.strptime(date, "%d/%m/%Y") for date in public_holidays]

# Mapping of day names to weekday numbers
day_to_weekday = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

# Function to calculate official last working day
def calculate_official_last_working_day(notice_accepted_date, notice_period_str):
    period_value, period_type = notice_period_str.split()
    period_value = int(period_value)

    if period_type.lower() in ["day", "days"]:
        official_last_working_day = notice_accepted_date + timedelta(days=period_value)
    elif period_type.lower() in ["month", "months"]:
        official_last_working_day = notice_accepted_date + relativedelta(months=period_value) - timedelta(days=1)
    else:
        raise ValueError("Invalid notice period format. Use 'days' or 'months'.")

    return official_last_working_day

# Function to adjust public holidays for rest days
def adjust_public_holidays_for_rest_days(public_holidays, off_days, rest_days):
    adjusted_holidays = []
    for holiday in public_holidays:
        if holiday.weekday() in rest_days:
            while holiday.weekday() in rest_days:
                holiday += timedelta(days=1)
        adjusted_holidays.append(holiday)
    return adjusted_holidays

# Function to calculate leave details
def calculate_leave_details(start_of_leave, unused_leave_days, off_days, public_holidays):
    end_of_leave = start_of_leave
    working_days = 0
    
    while working_days < unused_leave_days:
        if end_of_leave.weekday() not in off_days and end_of_leave not in public_holidays:
            working_days += 1
        end_of_leave += timedelta(days=1)
    
    end_of_leave -= timedelta(days=1)
    
    return {
        "Start of Leave": start_of_leave.strftime("%d/%m/%Y"),
        "End of Leave": end_of_leave.strftime("%d/%m/%Y"),
        "Total Working Days on Leave": working_days
    }

# Function to calculate unserved notice days
def calculate_unserved_notice_days(notice_accepted_date, official_last_working_day, last_physical_working_day):
    notice_days_served = (last_physical_working_day - notice_accepted_date).days
    total_notice_days = (official_last_working_day - notice_accepted_date).days

    unserved_notice_days = total_notice_days - notice_days_served
    return unserved_notice_days

# Function to break down unserved notice days by month
def breakdown_unserved_notice_by_month(unserved_notice_days, last_physical_working_day, official_last_working_day):
    breakdown = []
    current_date = last_physical_working_day + timedelta(days=1)
    remaining_days = unserved_notice_days

    while remaining_days > 0:
        next_month = current_date.replace(day=28) + timedelta(days=4)
        days_in_month = (next_month - timedelta(days=next_month.day)).day
        days_remaining_in_month = min(days_in_month - current_date.day + 1, remaining_days)

        breakdown.append(f"{current_date.strftime('%B')} - {days_remaining_in_month} days")
        remaining_days -= days_remaining_in_month
        current_date = (current_date + timedelta(days=days_remaining_in_month)).replace(day=1)

    return breakdown

# Streamlit app
st.title("Employee Resignation Calculator")

resignation_type = st.selectbox("Resignation Type", ["Resignation with Notice"])
employee_name = st.text_input("Employee Name", "John Doe")
employee_id = st.text_input("Employee ID", "4200")
notice_accepted_date = st.date_input("Notice Accepted Date", datetime(2024, 7, 12))
notice_period = st.text_input("Notice Period", "1 month")
unused_leave_days = st.number_input("Unused Leave Days", 0, 100, 50)
last_physical_working_day = st.date_input("Last Physical Working Day", datetime(2024, 7, 25))
off_days = st.text_input("Off Days", "saturday, sunday")
processor = st.selectbox("Processor", ["Hairul Izwan Mokhti", "Norwana Adnan", "Ainur Nashiha", "Hanis Fudhail"])
processing_date = st.date_input("Processing Date", datetime(2024, 7, 12))

# Convert input to correct types
notice_accepted_date = datetime.strptime(str(notice_accepted_date), "%Y-%m-%d")
last_physical_working_day = datetime.strptime(str(last_physical_working_day), "%Y-%m-%d")
off_days_list = [day_to_weekday[day.strip().lower()] for day in off_days.split(",")]

rest_days = [5, 6]  # Assuming rest days are Saturday (5) and Sunday (6)
adjusted_public_holidays = adjust_public_holidays_for_rest_days(public_holidays, off_days_list, rest_days)

if resignation_type == "Resignation with Notice":
    # Perform calculations
    official_last_working_day = calculate_official_last_working_day(notice_accepted_date, notice_period)
    unserved_notice_days = calculate_unserved_notice_days(notice_accepted_date, official_last_working_day, last_physical_working_day)

    unserved_notice_days_covered_by_leave = min(unserved_notice_days, unused_leave_days)
    unserved_notice_days_remaining = unserved_notice_days - unserved_notice_days_covered_by_leave
    unused_leave_balance = unused_leave_days - unserved_notice_days_covered_by_leave

    # Calculate leave days to be cleared during notice period
    workdays_during_notice_period = sum(
        1 for day in (notice_accepted_date + timedelta(days=i) for i in range((last_physical_working_day - notice_accepted_date).days + 1))
        if day.weekday() not in off_days_list and day not in adjusted_public_holidays
    )
    leave_to_clear_during_notice = min(unused_leave_balance, workdays_during_notice_period)

    # Calculate leave days to extend last physical working day
    leave_used_to_extend = unused_leave_balance - leave_to_clear_during_notice
    last_physical_working_day_extended = last_physical_working_day + timedelta(days=leave_used_to_extend)

    final_employment_date = last_physical_working_day_extended
    last_payroll_date = final_employment_date

    leave_used_to_offset_short_notice = unserved_notice_days_covered_by_leave

# Crafting email template
if resignation_type == "Resignation with Notice":
    if unserved_notice_days_remaining > 0:
        breakdown = breakdown_unserved_notice_by_month(unserved_notice_days_remaining, last_physical_working_day, official_last_working_day)
        breakdown_str = "\n".join(breakdown)
        unserved_notice_info = f"- Unserved Notice Period (Days):\n{breakdown_str}\nTotal: {unserved_notice_days_remaining} days, to be recovered from the final wages."
    else:
        unserved_notice_info = ""

    email_template = f"""
Subject: Resignation and Final Employment Details

Dear {employee_name},

This email is to confirm the details of your resignation and the final calculations for your last working day, leave balance, and payroll.

Employee Name: {employee_name}
Employee ID: {employee_id}

Resignation Details:
- Resignation Type: {resignation_type}
- Notice Received on: {notice_accepted_date.strftime('%d/%m/%Y')}
- Notice Required as per Employment Contract: {notice_period}
- Official Last Working Day: {official_last_working_day.strftime('%d/%m/%Y')}
- Last Working Day Requested: {last_physical_working_day.strftime('%d/%m/%Y')}

Leave and Payroll Details:
- LEAVE BALANCE: {unused_leave_days} days
- Number of Leave Days Used to Offset Short Notice: {leave_used_to_offset_short_notice}
- Number of Leave Days Used to be Cleared During Workdays Throughout Notice Period: {leave_to_clear_during_notice}
- Number of Leave Days Used to Extend the Last PHYSICAL Working Date: {leave_used_to_extend}
- Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%d/%m/%Y')}
{unserved_notice_info}

You are required to ensure the clearances/actions below are fulfilled to ensure a smooth process:

Checklist for Resigning Staff:
- [ ] Schedule handover of company property for {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Return all company property including access cards, keys, and devices
- [ ] Ensure all work documents are handed over to the relevant department
- [ ] Complete the exit interview as per company policy
- [ ] Provide forwarding contact information and address for future correspondence
- [ ] Any other questions or clarifications can be sent to hr@telecontinent.com.my

Please let us know if you have any questions or need further clarification.

Best regards,

{processor}
Date Processed: {processing_date.strftime('%d/%m/%Y')}
"""

st.markdown(email_template)

# Checklist for HR Ops
hr_ops_checklist = f"""
Checklist for HR Ops:
- [ ] Prepare acceptance of resignation with last working date as per the final date.
- [ ] Clarify that no physical presence is required after {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Explain continuation of salary and benefits until {final_employment_date.strftime('%d/%m/%Y')}
- [ ] Schedule handover of company property for {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Arrange for system access and door access termination on {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Conduct exit interview as per company policy
"""

st.markdown(hr_ops_checklist)
