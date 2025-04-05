import streamlit as st
import datetime
from db import fetch_data, get_session, fetch_objs
from models import DayPlanningTimePeriod, Day, Venue, Instructor, Group, Activity
from datetime import time
from opt import Instance, TimetableSolver
from streamlit_calendar import calendar


st.set_page_config(
    page_title="Results",
    page_icon=":top:",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title(":calendar: Calendar View")

calendar_events = [
    {
        "title": "Math - LH1",
        "daysOfWeek": [1],  # Monday
        "startTime": "09:30:00",
        "endTime": "10:30:00",
        "resourceId": "group_a",  # Group View
        "extendedProps": {
            "teacherId": "teacher_1",
            "venueId": "venue_1",
        }
    },
    {
        "title": "Science Lab",
        "daysOfWeek": [3],  # Wednesday
        "startTime": "11:00:00",
        "endTime": "12:00:00",
        "resourceId": "group_b",  # Group View
        "extendedProps": {
            "teacherId": "teacher_2",
            "venueId": "venue_2",
        }
    },
    {
        "title": "Sports",
        "daysOfWeek": [5],  # Friday
        "startTime": "14:00:00",
        "endTime": "15:00:00",
        "resourceId": "group_c",  # Venue View
        "extendedProps": {
            "teacherId": "teacher_3",
            "groupId": "venue_3",
        }
    },
]

group_resources = [
    {"id": "group_a", "title": "Group A"},
    {"id": "group_b", "title": "Group B"},
    {"id": "group_c", "title": "Group C"},
]

teacher_resources = [
    {"id": "teacher_1", "title": "Mr. Smith"},
    {"id": "teacher_2", "title": "Ms. Johnson"},
    {"id": "teacher_3", "title": "Dr. Brown"},
]

venue_resources = [
    {"id": "venue_1", "title": "Classroom 101"},
    {"id": "venue_2", "title": "Lab 202"},
    {"id": "venue_3", "title": "Auditorium"},
]

calendar_options = {
    "editable": True,
    "selectable": True,
    "initialDate": "2024-04-01",  # Start on a Monday
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": 'Weekly,timeGridDay'
    },
    "dayHeaderFormat": { "weekday": "short" },  # 🗓️ Show only "Mon", "Tue", etc.
    "slotDuration": "00:15:00",
    "slotMinTime": "09:00:00",
    "slotMaxTime": "17:00:00",
    "initialView": 'Weekly',
    "views": {
        "Weekly": {
            "type": 'timeGridWeek',
            "firstDay": 1
            }
    },
    "locale": "es",
    "allDaySlot": False,
    "expandRows": False
}

calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    key='calendar', # Assign a widget key to prevent state loss
    )