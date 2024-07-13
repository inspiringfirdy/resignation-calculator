import streamlit as st
from datetime import datetime, timedelta

def calculate_last_working_day(resignation_date, notice_period_days, leave_balance, use_leave_to_offset):
    if use_leave_to_offset:
        total_days = notice_period_days - leave_balance
    else:
        total_days = notice_period_days
    return resignation_date + timedelta(days=total_days)

def main():
    st.title("Resignation Scenarios and Treatments")

    scenarios = [
        "Immediate Resignation",
        "Resignation with Full Notice",
        "Resignation During Probation",
        "Resignation for Immediate Health or Personal Reasons",
        "Resignation with Garden Leave",
        "Mutual Agreement",
        "Resignation with Outstanding Projects",
        "Resignation with Legal or Disciplinary Issues"
    ]

    st.header("Determine Last Working Day Based on Resignation Scenario")
    
    scenario = st.selectbox("Select Resignation Scenario:", scenarios)
    resignation_date = st.date_input("Resignation Date:", datetime.today())
    notice_period_days = st.number_input("Enter Notice Period (in days):", min_value=0, step=1, value=0)
    leave_balance = st.number_input("Enter Leave Balance (in days):", min_value=0, step=1, value=0)
    use_leave_to_offset = st.checkbox("Use leave balance to offset notice period?", value=False)

    last_working_day = calculate_last_working_day(resignation_date, notice_period_days, leave_balance, use_leave_to_offset)

    st.subheader("Resignation Details")
    st.write(f"Resignation Scenario: {scenario}")
    st.write(f"Notice Period (days): {notice_period_days}")
    st.write(f"Leave Balance (days): {leave_balance}")
    st.write(f"Using Leave to Offset Notice Period: {use_leave_to_offset}")
    st.write(f"Last Working Day: {last_working_day.strftime('%Y-%m-%d')}")

    st.subheader("Steps for Handling Resignation")
    steps = [
        "Calculate the required notice period.",
        "Determine if the employee will serve the full notice period or if leave will be used to offset the period.",
        "Calculate the annual leave balance.",
        "Determine if leave can be used to offset the notice period or if it will be forfeited.",
        "Include salary up to the last working day.",
        "Include payment in lieu of notice if applicable.",
        "Include any unused annual leave if company policy allows.",
        "Provide resignation acceptance letter detailing terms.",
        "Ensure proper documentation of the last working day, leave balance, and final payment.",
        "Ensure the employee completes the handover of responsibilities.",
        "Ensure the return of company property.",
        "Ensure all statutory contributions are made up to the official last working day.",
        "Conduct an exit interview if applicable to gather feedback and ensure all administrative matters are settled."
    ]
    for step in steps:
        st.write(f"- {step}")

if __name__ == "__main__":
    main()
