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

def calculate_leave_dates_backward(start_date, leave_balance, off_days, rest_days, public_holidays):
    leave_dates = []
    current_date = start_date
    while leave_balance > 0:
        if current_date.weekday() not in off_days and current_date.weekday() not in rest_days and current_date not in public_holidays:
            leave_dates.append(current_date)
            leave_balance -= 1
        current_date -= timedelta(days=1)
    return leave_dates[::-1]  # Reverse to maintain chronological order

def calculate_leave_dates_forward(start_date, leave_balance, off_days, rest_days, public_holidays):
    leave_dates = []
    current_date = start_date
    while leave_balance > 0:
        if current_date.weekday() not in off_days and current_date.weekday() not in rest_days and current_date not in public_holidays:
            leave_dates.append(current_date)
            leave_balance -= 1
        current_date += timedelta(days=1)
    return leave_dates

def adjust_holidays(holidays, off_days, rest_days):
    adjusted_holidays = []
    for holiday in holidays:
        if holiday.weekday() in off_days or holiday.weekday() in rest_days:
            next_working_day = holiday + timedelta(days=1)
            while next_working_day.weekday() in off_days or next_working_day.weekday() in rest_days or next_working_day in holidays:
                next_working_day += timedelta(days=1)
            adjusted_holidays.append(next_working_day)
        else:
            adjusted_holidays.append(holiday)
    return adjusted_holidays

# Input parameters from the user
notice_received_date = st.date_input("Date of Manager Acknowledgement", datetime(2024, 7, 18))
notice_period_months = st.number_input("Notice Period (Months)", value=1, min_value=0)
requested_last_working_day = st.date_input("Requested Last Working Day", datetime(2024, 8, 14))
leave_balance = st.number_input("Leave Balance (Days)", value=2, min_value=0)
off_day = st.selectbox("Off Day", ["Saturday", "Sunday"], index=0)
rest_day = st.selectbox("Rest Day", ["Saturday", "Sunday"], index=1)

# Convert days to weekday indices
off_day_index = 5 if off_day == "Saturday" else 6
rest_day_index = 5 if rest_day == "Saturday" else 6

# Convert dates to datetime objects
notice_received_date = datetime.combine(notice_received_date, datetime.min.time())
requested_last_working_day = datetime.combine(requested_last_working_day, datetime.min.time())

# List of public holidays for Kuala Lumpur in 2024
public_holidays = [
    "01/01/2024", "25/01/2024", "01/02/2024", "10/02/2024", "11/02/2024", "12/02/2024", "28/03/2024",
    "10/04/2024", "11/04/2024", "01/05/2024", "22/05/2024", "03/06/2024", "17/06/2024", "07/07/2024",
    "08/07/2024", "31/08/2024", "16/09/2024", "31/10/2024", "25/12/2024"
]
public_holidays = [datetime.strptime(date, "%d/%m/%Y") for date in public_holidays]

# Adjust public holidays if they fall on rest days or off days
adjusted_public_holidays = adjust_holidays(public_holidays, {off_day_index}, {rest_day_index})

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
    unserved_notice_days = calculate_unserved_notice(unserved_notice_start, unserved_notice_end)
    days_unserved = unserved_notice_days

    leave_used_to_offset_notice = min(leave_balance, days_unserved)
    updated_leave_balance = leave_balance - leave_used_to_offset_notice
    short_notice_days = days_unserved - leave_used_to_offset_notice

    # Set unserved notice dates to "N/A" if there are no unserved days
    unserved_notice_dates_str = "N/A" if days_unserved == 0 else f"{unserved_notice_start.strftime('%d/%m/%Y')} - {unserved_notice_end.strftime('%d/%m/%Y')}"

    # Option handling based on leave balance
    option_1_leave_dates = []
    if leave_balance > 0:
        # Option 1: Clear leave on working days during notice period excluding off days and public holidays
        option_1_leave_dates = calculate_leave_dates_backward(requested_last_working_day - timedelta(days=1), leave_balance, {off_day_index}, {rest_day_index}, adjusted_public_holidays)
        last_physical_date_option_1 = requested_last_working_day - timedelta(days=len(option_1_leave_dates) + 1)
        last_payroll_date_option_1 = requested_last_working_day
    else:
        last_physical_date_option_1 = requested_last_working_day
        last_payroll_date_option_1 = requested_last_working_day

    option_2_extended_dates = []
    if leave_balance > 0:
        # Option 2: Extend the last working day starting from the next working day of the requested last working day
        option_2_extended_dates = calculate_leave_dates_forward(unserved_notice_start, leave_balance, {off_day_index}, {rest_day_index}, adjusted_public_holidays)
        last_physical_date_option_2 = requested_last_working_day
        last_payroll_date_option_2 = option_2_extended_dates[-1] if option_2_extended_dates else requested_last_working_day
    else:
        last_physical_date_option_2 = requested_last_working_day
        last_payroll_date_option_2 = requested_last_working_day

    # Output results
    results = {
        "Official Last Day": official_last_day.strftime("%d/%m/%Y"),
        "Notice Served (Date)": f"{notice_served_start.strftime('%d/%m/%Y')} - {notice_served_end.strftime('%d/%m/%Y')}",
        "Total Number of Days Served": days_served,
        "Full Notice Period (Days)": full_notice_period_days,
        "Unserved Notice (Date)": unserved_notice_dates_str,
        "Total Number of Days Unserved": days_unserved,
        "Total Leave Balance": leave_balance,
        "Leave Used to Offset Notice": leave_used_to_offset_notice,
        "Updated Leave Balance": updated_leave_balance,
        "Short Notice (to be recovered through final pay)": short_notice_days if short_notice_days > 0 else 0,
        "Option 1 Description": "Clear leave on working days during the notice period, excluding off days and public holidays. The last physical working day is the day before the employee starts their leave.",
        "Option 1 Leave Dates": [date.strftime("%d/%m/%Y") for date in option_1_leave_dates],
        "Last Physical Date Option 1": last_physical_date_option_1.strftime("%d/%m/%Y") if last_physical_date_option_1 else None,
        "Last Payroll Date Option 1": last_payroll_date_option_1.strftime("%d/%m/%Y"),
        "Option 2 Description": "Extend the last working day starting from the next working day after the requested last working day, excluding off days and public holidays.",
        "Option 2 Extended Dates": [date.strftime("%d/%m/%Y") for date in option_2_extended_dates],
        "Last Physical Date Option 2": last_physical_date_option_2.strftime("%d/%m/%Y"),
        "Last Payroll Date Option 2": last_payroll_date_option_2.strftime("%d/%m/%Y") if last_payroll_date_option_2 else None,
    }

    # Display results using pandas DataFrame
    results_df = pd.DataFrame(list(results.items()), columns=["Item", "Value"])
    st.table(results_df)

except Exception as e:
    st.error(f"An error occurred: {e}")
