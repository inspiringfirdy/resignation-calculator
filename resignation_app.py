import streamlit as st
from datetime import datetime, timedelta
import calendar
import pandas as pd

# Function to handle date calculations
def add_months(start_date, months):
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def calculate_official_last_day(received_date, period_months):
    return add_months(received_date, period_months) - timedelta(days=1)

def calculate_days_served(start_date, end_date):
    return (end_date - start_date).days + 1

def calculate_unserved_notice(start_date, end_date):
    return (end_date - start_date).days + 1

# Input parameters from the user
notice_received_date = st.date_input("Date of Manager Acknowledgement", datetime(2024, 7, 15))
notice_period_months = st.number_input("Notice Period (Months)", value=1, min_value=0)
requested_last_working_day = st.date_input("Requested Last Working Day", datetime(2024, 8, 2))
leave_balance = st.number_input("Leave Balance (Days)", value=20, min_value=0)
off_days = st.multiselect("Employee Off & Rest Days", ["Saturday", "Sunday"], default=["Saturday", "Sunday"])

# Convert dates to datetime objects
notice_received_date = datetime.combine(notice_received_date, datetime.min.time())
requested_last_working_day = datetime.combine(requested_last_working_day, datetime.min.time())

# Public holidays for Kuala Lumpur in 2024 (example dates)
public_holidays = [
    "01/01/2024", "01/02/2024", "01/05/2024", "22/08/2024", "31/08/2024",
    # Add more public holidays as needed
]
public_holidays = [datetime.strptime(date, "%d/%m/%Y") for date in public_holidays]

# Ensure dates are properly handled and avoid type mismatch
try:
    # Calculations
    official_last_day = calculate_official_last_day(notice_received_date, notice_period_months)
    notice_served_start = notice_received_date
    notice_served_end = requested_last_working_day
    days_served = calculate_days_served(notice_served_start, notice_served_end)
    full_notice_period_days = calculate_days_served(notice_received_date, official_last_day)
    unserved_notice_start = requested_last_working_day + timedelta(days=1)
    unserved_notice_end = official_last_day
    days_unserved = calculate_unserved_notice(unserved_notice_start, unserved_notice_end)

    leave_used_to_offset_notice = min(leave_balance, days_unserved)
    updated_leave_balance = leave_balance - leave_used_to_offset_notice
    short_notice_days = days_unserved - leave_used_to_offset_notice

    # Output results
    results = {
        "Official Last Day": official_last_day.strftime("%d/%m/%Y"),
        "Notice Served (Date)": f"{notice_served_start.strftime('%d/%m/%Y')} - {notice_served_end.strftime('%d/%m/%Y')}",
        "Total Number of Days Served": days_served,
        "Full Notice Period (Days)": full_notice_period_days,
        "Unserved Notice (Date)": f"{unserved_notice_start.strftime('%d/%m/%Y')} - {unserved_notice_end.strftime('%d/%m/%Y')}",
        "Total Number of Days Unserved": days_unserved,
        "Total Leave Balance": leave_balance,
        "Leave Used to Offset Notice": leave_used_to_offset_notice,
        "Updated Leave Balance": updated_leave_balance,
        "Short Notice (to be recovered through final pay)": short_notice_days if short_notice_days > 0 else 0
    }

    # Option handling based on leave balance
    if updated_leave_balance > 0:
        # Option 1: Clear leave on working days during notice period excluding off days and public holidays
        option_1_leave_dates = []
        current_date = notice_served_start
        while len(option_1_leave_dates) < updated_leave_balance and current_date <= notice_served_end:
            if current_date.weekday() < 5 and current_date not in public_holidays:  # Weekday and not a public holiday
                option_1_leave_dates.append(current_date)
            current_date += timedelta(days=1)
        last_physical_date_option_1 = option_1_leave_dates[-1] if option_1_leave_dates else None
        last_payroll_date_option_1 = notice_served_end

        # Option 2: Extend the last working day starting from the next working day of the requested last working day
        option_2_extended_dates = []
        current_date = unserved_notice_start
        while len(option_2_extended_dates) < updated_leave_balance:
            if current_date.weekday() < 5 and current_date not in public_holidays:  # Weekday and not a public holiday
                option_2_extended_dates.append(current_date)
            current_date += timedelta(days=1)
        last_physical_date_option_2 = notice_served_end
        last_payroll_date_option_2 = option_2_extended_dates[-1] if option_2_extended_dates else None

        results.update({
            "Option 1 Leave Dates": [date.strftime("%d/%m/%Y") for date in option_1_leave_dates],
            "Last Physical Date Option 1": last_physical_date_option_1.strftime("%d/%m/%Y") if last_physical_date_option_1 else None,
            "Last Payroll Date Option 1": last_payroll_date_option_1.strftime("%d/%m/%Y"),
            "Option 2 Extended Dates": [date.strftime("%d/%m/%Y") for date in option_2_extended_dates],
            "Last Physical Date Option 2": last_physical_date_option_2.strftime("%d/%m/%Y"),
            "Last Payroll Date Option 2": last_payroll_date_option_2.strftime("%d/%m/%Y") if last_payroll_date_option_2 else None,
        })

    # Display results using pandas DataFrame
    results_df = pd.DataFrame(list(results.items()), columns=["Item", "Value"])
    st.dataframe(results_df)

except Exception as e:
    st.error(f"An error occurred: {e}")
