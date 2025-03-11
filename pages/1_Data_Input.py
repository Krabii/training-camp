import streamlit as st
from db import get_session, fetch_data
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import Team, Coach, Facility
import pandas as pd

st.title("Data Input")

tab1, tab2, tab3 = st.tabs(["Teams", "Coaches", "Facilities"])
with tab1:

    st.title("Manage Teams")

    # Fetch Coaches
    with get_session() as session:
        coaches = session.exec(select(Coach)).all()
    coach_options = {coach.id: coach.name for coach in coaches}

    # 🚀 Fetch Teams Data with Coach Dropdown
    def fetch_teams():
        with get_session() as session:
            teams = session.exec(select(Team)).all()
            coaches = {coach.id: coach.name for coach in session.exec(select(Coach)).all()}  # Map ID -> Name

            df = pd.DataFrame([row.dict() for row in teams])
            df["coach_id"] = df["coach_id"].map(coaches)  # Convert ID -> Name
            df.rename(columns={"coach_id": "coach_name"}, inplace=True)  # Rename column
            return df[["id", "name", "gender", "age_group", "coach_name"]]  # Ensure order


    # Fetch Team Data
    df_team = fetch_teams()
    edited_df = st.data_editor(
        df_team,
        column_config={
            "name": "Name",
            "coach_name": st.column_config.SelectboxColumn(
                "Coach",
                options=list(coach_options.values()),  # List of Coach Names
                help="Select the coach for this team",
            ),
            "age_group": st.column_config.NumberColumn(
                "Age",
                min_value=4,
                max_value=40,
                step=1,
                format="%d"
            ),
            "gender": st.column_config.SelectboxColumn(
                "Gender",
                options=["M", "F", "MIXED"]
            )
        },
        disabled=["id"],
        hide_index=True,
        # num_rows="dynamic",
        key="team_editor",
        column_order=['id', 'name', 'coach_name', 'age', 'gender']
    )

    # 📌 Save Changes
    if st.button("Save Teams"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                # Convert coach name back to ID for saving
                coach_id = {v: k for k, v in coach_options.items()}[row["coach_name"]]
                
                team = session.exec(select(Team).where(Team.id == row["id"])).first()
                team.name = row["name"]
                team.gender = row["gender"]
                team.age_group = row["age_group"]
                team.coach_id = coach_id  # Save correct ID
                session.commit()
        st.success("Changes saved!")
        st.rerun()

    st.write("### Add New Team")
    with st.form("add_team"):
        name = st.text_input("Team Name")
        gender = st.selectbox("Gender", ["M", "F", "MIXED"])
        age_group = st.number_input("Age Group", min_value=5, max_value=40)
        coach_id = st.selectbox("Coach", list(coach_options.keys()), format_func=lambda x: coach_options[x])

        submitted = st.form_submit_button("Add Team")
        if submitted and name:
            with get_session() as session:
                session.add(Team(name=name, gender=gender, age_group=age_group, coach_id=coach_id))
                session.commit()
            st.success(f"Team '{name}' added successfully!")
            st.rerun()

with tab2:
    st.title("Manage Coaches")

    # 📌 Display and Edit Coaches
    df = fetch_data(Coach)
    edited_df = st.data_editor(df, key="coach_editor", disabled=["id"], hide_index=True,
    column_order=['id', 'name'])

    # 📌 Save Changes
    if st.button("Save Coaches"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                session.exec(
                    select(Coach)
                    .where(Coach.id == row["id"])
                ).first().name = row["name"]
            session.commit()
        st.success("Changes saved!")
        st.rerun()

    # 📌 Create a new Coach
    st.write("### Add New Coach")
    with st.form("add_coach"):
        name = st.text_input("Coach Name")
        submitted = st.form_submit_button("Add Coach")
        if submitted and name:
            with get_session() as session:
                session.add(Coach(name=name))
                session.commit()
            st.success(f"Coach '{name}' added successfully!")


with tab3:
    st.title("Manage Facilities")

    df = fetch_data(Facility)
    edited_df = st.data_editor(df, key="facility_editor", disabled=["id"], hide_index=True,
    column_config={
        "floor_type": st.column_config.SelectboxColumn(
            "Floor Type",
            options=["real", "artificial"]
        )
    },
    column_order=['id', 'name', 'floor_type']
    )

    if st.button("Save Facilities"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                facility = session.exec(select(Facility).where(Facility.id == row["id"])).first()
                facility.name = row["name"]
                facility.floor_type = row["floor_type"]
                session.commit()
        st.success("Changes saved!")
        st.rerun()

    st.write("### Add New Facility")
    with st.form("add_facility"):
        name = st.text_input("Facility Name")
        floor_type = st.selectbox("Floor Type", ["real", "artificial"])

        submitted = st.form_submit_button("Add Facility")
        if submitted and name:
            with get_session() as session:
                session.add(Facility(name=name, floor_type=floor_type))
                session.commit()
            st.success(f"Facility '{name}' added successfully!")
