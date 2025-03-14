import streamlit as st
from db import get_session, fetch_data
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import Group, Venue, Instructor, Tag, Activity
import pandas as pd
from sqlalchemy import delete

st.set_page_config(
    page_title="Data Input",
    page_icon=":page_facing_up:",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)


st.title(":page_facing_up: Data Input")

# Check if "success_toast" is in session state
if "success_toast" in st.session_state and st.session_state.success_toast:
    st.toast("✅ Success! Your changes have been saved.")
    st.session_state.success_toast = False  # Reset flag after showing toast
if "error_toast" in st.session_state and st.session_state.success_toast:
    st.toast(":x: Error: Cannot delete row(s) due to existing references. Remove related records first.")


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Groups", "Instructors", "Venues", "Tags", "Activities"])

with tab1:

    st.title("Manage Groups")

    # Fetch Instructores
    with get_session() as session:
        instructores = session.exec(select(Instructor)).all()
    instructor_options = {instructor.id: instructor.name for instructor in instructores}

    # 🚀 Fetch Groups Data with Instructor Dropdown
    def fetch_groups():
        with get_session() as session:
            groups = session.exec(select(Group)).all()
            instructores = {instructor.id: instructor.name for instructor in session.exec(select(Instructor)).all()}  # Map ID -> Name

            df = pd.DataFrame([row.model_dump() for row in groups])
            df["instructor_id"] = df["instructor_id"].map(instructores)  # Convert ID -> Name
            df.rename(columns={"instructor_id": "instructor_name"}, inplace=True)  # Rename column
            return df[["id", "name", "gender", "age_group", "instructor_name"]]  # Ensure order


    # Fetch Group Data
    df_group = fetch_groups()
    df_group["Delete"] = False  # Add a delete column (checkboxes)
    edited_df = st.data_editor(
        df_group,
        column_config={
            "name": "Name",
            "instructor_name": st.column_config.SelectboxColumn(
                "Instructor",
                options=list(instructor_options.values()),  # List of Instructor Names
                help="Select the instructor for this group",
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
        key="group_editor",
        column_order=['name', 'instructor_name', 'age', 'gender', 'Delete']
    )

    # 📌 Save Changes
    if st.button("Update Groups"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                # Convert instructor name back to ID for saving
                instructor_id = {v: k for k, v in instructor_options.items()}[row["instructor_name"]]
                
                group = session.exec(select(Group).where(Group.id == row["id"])).first()
                group.name = row["name"]
                group.gender = row["gender"]
                group.age_group = row["age_group"]
                group.instructor_id = instructor_id  # Save correct ID
                session.commit()
        st.session_state.success_toast = True  # Set flag to show toast after rerun
        st.rerun()  # Force rerun
    
    if st.button("Delete Groups"):
        # Delete selected groups
        delete_ids = edited_df[edited_df["Delete"]]["id"].tolist()
        if delete_ids:
            try:
                session.exec(delete(Group).where(Group.id.in_(delete_ids)))
                session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
            except Exception as e:
                st.error(f"❌ Error: Cannot delete row(s) due to existing references. Remove related records first.")  # Show error if deletion blocked due to foreign key constraint

    # 📌 Add Group Modal
    @st.dialog("Add New Group")
    def add_group_form():
        with st.form("add_group"):
            name = st.text_input("Group Name")
            gender = st.selectbox("Gender", ["M", "F", "MIXED"])
            age_group = st.number_input("Age Group", min_value=0, max_value=100)
            instructor_id = st.selectbox("Instructor", list(instructor_options.keys()), format_func=lambda x: instructor_options[x])

            submitted = st.form_submit_button("Add Group")
            if submitted and name:
                with get_session() as session:
                    session.add(Group(name=name, gender=gender, age_group=age_group, instructor_id=instructor_id))
                    session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun

    # Trigger Add New Group modal when the button is clicked
    if st.button("Add New Group"):
        add_group_form()

with tab2:
    st.title("Manage Instructores")

    # 📌 Display and Edit Instructores
    df = fetch_data(Instructor)
    df["Delete"] = False  # Add a delete column (checkboxes)
    edited_df = st.data_editor(
        df,
        key="instructor_editor",
        disabled=["id"],
        hide_index=True,
        column_config={
            'name': "Name"
        },
        column_order=['name', 'Delete'])

    # 📌 Save Changes
    if st.button("Update Instructors"):
        with get_session() as session:

            # Update remaining instructors
            for index, row in edited_df.iterrows():
                session.exec(
                    select(Instructor)
                    .where(Instructor.id == row["id"])
                ).first().name = row["name"]
            session.commit()
            st.session_state.success_toast = True  # Set flag to show toast after rerun
            st.rerun()  # Force rerun
    
    if st.button("Delete Instructors"):
        # Delete selected instructors
        delete_ids = edited_df[edited_df["Delete"]]["id"].tolist()
        if delete_ids:
            try:
                session.exec(delete(Instructor).where(Instructor.id.in_(delete_ids)))
                session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
            except Exception as e:
                st.error(f"❌ Error: Cannot delete row(s) due to existing references. Remove related records first.")  # Show error if deletion blocked due to foreign key constraint

    # 📌 Add Instructor Modal
    @st.dialog("Add New Instructor")
    def add_instructor_form():
        with st.form("add_instructor"):
            name = st.text_input("Instructor Name")
            submitted = st.form_submit_button("Add Instructor")
            if submitted and name:
                with get_session() as session:
                    session.add(Instructor(name=name))
                    session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun

    # Trigger Add New Instructor modal when the button is clicked
    if st.button("Add New Instructor"):
        add_instructor_form()


with tab3:

    st.title("Venues")
    df = fetch_data(Venue)
    df["Delete"] = False  # Add a delete column (checkboxes)
    edited_df = st.data_editor(
        df,
        key="venue_editor",
        disabled=["id"],
        hide_index=True,
        column_config={
            'name': "Name"
        },
        column_order=['name', 'Delete']
    )

    if st.button("Update Venues"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                venue = session.exec(select(Venue).where(Venue.id == row["id"])).first()
                venue.name = row["name"]
                session.commit()
        st.session_state.success_toast = True  # Set flag to show toast after rerun
        st.rerun()  # Force rerun

    if st.button("Delete Venues"):
        # Delete selected Venues
        delete_ids = edited_df[edited_df["Delete"]]["id"].tolist()
        if delete_ids:
            try:
                session.exec(delete(Venue).where(Venue.id.in_(delete_ids)))
                session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
            except Exception as e:
                st.error(f"❌ Error: Cannot delete row(s) due to existing references. Remove related records first.")  # Show error if deletion blocked due to foreign key constraint

    # 📌 Add Venue Modal
    @st.dialog("Add New Venue")
    def add_venue_form():
        with st.form("add_venue"):
            name = st.text_input("Venue Name")
            submitted = st.form_submit_button("Add Venue")
            if submitted and name:
                with get_session() as session:
                    session.add(Venue(name=name))
                    session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun

    # Trigger Add New Venue modal when the button is clicked
    if st.button("Add New Venue"):
        add_venue_form()

with tab4:
    st.title("Tags")

    st.write("Use Tags to label either Groups, Instructors, Venues or Activities. You can later create complex rules for your Timetable based on tags.")

    df_tag = fetch_data(Tag)
    df_tag["Delete"] = False
    edited_df_tag = st.data_editor(
        df_tag,
        key="tag_editor",
        disabled=["id"],
        hide_index=True,
        column_config={
            'name': "Name"
        },
        column_order=['name', "Delete"]
    )

    if st.button("Update Tags"):
        with get_session() as session:
            for index, row in edited_df_tag.iterrows():
                tag = session.exec(select(Tag).where(Tag.id == row["id"])).first()
                tag.name = row["name"]
                session.commit()
        st.session_state.success_toast = True  # Set flag to show toast after rerun
        st.rerun()

    if st.button("Delete Tags"):
        # Delete selected Venues
        delete_ids = edited_df_tag[edited_df_tag["Delete"]]["id"].tolist()
        if delete_ids:
            try:
                session.exec(delete(Tag).where(Tag.id.in_(delete_ids)))
                session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
            except Exception as e:
                st.error(f"❌ Error: Cannot delete row(s) due to existing references. Remove related records first.")  # Show error if deletion blocked due to foreign key constraint


    @st.dialog("Add New Tag")
    def add_tag_form():
        with st.form("add_venue"):
            name = st.text_input("Tag Name")
            submitted = st.form_submit_button("Add Tag")
            if submitted and name:
                with get_session() as session:
                    session.add(Tag(name=name))
                    session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
    # Trigger Add New modal when the button is clicked
    if st.button("Add New Tag"):
        add_tag_form()

with tab5:
    st.write("### Manage Activities")

    # 📌 Display and Edit Instructores
    df = fetch_data(Activity)
    df["Delete"] = False
    edited_df = st.data_editor(
        df,
        key="activity_editor",
        disabled=["id"],
        hide_index=True,
        column_config={
            'name': "Name"
        },
        column_order=['description', 'duration_minutes', "Delete"]
    )

    # 📌 Save Changes
    if st.button("Update Activities"):
        with get_session() as session:
            for index, row in edited_df.iterrows():
                session.exec(
                    select(Activity)
                    .where(Activity.id == row["id"])
                ).first().description = row["description"]
            session.commit()
        st.session_state.success_toast = True  # Set flag to show toast after rerun
        st.rerun()  # Force rerun

    if st.button("Delete Activities"):
        # Delete selected Venues
        delete_ids = edited_df[edited_df["Delete"]]["id"].tolist()
        if delete_ids:
            try:
                session.exec(delete(Activity).where(Activity.id.in_(delete_ids)))
                session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun
            except Exception as e:
                st.error(f"❌ Error: Cannot delete row(s) due to existing references. Remove related records first.")  # Show error if deletion blocked due to foreign key constraint

    # 📌 Add Activity Modal
    @st.dialog("Add New Activity")
    def add_activity_form():
        with st.form("add_activity"):
            description = st.text_input("Activity Description")
            dur = st.number_input("Activity Duration (minutes)", min_value=0, step=5, format="%d")
            submitted = st.form_submit_button("Add Activity")
            if submitted and description:
                with get_session() as session:
                    session.add(Activity(description=description, duration_minutes=dur))
                    session.commit()
                st.session_state.success_toast = True  # Set flag to show toast after rerun
                st.rerun()  # Force rerun

    # Trigger Add New Activity modal when the button is clicked
    if st.button("Add New Activity"):
        add_activity_form()
