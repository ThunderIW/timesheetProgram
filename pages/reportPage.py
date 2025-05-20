import streamlit as st

st.image("wieconLogo.png")
roles = st.session_state.get("roles", [])  # ✅ Safely fetch roles or default to empty list
st.title("Report Page")
try:
    if "CEO" in roles:
        st.success("ACCESS GRANTED")
        st.header("Here is the monthly report")


except TypeError as e:
    error_message=str(e)
    if "NoneType" in error_message:
        st.error("❌ Access denied. You are not authorized to view this page.")
        if st.button("Go Back",type="primary"):
            st.switch_page("clockInSystem.py")

