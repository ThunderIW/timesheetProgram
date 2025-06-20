import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import arrow
import databaseManagement  as db
import streamlit_shadcn_ui as ui
import time
import polars as pl



submittedToRemoveEmp = False
submittedEmp = False
emp_to_remove=False
person_name = []


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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
CONFIG_PATH_A = os.path.join(APP_ROOT, 'config.yaml')
LOGO_PATH=os.path.join(APP_ROOT, 'imgs',"wieconLogo.png")
login_sound=os.path.join(APP_ROOT,"sounds","login.wav" )




with open(CONFIG_PATH_A) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Hash passwords if needed
stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)



def create_project_code_plus_name():
    project_list = []
    for project_name in db.get_project_names():
        project_codes = db.get_projects_code(project_name)
        project_combo = f"{project_codes[0]}: {project_name}"
        project_list.append(project_combo)
    return project_list




# Login form
st.image(LOGO_PATH)
try:
    authenticator.login(fields={'Form name': 'Admin Login', 'Username': 'Username', 'Password': 'Password'},captcha=True)


    if st.session_state.get("authentication_status") is True:
        st.audio(data=login_sound, format='audio/wav', autoplay=True)
        username = st.session_state.get('username')
        user_info = config['credentials']['usernames'].get(username, {})
        user_roles = user_info.get('roles', [])
        st.title("👩‍💼💻🔑 Admin Page")
        st.subheader(f"Welcome **{st.session_state.get('name')}**")
        if username == 'boris' and "CEO" in user_roles:
            st.write(f"The current date and time is **{getWorkingTime(1)}**")
            st.success("you are logged in as a CEO 👨")

            with st.expander("Create new admin accounts",icon="🔑"):
                try:
                    email_of_registered_user, \
                        username_of_registered_user, \
                        name_of_registered_user = authenticator.register_user(roles=["admin"],password_hint=False,clear_on_submit=True)
                    if email_of_registered_user:
                        st.success('User registered successfully')
                except Exception as e:
                    st.error(e)

            not_clocked_out_emp = db.find_not_clocked_out_employee()
            if len(not_clocked_out_emp) >=1:
                for emp in not_clocked_out_emp:
                    first_name = emp[0]
                    last_name = emp[1]
                    emp_code = emp[2]
                    person_name.append(f"{emp_code}: {first_name} {last_name}")


                with st.expander(f"👨 Fill in not clocked out Employee for today {getWorkingTime(1)} "):


                    with st.form("Update Employee clock out"):
                        person_to_update=st.selectbox(label="Chose a person to log their time",options=[""]+person_name)



                        submit_update_person_clock_out_time=st.form_submit_button("Fill in not clocked_out_Employee",type="primary")
                    if len(person_to_update)==0 and submit_update_person_clock_out_time:
                        st.error("❌ Please Select which employee you want to update")

                    if  submit_update_person_clock_out_time and len(person_to_update)>0:
                        person_id=int(str(person_to_update).split(":")[0][2:])
                        person_name=str(person_to_update).split(":")[1].strip()
                        print(person_name)
                        db.update_unClock_emp(person_id)
                        st.success(f"{person_name}'s worked hour has been updated to 8 hours")
                        time.sleep(2.0)
                        st.rerun()








            with open(CONFIG_PATH_A, 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)







            tables_names = db.get_table_names()
            selected_table = st.selectbox("Select a table to view", tables_names)
            current_count = 0
            project_df = db.convertDBToDataframe(selected_table)
            pan_form = project_df.to_pandas()
            if project_df is None or project_df.is_empty():
                st.warning(f"⚠️ No data found or failed to load table: {selected_table}.")

            else:
                st.dataframe(data=project_df, use_container_width=True)
                #print(project_df)
                current_count = len(project_df)
                psd=project_df.write_csv()



                st.download_button(label=f"📥 Download {selected_table} to csv ",data=psd,file_name=f'{str(selected_table).lower().capitalize()}.csv',mime='text/csv',type="primary")
                st.warning("Please after download tell excel to keep leading zeros")


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

            with st.expander("➕➖ Add remove Update Projects"):
                choices=st.segmented_control("Select an process you would like to do",options=['Add a new Project','Remove an Project',"Update Project Info","Add A project Cost"],default="Add a new Project")


                project_names = db.get_project_names()
                if choices == "Remove an Project":
                    with st.form("remove_project_form"):

                        if len(project_names)==0:
                            st.warning("No projects found")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                        else:
                            project_to_remove=st.selectbox("Enter the name the name of the project you want to remove",options=[""]+create_project_code_plus_name(),key="selected_project_to_remove")
                            #new_project_name = st.text_input("Enter the project name you want to remove")
                            submitted = st.form_submit_button(f"Remove project ", type='primary')

                    if submitted and len(project_to_remove)>0:
                        project_code=str(project_to_remove).split(":")[0]

                        db.delete_Project_or_delete_emp(projectCode=project_code, mode=0)
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
                        project_budget=st.number_input(" 💵 Project Budget (TWD)",min_value=0.0,value=0.0,step=0.5,format="%.2f")
                        project_code=st.text_input("Please enter the project code")
                        submitted = st.form_submit_button("➕ Submit project",type='primary')

                        if submitted:
                            is_valid = True

                            if len(new_project_name)==0 and len(project_description)==0 and len(client_info)==0 and project_budget==0:
                                st.error(
                                    "❌ Please fill in all required fields: project name, client info,project budget and project code .")
                                is_valid=False
                            else:
                                if len(new_project_name) == 0:
                                    st.error("❌ Please type the **Project Name**")
                                    is_valid=False

                                if len(project_description) == 0:
                                    st.error("❌ Please type the **Project description**")
                                    is_valid=False

                                if project_budget == 0:
                                    st.error("❌ Please enter a valid **budget**.")
                                    is_valid=False

                                if len(project_code) == 0:
                                    st.error("❌ Please enter the project's **project code**.")
                                    is_valid=False

                                if len(client_info) == 0:
                                    st.error("❌ Please Type the **client name**.")
                                    is_valid = False


                            if is_valid:
                                result_for_project_insertion=db.add_project(new_project_name,project_description,client_info,project_budget,project_code)
                                print(result_for_project_insertion)
                                if "Integrity error: UNIQUE constraint failed: Projects.productName" in result_for_project_insertion:
                                    st.error(f"Project **{new_project_name}** has been already been entered")
                                    time.sleep(1.5)
                                    st.rerun()

                                if "Integrity error: UNIQUE constraint failed: Projects.projectCode" in result_for_project_insertion:
                                    st.error(f"Project code **{project_code}** has been already used, please use another project code")


                                else:
                                    st.success(f"Project {new_project_name} added successfully.")
                                    time.sleep(1.5)
                                    st.rerun()

                        data_for_projects = st.file_uploader(label="Upload the Project info", type=['csv'],key="upload_data_for_projects",accept_multiple_files=False)

                        df_project = None
                        if data_for_projects:
                            if data_for_projects.name.endswith(".csv"):
                                df_project = pl.read_csv(data_file=data_for_projects)
                                pd_df_for_projects = df_project.to_pandas()
                                ui.element(name="")
                                upload_button = ui.button(text="📤 Upload", key="Upload_project_data")
                                confirmUploadProject = ui.alert_dialog(show=upload_button, title="Upload project",
                                                                confirm_label="Upload project",
                                                                cancel_label="don't upload project", description="",
                                                                key="Upload_project_data_alert")
                                if confirmUploadProject:
                                    try:
                                        conn = db.get_connection()
                                        pd_df_for_projects.to_sql('Projects', conn, if_exists='replace', index=False)
                                        conn.commit()

                                    except Exception as e:
                                        print("Database insert error:", e)

                                    finally:
                                        st.success(f"{data_for_projects.name} has been uploaded successfully")
                                        conn.close()
                                        time.sleep(0.5)
                                        st.rerun()


                                if not confirmUploadProject:
                                    pass

                            else:
                                st.error("Please upload an excel(.csv) file")
                                df = None

                elif choices=="Update Project Info":
                        with st.form("update_project_form",enter_to_submit=True):
                            if len(project_names) == 0:
                                st.warning("No projects found")
                                update_submit_button_for_project = st.form_submit_button(f"Remove project ", type='primary')
                            else:
                                project_to_update=st.selectbox("Please select the project you want to update",options=[""]+project_names)
                                what_to_update_project = st.selectbox("Please select what you want to update", options=["","Project Name", "Client Name", "Project Description","Project Budget","Project Code"])
                                updated_value_project = st.text_input("Please enter the **new client** or **project name** or **project description** or **project budget** or **project code**")
                                update_submit_button_for_project = st.form_submit_button(f"Update project ", type='primary')

                                if update_submit_button_for_project:
                                    if len(project_to_update)==0 and len(what_to_update_project)==0 and len(updated_value_project)==0:
                                        st.error(
                                            "❌ Please fill in all required fields: project to update, what category would like to update and the value .")


                                    if len(project_to_update)==0:
                                        st.error("❌ Please select a project name")
                                    if len(what_to_update_project)==0:
                                        st.error("❌ Please select what category you want to update")

                                    if len(updated_value_project)==0:
                                        st.error("❌ Please enter a value ")

                                    else:
                                        print(db.update_project_info(project_to_update, what_to_update_project,
                                                                     updated_value_project))


                                    if len(project_to_update)>0 and len(what_to_update_project)>0 and len(updated_value_project)>0:
                                        st.success(f"Project {project_to_update} has been updated successfully")
                                        time.sleep(1.5)
                                        st.rerun()

                elif choices=="Add A project Cost":

                    with st.form("update_project_form", enter_to_submit=True):
                        project=st.selectbox("Please select a project you want to add this project cost to",options=[""]+create_project_code_plus_name())
                        category=st.selectbox(label="Please select a category", options=["","Flight","Hotel"])
                        reason=st.text_input("Please enter a description for this cost")
                        cost = st.number_input("💵 Enter cost (in TWD)", min_value=0.0, step=10.0, format="%.2f")
                        add_project_cost_button=st.form_submit_button(f"Add a project cost", type='primary')

                        if add_project_cost_button:
                            if cost==0 and len(reason)==0 and len(project)==0:
                                st.error(
                                    "❌ Please fill in all required fields: Description, the cost, the project you would like to add the cost to")
                            if cost==0 and len(reason)>0 and len(project)>0:
                                st.error("❌ Please enter a valid **Amount**.")


                            if len(reason)==0 and cost>0 and len(project)>0:
                                st.error("❌ Please enter a description.")


                            if len(project)==0 and len(reason)>0 and cost>0:
                                st.error("❌ Please select the project.")


                            if cost>0 and len(reason)>0 and len(project)>0:
                                project_code=str(project).split(":")[0]
                                st.success(f"Project cost has been successfully added to {project}")
                                db.insert_into_project_cost_table(reason,cost, project_code,category)







                removeAllProject=ui.button("🗑️ Remove all projects", key='styled_btn_tailwind_project', class_name="bg-red-600 text-white")
                removeAllProjectAlert=ui.alert_dialog(show=removeAllProject,title="Remove all projects?",description="",confirm_label="YES",cancel_label="NO",key="alert_dialog_for_project")
                if removeAllProjectAlert:
                    db.clear_database(mode=0)
                    st.success("All projects have been removed successfully")




            with st.expander("🧑‍💼 Employee management"):
                choices=st.segmented_control("Select an process you would like to do",options=['Add a new employee','Remove an Employee',"Update employee info"], default="Add a new employee",)
                emp_names=db.get_employees()
                if choices=="Remove an Employee":
                    with st.form("remove_employee_form"):
                        if len(emp_names) == 0:
                            st.warning("No Employees found")
                            submittedToRemoveEmp = st.form_submit_button(f"Remove Employee  ", type='primary')
                        else:
                            emp_to_remove = st.selectbox("Enter the name the employee of the project you want to remove",
                                                       options=[""]+emp_names)
                            submittedToRemoveEmp = st.form_submit_button(f"➖ Remove Employee ", type='primary')

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
                        emp_role=st.selectbox(label="Please select what role does this person have in the company", options=["",'CAD', 'Engineer','Admin','Management'])
                        submittedEmp=st.form_submit_button(f"➕ Add Employee ", type='primary')


                    if submittedEmp:
                        is_valid_emp_input=True
                        new_emp_number = generate_next_emp_number()

                        if len(first_name_for_submission) == 0 and len(last_name_for_submission) == 0 and ratePerHour == 0 and len(emp_role) == 0:
                            st.error("❌ Please fill in all required fields: first name, last name, hourly rate, and role.")
                            is_valid_emp_input=False

                        else:


                            if len(first_name_for_submission)==0:
                                st.error("❌ Please type the **employee first name**")
                                is_valid_emp_input=False

                            if len(last_name_for_submission) == 0:
                                st.error("❌ Please type the **employee last name**")
                                is_valid_emp_input=False

                            if ratePerHour == 0:
                                st.error("❌ Please enter a valid **hourly rate**.")
                                is_valid_emp_input=False

                            if len(emp_role) == 0:
                                st.error("❌ Please select the employee's **role**.")
                                is_valid_emp_input=False


                        if is_valid_emp_input:
                            if len(email) == 0:
                                safe_first = first_name_for_submission.lower().replace(" ", "")
                                safe_last = last_name_for_submission.lower().replace(" ", "")
                                email = f"{safe_first}.{safe_last}.{new_emp_number}@gmail.com"

                            result_for_emp_insertion = db.insert_new_emp(first_name_for_submission,
                                                                         last_name_for_submission, email, emp_role,
                                                                         new_emp_number, ratePerHour,new_emp_number)




                            if "Integrity error: UNIQUE constraint failed: Employees.email" in result_for_emp_insertion:

                                st.error(f"**{email}** has been already been used please use another email")
                                time.sleep(0.5)
                                st.rerun()

                            else:
                                st.success(f'Employee {first_name_for_submission} {last_name_for_submission} has been added successfully')
                                time.sleep(0.5)
                                st.rerun()

                    data_for_emp=st.file_uploader(label="Upload the employee info",type=['csv'],accept_multiple_files=False)

                    df_emp = None
                    if data_for_emp:
                        if data_for_emp.name.endswith(".csv"):
                            df_emp = pl.read_csv(data_for_emp,schema_overrides={"empCode":pl.Utf8,"EmpPassword":pl.Utf8})
                            print(df_emp)
                            pd_df_emp=df_emp.to_pandas()
                            #print(pd_df_emp)
                            upload_button=ui.button(text="📤 Upload",key="Upload_employee_data")
                            confirmUploadEmp=ui.alert_dialog(show=upload_button,title="Upload employee",confirm_label="Upload employee",cancel_label="don't upload employee",description="",key="Upload_employee_data_alert")
                            if confirmUploadEmp:

                                try:
                                    conn=db.get_connection()
                                    pd_df_emp.to_sql('Employees', conn, if_exists='replace', index=False)
                                    conn.commit()

                                except Exception as e:
                                    print("Database insert error:", e)

                                finally:
                                    st.success(f"{data_for_emp.name} has been uploaded successfully")
                                    conn.close()
                                    time.sleep(0.5)
                                    st.rerun()


                            if not confirmUploadEmp:
                                pass

                        else:
                            st.error("Please upload an excel(.csv) file")
                            df=None




                elif choices == "Update employee info":

                    if "form_success_update" not in st.session_state:
                        st.session_state.form_success_update = False

                    with st.form("update_employee_form",clear_on_submit=True,enter_to_submit=True):
                        if len(emp_names) == 0:
                            st.warning("No employees found")
                            update_submit_button = st.form_submit_button(f"Update Employee", type='primary')


                        else:
                            emp_to_update=st.selectbox("Please select which employee you want to update",
                                             options=[""] + emp_names)
                            what_to_update=st.selectbox("Please select what you want to update",options=["","Email","HourlyRate"])
                            updated_value=st.text_input("Please enter the new email/hourly rate **(example: 2.00)**")
                            update_submit_button = st.form_submit_button(f"Update Employee", type='primary')

                        if update_submit_button:
                            if len(emp_to_update)==0 and len(what_to_update)==0 and len(updated_value)==0:
                                st.error("❌ Please fill in all required fields: Employee, what to update, value")
                            if len(emp_to_update)==0:
                                st.error("❌ Please Select the employee you want to update")

                            if len(what_to_update)==0:
                                st.error("❌ Please Select what you want to update")

                            if len(updated_value)==0:
                                st.error("❌ Please enter the value you want to update")

                            else:
                                first_name,last_name=emp_to_update.split(" ")
                                try:
                                    money=int(updated_value)
                                    #print(db.update_emp_info(first_name,last_name,money))

                                except ValueError:
                                    email=updated_value
                                    db.update_emp_info(first_name, last_name, email)
                                st.success(f"Employee {emp_to_update} has been updated successfully")
                                time.sleep(1)
                                st.rerun()





                removeAllEmployee=ui.button("🗑️ Remove all Employee", key='styled_btn_tailwind_for_emp', class_name="bg-red-600 text-white")
                removeAllEmployeeAlert = ui.alert_dialog(show=removeAllEmployee, title="Remove all employees ?",
                                                        description="",
                                                        confirm_label="YES", cancel_label="NO",key="alert_dialog_for_emp")



                if removeAllProjectAlert:
                    db.clear_database(mode=0)
                    st.success("All employee have been removed successfully")



        if st.button("Generate report", type="primary"):
            st.switch_page("pages/reportPage.py")

        authenticator.logout()

    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Incorrect username or password")
        st.stop()

    else:
        st.warning("🔒 Please log in to continue")
        st.stop()
except Exception as e:
    st.error(e)



