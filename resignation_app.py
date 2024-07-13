import streamlit as st
from datetime import datetime, timedelta

# Function to calculate the official last day
def calculate_official_last_day(notice_received_date, notice_required_months):
    official_last_day = notice_received_date + timedelta(days=30*notice_required_months)
    return official_last_day - timedelta(days=1)

# Function to calculate total number of days served
def calculate_days_served(notice_served_start_date, notice_served_end_date):
    return (notice_served_end_date - notice_served_start_date).days + 1

# Function to calculate unserved notice days
def calculate_unserved_notice_days(last_working_day, official_last_day):
    return (official_last_day - last_working_day).days

# Streamlit app
st.title("Leave and Notice Period Calculation App")

# Input fields
notice_received_date = st.date_input("Notice Received Date", datetime(2024, 7, 15))
notice_required_months = st.number_input("Notice Required (Months)", min_value=1, max_value=12, value=1)
last_working_day = st.date_input("Last Working Day Requested", datetime(2024, 8, 2))
leave_balance = st.number_input("Leave Balance (Days)", min_value=0, value=20)
off_rest_days = st.text_input("Employee Off & Rest Days", "Saturday & Sunday")

# Calculate results
official_last_day = calculate_official_last_day(notice_received_date, notice_required_months)
notice_served_start_date = notice_received_date
notice_served_end_date = last_working_day
total_days_served = calculate_days_served(notice_served_start_date, notice_served_end_date)
full_notice_period_days = 30 * notice_required_months
unserved_notice_days = calculate_unserved_notice_days(last_working_day, official_last_day)
leave_used_to_offset_notice = min(leave_balance, unserved_notice_days)
updated_leave_balance = leave_balance - leave_used_to_offset_notice
short_notice_days = max(0, unserved_notice_days - leave_used_to_offset_notice)

# Display results
st.subheader("Results")
st.write(f"Official Last Day: {official_last_day.strftime('%d/%m/%Y')}")
st.write(f"Notice Served (Date): {notice_served_start_date.strftime('%d/%m/%Y')} - {notice_served_end_date.strftime('%d/%m/%Y')}")
st.write(f"Total Number of Days Served: {total_days_served} days")
st.write(f"Full Notice Period (Days): {full_notice_period_days} days")
st.write(f"Unserved Notice (Date): {(last_working_day + timedelta(days=1)).strftime('%d/%m/%Y')} - {official_last_day.strftime('%d/%m/%Y')}")
st.write(f"Total Number of Days Unserved: {unserved_notice_days} days")
st.write(f"Total Leave Balance: {leave_balance} days")
st.write(f"Leave Used to Offset Notice: {leave_used_to_offset_notice} days")
st.write(f"Updated Leave Balance: {updated_leave_balance} days")
st.write(f"Short Notice Days (to be recovered through final pay): {short_notice_days} days")

# Options if there is leave balance
if updated_leave_balance > 0:
    st.subheader("Options")
    option = st.radio("Choose an option:", ("Option 1: Clear leave during notice period", "Option 2: Extend last working day"))

    if option == "Option 1: Clear leave during notice period":
        st.write(f"Leave to clear on {(last_working_day - timedelta(days=leave_used_to_offset_notice - 1)).strftime('%d/%m/%Y')} to {last_working_day.strftime('%d/%m/%Y')}")
        st.write(f"Last Physical Date: {(last_working_day - timedelta(days=leave_used_to_offset_notice)).strftime('%d/%m/%Y')}")
        st.write(f"Last Payroll Date: {last_working_day.strftime('%d/%m/%Y')}")
    else:
        extended_last_day = last_working_day + timedelta(days=updated_leave_balance)
        st.write(f"Extend the last working day from {last_working_day + timedelta(days=1)} for {updated_leave_balance} days")
        st.write(f"Last Physical Date: {extended_last_day.strftime('%d/%m/%Y')}")
        st.write(f"Last Payroll Date: {official_last_day.strftime('%d/%m/%Y')}")

# Run the app with: streamlit run leave_calculation_app.py
