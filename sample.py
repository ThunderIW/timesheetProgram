import streamlit as st
import streamlit_shadcn_ui as ui
import streamlit_authenticator as stauth


#clicked = ui.button("Click", key="clk_btn")
#ui.button("Reset", key="reset_btn")
#st.write("UI Button Clicked:", clicked)


from streamlit_datalist import stDatalist

my_selection = stDatalist("This datalist is...", ["great", "cool", "neat"])
st.write(my_selection)