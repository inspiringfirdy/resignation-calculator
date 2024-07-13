import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Define public holidays for Kuala Lumpur in 2024
public_holidays = [
    "01/01/2024", "22/01/2024", "23/01/2024", "01/02/2024", "08/02/2024", "29/03/2024",
    "19/04/2024", "01/05/2024", "20/05/2024", "06/06/2024", "22/08/2024", "31/08/2024",
    "16/09/2024", "14/10/2024", "11/11/2024", "25/12/2024"  # Add more public holidays if needed
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

def calculate_official_last_working_day(notice_accepted_date, notice_period_str):
    period_value, period_type = notice_period_str.split()
    period_value = int(period_value)

    if period_type.lower() in ["day", "days"]:
        official_last_working_day = notice_accepted_date + timedelta(days=period_value) - timedelta(days=1)
    elif period_type.lower() in ["month", "months"]:
        official_last_working_day = notice_accepted_date + relativedelta(months=period_value) - timedelta(days=1)
    else:
        raise ValueError("Invalid notice period format. Use 'days' or 'months'.")

    return official_last_working_day

def adjust_public_holidays_for_rest_days(public_holidays, off_days, rest_days):
    adjusted_holidays = []
    for holiday in public_holidays:
        if holiday.weekday() in rest_days:
            while holiday.weekday() in rest_days:
                holiday += timedelta(days=1)
        adjusted_holidays.append(holiday)
    return adjusted_holidays

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

def calculate_unserved_notice_days(notice_accepted_date, official_last_working_day, last_physical_working_day):
    notice_days_served = (last_physical_working_day - notice_accepted_date).days
    total_notice_days = (official_last_working_day - notice_accepted_date).days

    unserved_notice_days = total_notice_days - notice_days_served
    return unserved_notice_days

# Streamlit app
st.title("Employee Resignation Calculator")

resignation_type = st.selectbox("Resignation Type", ["Resignation with Notice"])
employee_name = st.text_input("Employee Name", "John Doe")
employee_id = st.text_input("Employee ID", "4200")
notice_accepted_date = st.date_input("Notice Accepted Date", datetime(2024, 7, 12))
notice_period = st.text_input("Notice Period", "1 month")
unused_leave_days = st.number_input("Unused Leave Days (Annual Leave and Replacement Leave)", min_value=0, value=10)
last_physical_working_day = st.date_input("Last Physical Working Day", datetime(2024, 7, 25))
off_days = st.text_input("Off Days", "saturday, sunday")
processor = st.selectbox("Processor", ["Hairul Izwan Mokhti", "Norwana Adnan", "Ainur Nashiha", "Hanis Fudhail"])
processing_date = st.date_input("Processing Date", datetime(2024, 7, 12))
leave_option = st.selectbox("Leave Option", ["Clear leave during notice", "Extend last working day"])

if st.button("Calculate"):
    notice_accepted_date = datetime.strptime(str(notice_accepted_date), "%Y-%m-%d")
    last_physical_working_day = datetime.strptime(str(last_physical_working_day), "%Y-%m-%d")
    off_days_list = [day_to_weekday[day.strip().lower()] for day in off_days.split(",")]

    rest_days = [5, 6]  # Assuming rest days are Saturday (5) and Sunday (6)
    adjusted_public_holidays = adjust_public_holidays_for_rest_days(public_holidays, off_days_list, rest_days)

    official_last_working_day = None
    final_employment_date = None
    last_payroll_date = None
    unserved_notice_info = ""
    leave_used_to_offset_short_notice = 0
    leave_used_to_extend = 0
    unused_leave_balance = 0

    if resignation_type == "Resignation with Notice":
        official_last_working_day = calculate_official_last_working_day(notice_accepted_date, notice_period)
        unserved_notice_days = calculate_unserved_notice_days(notice_accepted_date, official_last_working_day, last_physical_working_day)

        unserved_notice_days_covered_by_leave = min(unserved_notice_days, unused_leave_days)
        unserved_notice_days_remaining = unserved_notice_days - unserved_notice_days_covered_by_leave
        unused_leave_balance = unused_leave_days - unserved_notice_days_covered_by_leave

        if unserved_notice_days_remaining > 0:
            final_employment_date = last_physical_working_day
            last_payroll_date = last_physical_working_day
            unserved_notice_info = f"July: {min(unserved_notice_days_remaining, 31 - last_physical_working_day.day)} days\n"
            if unserved_notice_days_remaining > 31 - last_physical_working_day.day:
                unserved_notice_info += f"August: {unserved_notice_days_remaining - (31 - last_physical_working_day.day)} days\n"
            unserved_notice_info += f"Total: {unserved_notice_days_remaining} days, to be recovered from the final wages."
        else:
            if leave_option == "Clear leave during notice":
                leave_used_to_extend = 0
                remaining_leave_days = unused_leave_balance
                leave_details = calculate_leave_details(last_physical_working_day + timedelta(days=1), remaining_leave_days, off_days_list, adjusted_public_holidays)
                final_employment_date = datetime.strptime(leave_details["End of Leave"], "%d/%m/%Y")
                last_payroll_date = final_employment_date
            else:
                if unused_leave_balance > 0:
                    leave_used_to_extend = unused_leave_balance
                    unused_leave_balance = 0  # All leave is used, no encashment
                    leave_details = calculate_leave_details(official_last_working_day + timedelta(days=1), leave_used_to_extend, off_days_list, adjusted_public_holidays)
                    final_employment_date = datetime.strptime(leave_details["End of Leave"], "%d/%m/%Y")
                else:
                    final_employment_date = official_last_working_day
                last_payroll_date = final_employment_date

    email_template = f"""
Subject: Resignation and Final Employment Details

Dear {employee_name},

This email is to confirm the details of your resignation and the final calculations for your last working day, leave balance, and payroll.

Employee Name: {employee_name}
Employee ID: {employee_id}

Resignation Details:
- Resignation Type: {resignation_type}
- Notice Accepted Date: {notice_accepted_date.strftime('%d/%m/%Y')}
- Official Last Working Day: {official_last_working_day.strftime('%d/%m/%Y') if official_last_working_day else 'N/A'}
- Last Physical Working Day: {last_physical_working_day.strftime('%d/%m/%Y')}

Leave and Payroll Details:
- Number of Leave Days Used to Offset Short Notice: {unserved_notice_days_covered_by_leave}
- Number of Leave to be cleared during notice period: {unused_leave_balance if leave_option == "Clear leave during notice" else 0}
- Final Employment Date (Adjusted Last Working Day): {final_employment_date.strftime('%d/%m/%Y')}
- Last Payroll Date (Salary paid up to): {last_payroll_date.strftime('%d/%m/%Y')}
- Unserved Notice Period (Days): {"0.00, the short notice is covered by the leave balance" if unserved_notice_days_remaining == 0 else f"{unserved_notice_info}"}

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

    st.subheader("Email Template")
    st.text_area("Generated Email Template", email_template, height=200)

    hr_ops_checklist = f"""
Checklist for HR Ops:
- [ ] Prepare acceptance of resignation with last working date as per the final date.
- [ ] Clarify that no physical presence is required after {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Explain continuation of salary and benefits until {final_employment_date.strftime('%d/%m/%Y')}
- [ ] Schedule handover of company property for {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Arrange for system access and door access termination on {last_physical_working_day.strftime('%d/%m/%Y')}
- [ ] Conduct exit interview as per company policy
"""

    st.subheader("Checklist for HR Ops")
    st.text_area("Generated HR Ops Checklist", hr_ops_checklist, height=200)
