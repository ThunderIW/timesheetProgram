import streamlit as st

import streamlit_authenticator as stauth
import yaml
from streamlit import title
from yaml.loader import SafeLoader
import streamlit_shadcn_ui as ui
import databaseManagement as db
from clockInSystem import emp_code
import polars as pl
import arrow




def create_project_code_plus_name():
    project_list=[]

    for project_name in db.get_project_names():
        project_codes=db.get_projects_code(project_name)
        project_combo=f"{project_codes[0]}: {project_name}"
        project_list.append(project_combo)
    return project_list


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
                project_name=project_to_view.split(":")[1]
                with st.expander(f"STATS about: **{project_code}  {project_name}** as of **{getWorkingTime(1)}**", expanded=True):

                    people_who_worked_on_the_project=db.get_people_who_worked_on_project(project_code)
                    total_hours_worked_project=db.get_total_hours_worked_on_project(project_code)[0][0]
                    cost_per_project=db.get_cost_per_project(project_code)
                    costs_remaining_budget=db.get_remaining_budget(project_code)
                    Pn,Pd,Pc=db.get_project_info(project_code)


                    if len(people_who_worked_on_the_project)>0 and  total_hours_worked_project!=0:
                        first_name=[row[0] for row in people_who_worked_on_the_project]
                        last_name = [row[1] for row in people_who_worked_on_the_project]
                        empCode=[row[2] for row in people_who_worked_on_the_project]
                        data={
                            "first_name":first_name,
                            "last_name":last_name,
                            "empCode":empCode,
                        }
                        st.subheader("General info on project")
                        st.write(f"**Project name**: {Pn}")
                        st.write(f"**Project description**: {Pd}")
                        st.write(f"**Project client**: {Pc}")

                        st.subheader("👨People who worked on the project")
                        df=pl.DataFrame(data)
                        st.dataframe(df, column_config={
                        "first_name":"first name ",
                        "last_name":"last name ",
                        "empCode":"Employee Code",
                        },use_container_width=True)

                        st.subheader("💵 COST info")
                        col1,col2=st.columns(2,gap="small",border=True)
                        with col1:
                            st.markdown("""
                                   <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                               """, unsafe_allow_html=True)
                            st.metric(label=f"💵 Cost of project **(TWD)** {project_code}:{project_name}", value=cost_per_project,delta=costs_remaining_budget)
                        #st.write(cost_per_project)
                        with col2:
                            st.markdown("""
                                    <div style="background-color:#f9f0ff; padding:20px; border-radius:10px;">
                                """, unsafe_allow_html=True)

                            if total_hours_worked_project<1 and total_hours_worked_project!=0:
                                total_min_worked=round(total_hours_worked_project*60,1)
                                st.metric(label="⌛ Minutes worked on the project  ",value=total_min_worked)
                            else:
                                st.metric(label="⌛ Hours worked on the project",value=total_hours_worked_project)

                        data_df=pl.DataFrame({
                            "project code":project_code,
                            "project name":project_name,
                            "total hours worked project":total_hours_worked_project,
                            "cost of project":cost_per_project,
                            "remaining_budget":costs_remaining_budget
                            })
                        data_as_csv=data_df.write_csv(None)
                        st.download_button(label="Download report",data=data_as_csv,file_name="project_data.csv",mime="text/csv", icon=":material/download:")



                    else:
                        st.warning("No project info or issue loading")





            if view_project_btn and len(project_to_view)==0:
                st.error("❌ Please select the project you want to view")
                #st.write(project_to_view)


    if st.button("Go back to dashboard",type="primary"):
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



