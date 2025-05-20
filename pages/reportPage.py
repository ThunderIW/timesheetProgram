import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)



st.image("wieconLogo.png")
roles = st.session_state.get("roles", [])  # ✅ Safely fetch roles or default to empty list
st.title("Report Page")
try:
    if "CEO" in roles:
        st.success("ACCESS GRANTED")
        st.header("Here is the monthly report")
    if st.button("Go back to dashboard"):
        st.switch_page("pages/Admin_page.py")

    authenticator.logout()
    if st.session_state.get("authentication_status") is None:
        st.switch_page("clockInSystem.py")



except TypeError as e:
    error_message=str(e)
    if "NoneType" in error_message:
        st.error("❌ Access denied. You are not authorized to view this page.")
        if st.button("Go Back",type="primary"):
            st.switch_page("clockInSystem.py")



