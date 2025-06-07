import os
from cProfile import label

import streamlit as st

import streamlit_authenticator as stauth
import yaml
from tensorflow.python.framework.test_ops import kernel_label
from yaml.loader import SafeLoader
import streamlit_shadcn_ui as ui
import databaseManagement as db
import polars as pl
import arrow
import plotly.graph_objects as go



bar_width=0.2


def create_final_project_df():
    projects=db.retrieve_full_report(mode="Projects")
    columns=[
        "Project Code",
        "Project Name",
        "Project Description",
        "Project Budget(TWD)",
        "Project Remaining budget(TWD)",
        "Total Hours",
        "Total Cost Per Project(TWD)"

    ]
    final_project_report=pl.DataFrame(projects,schema=columns,orient='row')
    return final_project_report


def create_final_report_df():
    # 1. If retrieve_full_report() returns a list of dicts:
    report = db.retrieve_full_report(mode="all")

    columns = [
        "Project Code",
        "product Name",
        "employee Code",
        "first Name",
        "last Name",
        "rate Per Hour(TWD)",
        "total Hours  Worked",
        "project Budget(TWD)",
        "Cost(TWD)"
    ]

    # Build DataFrame
    final_report_df = pl.DataFrame(report,schema=columns,orient="row")
    return final_report_df





def create_project_code_plus_name():
    project_list = []
    for project_name in db.get_project_names():
        project_codes = db.get_projects_code(project_name)
        project_combo = f"{project_codes[0]}: {project_name}"
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



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
CONFIG_PATH_R = os.path.join(APP_ROOT, 'config.yaml')
LOGO_PATH=os.path.join(APP_ROOT, 'imgs',"wieconLogo.png")



with open(CONFIG_PATH_R) as file:
    config = yaml.load(file, Loader=SafeLoader)

stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)







st.image(LOGO_PATH)
roles = st.session_state.get("roles", [])  # Safe fetch
st.title("Report Page")

try:
    if "CEO" in roles:
        st.success("ACCESS GRANTED")
        project_list = create_project_code_plus_name()
        if len(project_list) == 0:
            st.warning("No project or issue loading")
        else:
            project_to_view = st.selectbox("Please select the project you want to view", options=[""] + project_list)
            view_project_btn = ui.button("View project", key='styled_btn_tailwind', class_name="bg-green-800 text-white")

            if view_project_btn:
                if len(project_to_view) == 0:
                    st.error("❌ Please select the project you want to view")
                else:
                    project_code = project_to_view.split(":")[0]
                    project_name = project_to_view.split(":")[1]

                    # Load all project data
                    people_who_worked = db.get_people_who_worked_on_project(project_code)
                    total_hours = db.get_total_hours_worked_on_project(project_code)
                    total_hours = total_hours[0][0] if total_hours and total_hours[0] else 0
                    cost = db.get_cost_per_project(project_code)
                    remaining_budget = db.get_remaining_budget(project_code)
                    project_info = db.get_project_info(project_code)
                    Pn, Pd, Pc = project_info if project_info and len(project_info) == 3 else ("N/A", "N/A", "N/A")
                    Engineer_work_hours=db.get_CAD_and_engineer_hours(project_code,"Engineer")
                    CAD_Work_hours=db.get_CAD_and_engineer_hours(project_code,"CAD")
                    get_additional_cost_of_project=db.get_additional_Cost(project_code)[0]
                    print(CAD_Work_hours)
                    print(Engineer_work_hours)


                    # Check if any project info is missing
                    if not people_who_worked or total_hours == 0 or cost == 0 or remaining_budget == 0 or Pn == "N/A":
                        st.warning("No data available")
                    else:
                        with (st.expander(
                            f"STATS about: **{project_code}  {project_name}** as of **{getWorkingTime(1)}**",
                            expanded=True
                        )):
                            # General info
                            st.subheader("General info on project")
                            st.write(f"**Project name**: {Pn}")
                            st.write(f"**Project description**: {Pd}")
                            st.write(f"**Project client**: {Pc}")

                            # People table
                            st.subheader("👨 People who worked on the project")
                            data = {
                                "first_name": [row[0] for row in people_who_worked],
                                "last_name": [row[1] for row in people_who_worked],
                                "empCode": [row[2] for row in people_who_worked],
                            }
                            df = pl.DataFrame(data)
                            st.dataframe(
                                df,
                                column_config={
                                    "first_name": "first name ",
                                    "last_name": "last name ",
                                    "empCode": "Employee Code",
                                },
                                use_container_width=True
                            )

                            # Cost info
                            st.subheader("⌛ Split of Engineer and CAD Hours")
                            col1C,col2C=st.columns(2,gap="small",border=True)
                            with col1C:
                                st.markdown(
                                    """
                                    <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )

                                if Engineer_work_hours is not None:
                                    if  Engineer_work_hours>=1:
                                        st.metric(label="⌛Engineer Hours",value=Engineer_work_hours)
                                if Engineer_work_hours is None or Engineer_work_hours<1:
                                    st.metric(label="⌛ Engineer Hours",value=0)

                            with col2C:
                                st.markdown(
                                    """
                                    <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )

                                if CAD_Work_hours is not None:
                                    if CAD_Work_hours>=1:

                                        st.metric(label="⌛ CAD Hours",value=CAD_Work_hours)
                                if CAD_Work_hours is  None or CAD_Work_hours<1:
                                    st.metric(label="⌛ CAD Hours",value=0)



                            st.subheader("💵 COST info and ⌛ Total  Project Hours")
                            col1, col2,col3,col4 = st.columns(4, gap="small", border=True)
                            with col1:
                                st.markdown(
                                    """
                                    <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )


                                st.metric(
                                    label=f"💵 Cost of project **(TWD)** {project_code}",
                                    value=cost+get_additional_cost_of_project

                                )
                            with col2:
                                st.markdown(
                                    """
                                    <div style="background-color:#f9f0ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )
                                if total_hours < 1 and total_hours != 0:
                                    total_min_worked = round(total_hours * 60, 1)
                                    st.metric(label="⌛ Hours worked on the project", value=0)
                                else:
                                    st.metric(label="⌛ Hours worked on the project", value=total_hours)

                            with col3:
                                st.markdown(
                                    """
                                    <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )

                                st.metric(label="💵 Remaining Budget", value=round(remaining_budget-get_additional_cost_of_project))
                            # Download CSV
                            with col4:
                                st.markdown(
                                    """
                                    <div style="background-color:#e6f7ff; padding:20px; border-radius:10px;">
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.metric(label="💸 Additional Cost (TWD)", value=f"{get_additional_cost_of_project:,.2f}")
                            st.subheader("📦 Additional COST Breakdown")


    if st.button("See project reports"):
        if create_final_report_df().is_empty() and create_final_report_df().is_empty():
            st.warning("No data available")
        else:

            with st.expander(label=f"Summary as **{getWorkingTime(1)}**"):
                st.subheader("Overall")



            st.dataframe(create_final_report_df(),use_container_width=True)
            st.download_button(
                label="Download report",
                data=create_final_project_df().write_csv(None),
                file_name="project_data.csv",
                mime="text/csv",
                icon=":material/download:",key="All_download"
            )

            st.subheader("Individual projects")
            st.dataframe(create_final_project_df(),use_container_width=True)
            selected =create_final_project_df().select(["Project Code","Project Name","Project Budget(TWD)","Project Remaining budget(TWD)","Total Cost Per Project(TWD)"])
            pdf=selected.to_pandas()

            st.download_button(
                label="Download report",
                data=create_final_project_df().write_csv(None),
                file_name="project_data.csv",
                mime="text/csv",
                icon=":material/download:", key="P_download"
            )

            fig=go.Figure(data=[go.Bar(
                name="Project budget",
                x=pdf['Project Name'],
                y=pdf['Project Budget(TWD)'],

                marker_color="#3498DB",
                width=bar_width
            ),
            go.Bar(
                name="Remaining budget(TWD)",
                x=pdf['Project Name'],
                y=pdf['Project Remaining budget(TWD)'],
                marker_color="#FF5733",
                width=bar_width,


            ),
            go.Bar(
                name="Total Cost per project(TWD)",
                x=pdf['Project Name'],
                y=pdf['Total Cost Per Project(TWD)'],
                marker_color="#2ECC71",
                width=bar_width,
            )



            ])
            fig.update_layout(
                barmode='group',
                title="Project Budget vs Remaining Budget (TWD)",
                xaxis_title="Project Name",
                yaxis_title="Amount (TWD)",
                legend_title="Budget Portion",
                
            )


            st.plotly_chart(fig, use_container_width=True)






    if st.button("Go back to dashboard", type="primary"):
        st.switch_page("pages/Admin_page.py")

    authenticator.logout()
    if st.session_state.get("authentication_status") is None:
        st.switch_page("clockInSystem.py")

except TypeError as e:
    error_message = str(e)
    print(error_message)
    if "NoneType" in error_message:
        st.error("❌ Access denied. You are not authorized to view this page.")
        if st.button("Login", type="secondary"):
            st.switch_page("pages/Admin_page.py")
        if st.button("Return to Home", type="primary"):
            st.switch_page("clockInSystem.py")