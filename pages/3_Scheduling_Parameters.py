import streamlit as st
import datetime
from db import fetch_data, get_session, fetch_objs
from models import DayPlanningTimePeriod, Day, Venue, Instructor, Group, Activity, Schedule, minutes_to_day_time
from datetime import time
from opt import Instance, TimetableSolver
from streamlit_calendar import calendar
import json


st.set_page_config(
    page_title="Scheduling Parameters",
    page_icon=":pencil:",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title(":calendar: Scheduling Parameters")

if st.sidebar.button("Auto-Plan"):
    instructors = fetch_objs(Instructor)
    groups = fetch_objs(Group)
    venues = fetch_objs(Venue)
    activities = fetch_objs(Activity)
    opening_hours = fetch_objs(DayPlanningTimePeriod)

    new_instance = Instance(groups=groups, instructors=instructors, venues=venues, activities=activities, opening_times=opening_hours)

    solver = TimetableSolver(instance=new_instance)
    scheduled_activities, proto = solver.build()
    with get_session() as session:
        session.add(Schedule(
            proto=proto,
            result=json.dumps({i: e.to_dict() for i, e in enumerate(scheduled_activities)})
            ))
        session.commit()

st.write("## Define Scheduling Times")
df = fetch_data(DayPlanningTimePeriod)
df["Delete"] = False  # Add a delete column (checkboxes)
edited_df = st.data_editor(
    df,
    key="day_panning_editor",
    hide_index=True,
    column_config={
        'day': "Day Type"
    },
    column_order=['day', 'opening_time', 'closing_time','Delete'])

# 📌 Add Day Modal
@st.dialog("Add Planning Time Period")
def add_day_form():
    with st.form("Add Planning Time Period"):
        day = st.selectbox("Select Day", [d.value for d in Day])
        opening_time = st.time_input("Opening Time", value=time(9, 0))
        closing_time = st.time_input("Closing Time", value=time(16, 30))
        submit_button = st.form_submit_button("Add Entry")
        if submit_button and day:
            with get_session() as session:
                session.add(DayPlanningTimePeriod(day=Day(day), opening_time=opening_time, closing_time=closing_time))
                session.commit()
            st.session_state.success_toast = True  # Set flag to show toast after rerun
            st.rerun()  # Force rerun

# Constraints Section
st.header("⚡ Define Constraints")
st.markdown(
    """
    Constraints are **strict limitations** that must be respected during the scheduling process. These help avoid conflicts and ensure the timetable follows hard rules.

    **Examples:**
    - Set the **earliest start time for an activity to 8:00 AM**.
    - Exclude **specific venues for a particular group**.
    - Limit **instructors to a maximum of 6 teaching hours per day**.
    """
)

# Rules Section
st.header("⚖️ Rules")
st.markdown(
    """
    Rules are **specific conditions** that help guide the scheduling process. These can be **mandatory** or **optional goals** with different priority levels.

    **Examples:**
    - Ensure **a single instructor is assigned to a group for an entire course**.
    - Restrict **sports training to outdoor facilities after 4:00 PM**.
    - Allow **only certified labs for chemistry experiments**.
    """
)

# Logic Section
st.header("🧠 Logic")
st.markdown(
    """
    Logic handles **sequence-based relationships** between activities. These define **dependencies** and **ordering conditions** that must be followed.

    **Examples:**
    - If **Math I is scheduled on Monday, Math II must follow on the same day**.
    - **Lab I must be scheduled before Lab II**.
    - If an **exam is held in the morning, a review session should be scheduled the previous day**.
    """
)

# Priorities Section
st.header("🎯 Priorities")
st.markdown(
    """
    Priorities allow you to define **goal-based preferences** with **high**, **medium**, or **low importance**. The system will aim to meet these preferences while minimizing penalties for violations.

    **Examples:**
    - **High Priority:** Schedule **popular classes in larger venues**.
    - **Medium Priority:** Allocate **the best-equipped room for science classes**.
    - **Low Priority:** Assign **the same instructor for consecutive sessions to avoid transitions**.
    """
)


# Trigger Add New Venue modal when the button is clicked
if st.button("Add Planning Time Period"):
    add_day_form()