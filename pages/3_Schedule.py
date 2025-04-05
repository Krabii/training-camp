import streamlit as st
import datetime
from db import fetch_data, get_session, fetch_objs
from models import DayPlanningTimePeriod, Day, Venue, Instructor, Group, Activity
from datetime import time
from opt import Instance, TimetableSolver
from streamlit_calendar import calendar


st.set_page_config(
    page_title="Schedule",
    page_icon=":pencil:",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title(":calendar: Schedule Activities")

if st.sidebar.button("Auto-Plan"):
    instructors = fetch_objs(Instructor)
    groups = fetch_objs(Group)
    venues = fetch_objs(Venue)
    activities = fetch_objs(Activity)
    opening_hours = fetch_objs(DayPlanningTimePeriod)

    new_instance = Instance(groups=groups, instructors=instructors, venues=venues, activities=activities, opening_times=opening_hours)

    solver = TimetableSolver(instance=new_instance)
    scheduled_activities = solver.build()
    st.write(scheduled_activities)

calendar_options = {
    "editable": True,
    "selectable": True,
    "firstDay": 1,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "timeGridWeek",
    },
    "dayHeaderFormat": { "weekday": "short" },  # 🗓️ Show only "Mon", "Tue", etc.
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "timeGridWeek"
}
calendar_events = [
    {
        "title": "Math Class",
        "daysOfWeek": [1],  # Monday
        "startTime": "09:30:00",
        "endTime": "10:30:00",
    },
    {
        "title": "Science Lab",
        "daysOfWeek": [3],  # Wednesday
        "startTime": "11:00:00",
        "endTime": "12:00:00",
    },
    {
        "title": "Sports",
        "daysOfWeek": [5],  # Friday
        "startTime": "14:00:00",
        "endTime": "15:00:00",
    },
]

calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    key='calendar', # Assign a widget key to prevent state loss
    )
st.write(calendar)

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

# Trigger Add New Venue modal when the button is clicked
if st.button("Add Planning Time Period"):
    add_day_form()