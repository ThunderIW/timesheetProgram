import streamlit as st
import streamlit_shadcn_ui  as  ui


trigger_button =ui.button(text='trigger_button',key='trigger_button_1')
test=ui.alert_dialog(show=trigger_button, title="Alert Dialog", description="This is an alert dialog", confirm_label="OK", cancel_label="Cancel", key="alert_dialog_1")
