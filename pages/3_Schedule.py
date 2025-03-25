import streamlit as st
import datetime
from db import fetch_data, get_session
from models import DayPlanningTimePeriod, Day
from datetime import time

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
    pass

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