import time
import streamlit as st
import databaseManagement as db
import arrow
import streamlit_shadcn_ui as ui
import os




# Initialize session state keys safely
if "clocked_in_user" not in st.session_state:
    st.session_state["clocked_in_user"] = []

if "emp_code" not in st.session_state:
    st.session_state.emp_code = ""

if "clear_emp_code" not in st.session_state:
    st.session_state["clear_emp_code"] = False

if "clear_project_name" not in st.session_state:
    st.session_state["clear_project_name"] = False

# ❗ Initialize input values BEFORE using them
if "emp_code_input" not in st.session_state:
    st.session_state.emp_code_input = ""

if "project_name_input" not in st.session_state:
    st.session_state.project_name_input = ""

# ✅ Clear inputs when flagged (must happen AFTER inputs are initialized)
if st.session_state.clear_emp_code:
    st.session_state.emp_code_input = ""
    st.session_state.clear_emp_code = False
    st.rerun()

if st.session_state.clear_project_name:
    st.session_state.project_name_input = ""
    st.session_state.clear_project_name = False
    st.rerun()

# Load employee code
user = db.get_emp_code()

emp_list=[]
for emp_id in user:
    first, last = db.get_emp_name_by_code(emp_id)
    codePlusName=f"{emp_id}: {first} {last}"
    emp_list.append(codePlusName)
# Time formatting helper
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

LOGO_PATH=os.path.join(BASE_DIR, "imgs","wieconLogo.png")



st.image(LOGO_PATH)
st.title('Wiecon Time Management System')

# ✅ Selectbox for employee code (with blank option for reset)
emp_code = st.selectbox(
    "Employee number",
    options=[""] + emp_list,
    key="emp_code_input"
)

if emp_code and emp_code != "":
    emp_number=str(emp_code.split(":")[0])

    emp_id = db.get_emp_ID(emp_number)[0]
    print("emp_id",type(emp_id))
    #print(emp_id)

    first, last = db.get_emp_name_by_code(emp_number)
    st.markdown(f"Welcome <b>{first} {last}</b>",unsafe_allow_html=True)
    st.write(f"The current date and time is **{getWorkingTime(1)}**")

    if emp_code in st.session_state["clocked_in_user"]:
        st.success("👋 Glad to see you're finishing work today.")

        try:
            project_names=db.get_project_names()
            project_code_plus_name_list = []
            for project_name in project_names:
                project_code=db.get_projects_code(project_name)
                project_code_plus_name=f"{project_code[0]}:{project_name}"
                project_code_plus_name_list.append(project_code_plus_name)
            project_name = st.selectbox(
                "Enter the project name",
                options=[""] +project_code_plus_name_list,
                key="project_name_input"
            )
            if project_name:
                project_id = db.get_project_id(project_name.split(":")[1])[0]
                #print("project:", project_id)
                password = st.text_input("🔑 Please enter your employee passcode to confirm clock out ")
                clock_out = ui.button("Clock out/時鐘輸出", key='styled_btn_tailwind', class_name="bg-green-800 text-white")

                if clock_out and password==db.get_emp_password(emp_id):
                    end_time = getWorkingTime(0)
                    db.update_work_done(endTime=end_time, projectWorkOnID=project_id, empolyeeID=emp_id)
                    st.balloons()
                    st.session_state["clocked_in_user"].remove(emp_code)
                    st.success(f"{emp_code} clocked out at **{getWorkingTime(1)}**.")
                    db.calculate_total_hours_worked(empID=emp_id)

                    time.sleep(1.5)
                    st.session_state.clear_emp_code = True
                    st.session_state.clear_project_name = True
                    st.rerun()
                if clock_out and password != db.get_emp_password(emp_id):
                    st.error(f"Please enter your employee password **{first} {last}**.")

        except TypeError:
            pass

    elif emp_number in user and emp_code not in st.session_state["clocked_in_user"]:
        print("HIT clocked IN")
        print(emp_id)
        start_time = getWorkingTime(0)
        st.session_state["clocked_in_user"].append(emp_code)
        db.insert_Work_done(employeeID=emp_id, StartTime=start_time, endTime="", projectWorkedonID=0)
        st.success(f"{emp_code} has been clocked for {getWorkingTime(1)}.")

        time.sleep(1.5)
        st.session_state.clear_emp_code = True
        st.session_state.clear_project_name = True
        st.rerun()

    else:
        st.error("❌ Invalid employee code.")



