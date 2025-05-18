import time
import yaml
import sqlite3
import arrow
import pandas as pd
import streamlit_shadcn_ui as u
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_custom_notification_box import custom_notification_box
import streamlit as st
from streamlit_card import card
from streamlit_autorefresh import st_autorefresh
import databaseManagement as db
from streamlit_datalist import stDatalist
import pygwalker as pyg






def getWorkingTime(type: int):
    correctedFormat = ""
    workingHourFormat = "HH:mm"
    dateFormat = "D MMMM YYYY, h:mm A"
    utc = arrow.utcnow()
    local = utc.to('Asia/Taipei')
    if type == 0:
        correctedFormat = local.format(workingHourFormat)
    if type == 1:
        correctedFormat = local.format(dateFormat)
    return correctedFormat

styles = {
    'material-icons': {'color': 'red'},
    'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
    'notification-text': {'': ''},
    'close-button': {'': ''},
    'link': {'': ''}
}

# Load config and credentials
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Hash passwords if needed
stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

st.image("wieconLogo.png")
st.header('Wiecon Time Management System')

# Login section
try:
    authenticator.login(fields={'Form name': 'Employee login', 'Username': 'Employee code', 'Password': 'Employee password'})

    if st.session_state.get('authentication_status'):
        st.audio("login.wav", format='audio/wav', autoplay=True, )
        username = st.session_state.get('username')
        user_info = config['credentials']['usernames'].get(username, {})
        user_roles = user_info.get('roles', [])

        st.subheader(f"Welcome **{st.session_state.get('name')}**")
        st.write(f"The current date and time is {getWorkingTime(1)}")


        if 'CEO' in user_roles:
            # 🚀 CEO Dashboard
            st.subheader("👔 CEO Dashboard")
            st.success("You are logged in as the CEO.")
            st.write("Access executive tools, reports, and analytics here.")
            # Additional CEO functionality can go here
            st_autorefresh(interval=30000, key="refresh-30s")

            tables_names=db.get_table_names()
            selected_table=st.selectbox("Select a table to view",tables_names)
            current_count = 0
            project_df=db.convertDBToDataframe(selected_table)
            pan_form=project_df.to_pandas()
            if project_df is None or project_df.is_empty():
                st.warning(f"⚠️ No data found or failed to load table: {selected_table}.")

            else:
                st.dataframe(data=project_df, use_container_width=True)
                current_count = len(project_df)
                if u.button("Click here to view data ", key='styled_btn_tailwind', class_name="bg-green-800 text-white"):
                    pyg.walk(pan_form)

            if "last_updated" not in st.session_state:
                st.session_state["last_updated"] = arrow.utcnow()
                st.session_state["last_row_count"] = current_count

            if current_count != st.session_state["last_row_count"]:
                st.session_state["last_updated"] = arrow.utcnow()
                st.session_state["last_row_count"] = current_count

            last_time = st.session_state["last_updated"]
            elapsed = (arrow.utcnow() - last_time).total_seconds()

            st.markdown(f"🕒 **Last update:** {last_time.humanize()} ({last_time.format('YYYY-MM-DD HH:mm:ss')})")



            st.markdown("---")
            st.subheader("💼 Management")

            with st.expander("➕➖ Add or remove  New Project"):
                modeToRemoveProject = st.toggle("Tick to remove project", key="RemoveProject")
                if modeToRemoveProject:
                    with st.form("remove_project_form"):
                        project_names=db.get_project_names()
                        if len(project_names)==0:
                            st.warning("No projects found")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                        else:
                            project_to_remove=stDatalist("Enter the name the name of the project you want to remove",options=project_names)
                            #new_project_name = st.text_input("Enter the project name you want to remove")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')



                else:
                    with st.form("add_project_form"):

                        new_project_name = st.text_input("Enter new project name")
                        project_description=st.text_input("Enter project description")
                        client_info=st.text_input("Client name")
                        submitted = st.form_submit_button("Add Project",type='primary')

                if submitted and modeToRemoveProject==False:
                    db.add_project(new_project_name,project_description)
                    st.success("Project added successfully.")
                    st.rerun()

                if submitted and modeToRemoveProject==True:
                    print(project_to_remove)
                    db.delete_Project_or_delete_emp(project_to_remove,mode=0)
                    st.success(f"{project_to_remove} has been removed successfully.")


            with st.expander(" 🧑‍💼 Employee management"):

                modeToRemoveEmployee = st.toggle("Tick to remove Employee",key="RemoveEmployee")
                emp_names=db.get_employees()
                if modeToRemoveEmployee:
                    with st.form("remove_employee_form"):
                        if len(emp_names) == 0:
                            st.warning("No Employees found")
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee  ", type='primary')
                        else:
                            emp_to_remove = stDatalist("Enter the name the employee of the project you want to remove",
                                                       options=emp_names)
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee ", type='primary')


                        if submittedToRemoveEmp and modeToRemoveEmployee == True:
                            first_name,last_name= emp_to_remove.split(" ")
                            db.delete_Project_or_delete_emp(emp_first_name=first_name,emp_last_name=last_name,mode=1)
                            st.success(f'Employee {emp_to_remove} has been removed successfully')



                else:
                    try:
                        email_of_registered_user, \
                            username_of_registered_user, \
                            name_of_registered_user = authenticator.register_user(password_hint=False, captcha=False,roles=["employee"])
                        if email_of_registered_user:
                            st.success('User registered successfully')
                            first_name,last_name=name_of_registered_user.split(" ")
                            db.insert_new_emp(first_name,last_name,email_of_registered_user)
                    except Exception as e:
                        st.error(e)










                '''
                with st.form("management_form"):
                    employee_first_name = st.text_input("Enter first name")
                    employee_last_name = st.text_input("Enter last name")
                    submitted=st.form_submit_button("Add employee",type='primary')
                

                if submitted:
                    db.insert_new_emp(employee_first_name,employee_last_name)
                    st.success("Employee added successfully.")
                '''








        else:
            # 👷 Standard employee interface
            startTime = getWorkingTime(0)
            employee_id = username
            sessions = db.get_times(employee_id)

            has_active_session = False

            if sessions:
                last_start, last_end = sessions[0]
                has_active_session = (last_end == "")

            if not has_active_session:
                st.info("You are not currently clocked in.")
                if u.button("Clock in", key='styled_btn_tailwind',class_name="bg-green-800 text-white"):
                    db.insert_Work_done(employee_id, 0, startTime, "")
                    st.success(f"Your start time has been recorded at {getWorkingTime(1)}")

            if has_active_session:
                st.warning("You have an active session. Please log your end time.")
                project_number_ID = st.number_input("What project did you work on?", min_value=1, step=1, format="%d")
                if u.button("Log punch out time", key="styled_btn_tailwind", className="bg-green-800 text-white"):
                    db.update_work_done(getWorkingTime(0), project_number_ID, employee_id)
                    db.calculate_total_hours_worked(employee_id)
                    st.success("End time and task saved!")
                    st.snow()

        authenticator.logout('Logout')

    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your Employee code and Employee password')

except Exception as e:
    st.error(e)


# Save updated config (optional if login data changes during session)
with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
