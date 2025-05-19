from cProfile import label

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import arrow
from streamlit_autorefresh import st_autorefresh
import databaseManagement as db
import streamlit_shadcn_ui as u
import pygwalker as pyg
import time



submittedToRemoveEmp = False
submittedEmp = False
emp_to_remove=False

def generate_next_emp_number():
    # Get the highest current emp_number
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT empCode FROM Employees ORDER BY empCode DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return "001"  # Start from 001 if no employees exist yet
    else:
        last_number = int(result[0])
        return str(last_number + 1).zfill(3)


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






# Login form
st.image("wieconLogo.png")
try:
    authenticator.login(fields={'Form name': 'Admin Login', 'Username': 'Username', 'Password': 'Password'})


    if st.session_state.get("authentication_status") is True:
        st.audio("login.wav", format='audio/wav', autoplay=True, )
        username = st.session_state.get('username')
        user_info = config['credentials']['usernames'].get(username, {})
        user_roles = user_info.get('roles', [])
        st.title("👩‍💼💻🔑 admin Page")
        if username == 'boris' and "CEO" in user_roles:
            st.subheader(f"Welcome **{st.session_state.get('name')}**")
            st.write(f"The current date and time is **{getWorkingTime(1)}**")
            st.success(" your are logged in as a CEO 👨")

            tables_names = db.get_table_names()
            selected_table = st.selectbox("Select a table to view", tables_names)
            current_count = 0
            project_df = db.convertDBToDataframe(selected_table)
            pan_form = project_df.to_pandas()
            if project_df is None or project_df.is_empty():
                st.warning(f"⚠️ No data found or failed to load table: {selected_table}.")

            else:
                st.dataframe(data=project_df, use_container_width=True)
                current_count = len(project_df)


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
                choices=st.segmented_control("Select an process you would like to do",options=['Add a new Project','Remove an Project',"Update Project Info"],default="Add a new Project")


                project_names = db.get_project_names()
                if choices == "Remove an Project":
                    with st.form("remove_project_form"):

                        if len(project_names)==0:
                            st.warning("No projects found")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                        else:
                            project_to_remove=st.selectbox("Enter the name the name of the project you want to remove",options=[""]+project_names,key="selected_project_to_remove")
                            #new_project_name = st.text_input("Enter the project name you want to remove")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                    if submitted and len(project_to_remove)>0:
                        print(project_to_remove)
                        db.delete_Project_or_delete_emp(project_to_remove, mode=0)
                        st.success(f"{project_to_remove} has been removed successfully.")
                        time.sleep(1)
                        st.rerun()
                    if submitted and len(project_to_remove)==0:
                        st.error("Please select a project name")
                        time.sleep(1)
                        st.rerun()



                elif choices == "Add a new Project":
                    with st.form("add_project_form"):

                        new_project_name = st.text_input("Enter new project name",key="new_project_name_input")
                        project_description=st.text_input("Enter project description",key="project_desc_input")
                        client_info=st.text_input("Client name",key="client_info_input")
                        submitted = st.form_submit_button("Submit project",type='primary')

                        if submitted:
                            result_for_project_insertion=db.add_project(new_project_name,project_description,client_info)
                            if "Integrity error: UNIQUE constraint failed: Projects.productName" in result_for_project_insertion:
                                st.error(f"Project **{new_project_name}** has been already been entered")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.success(f"Project {new_project_name} added successfully.")
                                time.sleep(1.5)
                                st.rerun()
                elif choices=="Update Project Info":
                        with st.form("update_project_form"):
                            if len(project_names) == 0:
                                st.warning("No projects found")
                                update_submit_button_for_project = st.form_submit_button(f"Remove project ", type='primary')
                            else:
                                project_to_update=st.selectbox("Please select the project you want to update",options=[""]+project_names)
                                what_to_update_project = st.selectbox("Please select what you want to update", options=["","Project Name", "Client Name", "Project Description"])
                                updated_value_project = st.text_input("Please enter the **new client** or **project name** or **project description**")
                                update_submit_button_for_project = st.form_submit_button(f"Update project ", type='primary')

                        if update_submit_button_for_project and len(updated_value_project)>0 and len(what_to_update_project)>0:
                            print(db.update_project_info(project_to_update,what_to_update_project,updated_value_project))
                            st.success(f"Project {project_to_update} been updated successfully")
                            time.sleep(1.5)
                            st.rerun()

                        if len(project_to_update)==0:
                            st.error("Please select a project name")
                        if len(what_to_update_project)==0:
                            st.error("Please select what you what to update")
                        if len(updated_value_project)==0:
                            st.error(f"Please type what is your new value for {what_to_update_project}")




            with st.expander(" 🧑‍💼 Employee management"):
                choices=st.segmented_control("Select an process you would like to do",options=['Add a new employee','Remove an Employee',"Update employee info"], default="Add a new employee")
                emp_names=db.get_employees()
                if choices=="Remove an Employee":
                    with st.form("remove_employee_form"):
                        if len(emp_names) == 0:
                            st.warning("No Employees found")
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee  ", type='primary')
                        else:
                            emp_to_remove = st.selectbox("Enter the name the employee of the project you want to remove",
                                                       options=[""]+emp_names)
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee ", type='primary')

                    if submittedToRemoveEmp and len(emp_to_remove)>0:
                        first_name, last_name = emp_to_remove.split(" ")
                        db.delete_Project_or_delete_emp(emp_first_name=first_name, emp_last_name=last_name, mode=1)
                        st.success(f'Employee {emp_to_remove} has been removed successfully')
                        time.sleep(0.5)
                        st.rerun()
                    if submittedToRemoveEmp and len(emp_to_remove)==0:
                        st.error("Please select a Employee name")
                        time.sleep(0.5)
                        st.rerun()



                elif choices=="Add a new employee":

                    with st.form("employee_form"):
                        first_name_for_submission=st.text_input("Enter employee first name")
                        last_name_for_submission=st.text_input("Enter employee last name")
                        email=st.text_input("✉️ Enter employee email")
                        ratePerHour=st.number_input(" 💵 Hourly Rate (TWD)",min_value=0.0, max_value=1000.0,value=0.0,step=0.5,format="%.2f")
                        emp_role=st.selectbox(label="Please select what role does this person have in the company", options=['CAD', 'Engineer','Admin','Management'])
                        submittedEmp=st.form_submit_button(f"Add Employee ", type='primary')



                    if submittedEmp:
                        new_emp_number = generate_next_emp_number()
                        if len(email)==0:
                            safe_first = first_name_for_submission.lower().replace(" ", "")
                            safe_last = last_name_for_submission.lower().replace(" ", "")
                            email = f"{safe_first}.{safe_last}.{new_emp_number}@gmail.com"

                        result_for_emp_insertion=db.insert_new_emp(first_name_for_submission, last_name_for_submission, email, emp_role,new_emp_number,ratePerHour)
                        print(result_for_emp_insertion)
                        if "Integrity error: UNIQUE constraint failed: Employees.email" in result_for_emp_insertion:

                            st.error(f"**{email}** has been already been used please use another email")
                            time.sleep(0.5)
                            st.rerun()
                        if "success"  in result_for_emp_insertion:
                            st.success(f'Employee {first_name_for_submission} {last_name_for_submission} has been added successfully')
                            time.sleep(0.5)
                            st.rerun()
                elif choices == "Update employee info":
                    with st.form("update_employee_form"):
                        if len(emp_names) == 0:
                            st.warning("No employees found")
                            update_submit_button = st.form_submit_button(f"Update Employee", type='primary')





                        else:
                            emp_to_update=st.selectbox("Please select which employee you want to update",
                                             options=[""] + emp_names)
                            what_to_update=st.selectbox("Please select what you want to update",options=["","Email","HourlyRate"])
                            updated_value=st.text_input("Please enter the new email/hourly rate **(example: 2.00)**")
                            update_submit_button = st.form_submit_button(f"Update Employee", type='primary')

                        if update_submit_button and len(updated_value)>0:
                            first_name,last_name=emp_to_update.split(" ")
                            try:
                                money=int(updated_value)
                                print(db.update_emp_info(first_name,last_name,money))

                            except ValueError:
                                email=updated_value
                                db.update_emp_info(first_name, last_name, email)
                            st.success(f"Employee {emp_to_update} been updated successfully")
                        if update_submit_button and len(emp_to_update)==0:
                            st.error("Please select a Employee name")
                        if update_submit_button and len(what_to_update)==0:
                            st.error("Please select what you want to update")
                        if update_submit_button and len(updated_value)==0:
                            st.error("Please type a value")





        authenticator.logout()

    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Incorrect username or password")
        st.stop()

    else:
        st.warning("🔒 Please log in to continue")
        st.stop()
except Exception as e:
    st.error(e)



