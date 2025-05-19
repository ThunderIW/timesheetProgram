
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
                modeToRemoveProject = st.toggle("Tick to remove project", key="RemoveProject")
                if modeToRemoveProject:
                    with st.form("remove_project_form"):
                        project_names=db.get_project_names()
                        if len(project_names)==0:
                            st.warning("No projects found")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                        else:
                            project_to_remove=st.selectbox("Enter the name the name of the project you want to remove",options=project_names)
                            #new_project_name = st.text_input("Enter the project name you want to remove")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')



                else:
                    with st.form("add_project_form"):

                        new_project_name = st.text_input("Enter new project name")
                        project_description=st.text_input("Enter project description")
                        client_info=st.text_input("Client name")
                        submitted = st.form_submit_button("Submit project",type='primary')

                if submitted and modeToRemoveProject==False:
                    db.add_project(new_project_name,project_description)
                    st.success("Project added successfully.")
                    time.sleep(0.3)
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
                            emp_to_remove = st.selectbox("Enter the name the employee of the project you want to remove",
                                                       options=emp_names)
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee ", type='primary')






                else:
                    with st.form("employee_form"):
                        first_name_for_submission=st.text_input("Enter employee first name")
                        last_name_for_submission=st.text_input("Enter employee last name")
                        email=st.text_input("✉️ Enter employee email")
                        ratePerHour=st.number_input(" 💵 Hourly Rate (TWD)",min_value=0.0, max_value=1000.0,value=0.0,step=0.5,format="%.2f")
                        emp_role=st.selectbox(label="Please select what role does this person have in the company", options=['CAD', 'Engineer','Admin','Management'])
                        submittedEmp=st.form_submit_button(f"Add Employee ", type='primary')

                if submittedToRemoveEmp and modeToRemoveEmployee == True:
                    first_name, last_name = emp_to_remove.split(" ")
                    db.delete_Project_or_delete_emp(emp_first_name=first_name, emp_last_name=last_name, mode=1)
                    st.success(f'Employee {emp_to_remove} has been removed successfully')
                    time.sleep(0.3)
                    st.rerun()

                if submittedEmp and modeToRemoveEmployee == False:
                    new_emp_number = generate_next_emp_number()
                    db.insert_new_emp(first_name_for_submission, last_name_for_submission, email, emp_role,new_emp_number)
                    st.success(f'Employee {first_name_for_submission} {last_name_for_submission} has been added successfully')
                    time.sleep(0.5)
                    st.rerun()

                    #st.warning("After you have chosen this please select the register below to register the employee", )




        authenticator.logout()

    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Incorrect username or password")
        st.stop()

    else:
        st.warning("🔒 Please log in to continue")
        st.stop()
except Exception as e:
    st.error(e)



