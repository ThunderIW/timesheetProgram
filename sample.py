import time
import streamlit as st

# Simulated employee codes
def get_emp_code():
    return ["001", "002", "003", "004"]

# Session state setup
if "emp_code_input" not in st.session_state:
    st.session_state.emp_code_input = ""
if "clocked_in" not in st.session_state:
    st.session_state.clocked_in = False
if "clear_emp_code" not in st.session_state:
    st.session_state.clear_emp_code = False

# Clear the input field after delay
if st.session_state.clear_emp_code:
    st.session_state.emp_code_input = ""
    st.session_state.clocked_in = False
    st.session_state.clear_emp_code = False
    st.rerun()

st.title("🕒 Auto Clock-In System")

# Employee selection (no button needed)
emp_code = st.selectbox(
    "Select your employee code:",
    options=[""] + get_emp_code(),
    key="emp_code_input"
)

# Auto clock-in logic
if emp_code and emp_code != "" and not st.session_state.clocked_in:
    st.session_state.clocked_in = True
    st.success(f"{emp_code} clocked in at {time.strftime('%H:%M:%S')}")
    time.sleep(2)  # show success message briefly
    st.session_state.clear_emp_code = True
    st.rerun()
