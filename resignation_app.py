import streamlit as st
from datetime import datetime, timedelta

# Function to calculate the results
def calculate_results(notice_received, notice_required, last_working_day_requested, leave_balance, employee_off_days):
    notice_received_date = datetime.strptime(notice_received, "%d/%m/%Y")
    last_working_day_requested_date = datetime.strptime(last_working_day_requested, "%d/%m/%Y")

    # Calculate official last day
    official_last_day = notice_received_date + timedelta(days=notice_required*30 - 1)

    # Calculate notice served dates
    notice_served_start = notice_received_date
    notice_served_end = last_working_day_requested_date
    total_days_served = (notice_served_end - notice_served_start).days + 1

    # Calculate full notice period
    full_notice_period = (official_last_day - notice_received_date).days + 1

    # Calculate unserved notice period
    unserved_notice_start = last_working_day_requested_date + timedelta(days=1)
    unserved_notice_end = official_last_day
    total_days_unserved = (unserved_notice_end - unserved_notice_start).days + 1

    # Calculate leave used to offset notice
    leave_used_to_offset_notice = min(total_days_unserved, leave_balance)

    # Calculate updated leave balance or short notice
    updated_leave_balance = leave_balance - leave_used_to_offset_notice
    short_notice_days = max(0, total_days_unserved - leave_balance)

    # Determine the last physical and payroll dates based on options
    if updated_leave_balance > 0:
        last_physical_date_option1 = last_working_day_requested_date - timedelta(days=updated_leave_balance)
        last_physical_date_option2 = last_working_day_requested_date
        last_payroll_date_option1 = last_working_day_requested_date
        last_payroll_date_option2 = official_last_day
    else:
        last_physical_date_option1 = last_working_day_requested_date
        last_physical_date_option2 = last_working_day_requested_date
        last_payroll_date_option1 = last_working_day_requested_date
        last_payroll_date_option2 = official_last_day

    return {
        "Official Last Day": official_last_day.strftime("%d/%m/%Y"),
        "Notice Served Dates": f"{notice_served_start.strftime('%d/%m/%Y')} - {notice_served_end.strftime('%d/%m/%Y')}",
        "Total Days Served": total_days_served,
        "Full Notice Period": full_notice_period,
        "Unserved Notice Dates": f"{unserved_notice_start.strftime('%d/%m/%Y')} - {unserved_notice_end.strftime('%d/%m/%Y')}",
        "Total Days Unserved": total_days_unserved,
        "Leave Used to Offset Notice": leave_used_to_offset_notice,
        "Updated Leave Balance": updated_leave_balance,
        "Short Notice Days": short_notice_days,
        "Last Physical Date Option 1": last_physical_date_option1.strftime("%d/%m/%Y"),
        "Last Payroll Date Option 1": last_payroll_date_option1.strftime("%d/%m/%Y"),
        "Last Physical Date Option 2": last_physical_date_option2.strftime("%d/%m/%Y"),
        "Last Payroll Date Option 2": last_payroll_date_option2.strftime("%d/%m/%Y"),
    }

# Streamlit application
st.title("Employee Resignation Calculator")

notice_received = st.date_input("Notice Received Date", value=datetime(2024, 7, 15))
notice_required = st.number_input("Notice Required (months)", min_value=1, value=1)
last_working_day_requested = st.date_input("Last Working Day Requested", value=datetime(2024, 8, 2))
leave_balance = st.number_input("Leave Balance (days)", min_value=0, value=20)
employee_off_days = st.text_input("Employee Off & Rest Days", value="Saturday & Sunday")

if st.button("Calculate"):
    results = calculate_results(
        notice_received.strftime("%d/%m/%Y"),
        notice_required,
        last_working_day_requested.strftime("%d/%m/%Y"),
        leave_balance,
        employee_off_days
    )
    
    for key, value in results.items():
        st.write(f"{key}: {value}")
