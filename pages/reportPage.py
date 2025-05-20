import streamlit as st

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit_shadcn_ui as ui
import databaseManagement as db





def create_project_code_plus_name():
    project_list=[]

    for project_name in db.get_project_names():
        project_codes=db.get_projects_code(project_name)
        project_combo=f"{project_codes[0]}: {project_name}"
        project_list.append(project_combo)
    return project_list







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
        if len(create_project_code_plus_name())==0:
            st.warning("No project or issue loading")
        if len (create_project_code_plus_name())>0:

            project_to_view=st.selectbox("Please select the project you want to view",options=[""]+create_project_code_plus_name())

            view_project_btn=ui.button("View project", key='styled_btn_tailwind', class_name="bg-green-800 text-white")

            if view_project_btn and len(project_to_view)>0:
                project_code=project_to_view.split(":")[0]
                st.write(project_to_view)
                st.write(project_code)

            if view_project_btn and len(project_to_view)==0:
                st.error("❌ Please select the project you want to view")
                #st.write(project_to_view)


    if st.button("Go back to dashboard"):
        st.switch_page("pages/Admin_page.py")

    authenticator.logout()
    if st.session_state.get("authentication_status") is None:
        st.switch_page("clockInSystem.py")



except TypeError as e:
    error_message=str(e)
    print(error_message)
    if "NoneType" in error_message:
        st.error("❌ Access denied. You are not authorized to view this page.")
        if st.button("Login",type="secondary"):
            st.switch_page("pages/Admin_page.py")
        if st.button("Go Back",type="primary",):
            st.switch_page("clockInSystem.py")



