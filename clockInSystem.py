import time
import streamlit as st
from streamlit_datalist import stDatalist
import databaseManagement as db
import arrow
import streamlit_shadcn_ui as ui

# Initialize session state key safely
if "clocked_in_user" not in st.session_state:
    st.session_state["clocked_in_user"] = []


if "emp_code" not in st.session_state:
    st.session_state.emp_code = ""

user = db.get_emp_code()

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






st.image("wieconLogo.png")
st.title('Wiecon Time Management System')

emp_code = stDatalist("Select/type your employee number(選擇/輸入您的員工號碼)",options=user)


if emp_code:
    emp_id = db.get_emp_ID(emp_code)[0]
    print(emp_id)

    first,last=db.get_emp_name_by_code(emp_code)
    st.write(f"Welcome **{first} {last}**")
    st.write(f"The current date and time is **{getWorkingTime(1)}**")



    if emp_code in st.session_state["clocked_in_user"]:
        st.success("👋 Glad to see you're finishing work today.")
        #project_number=st.number_input(label="enter your project number", min_value=1, max_value=20,step=1)
        try:
            project_name=stDatalist("enter the project name",options=db.get_project_names())
            project_id=db.get_project_id(project_name)[0]
            print("project:",project_id)
            clock_out = ui.button("Clock out/時鐘輸出", key='styled_btn_tailwind', class_name="bg-green-800 text-white")
            # clock_out=st.button("Clock out",type="primary")
            if project_name and clock_out:
                end_time = getWorkingTime(0)
                print(db.update_work_done(endTime=end_time, projectWorkOnID=project_id, empolyeeID=emp_id))
                st.balloons()
                time.sleep(1)
                st.session_state["clocked_in_user"].remove(emp_code)
                st.success(f"{emp_code} clocked out at **{getWorkingTime(1)}**.")
                db.calculate_total_hours_worked(empID=emp_id)
                st.session_state.emp_code = ""
        except TypeError:
            pass








    elif emp_code in user and emp_code not in st.session_state["clocked_in_user"]:
        start_time = getWorkingTime(0)
        st.session_state["clocked_in_user"].append(emp_code)
        db.insert_Work_done(employeeID=emp_id, StartTime=start_time, endTime="", projectWorkedonID=0)
        st.success(f"{emp_code} has been clocked for {getWorkingTime(1)}.")


    else:
        st.error("❌ Invalid employee code.")






