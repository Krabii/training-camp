import streamlit as st
import datetime
import json
from db import fetch_data, get_session, fetch_objs
from models import DayPlanningTimePeriod, Schedule, Activity, minutes_to_day_time
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

# Write Calendar events
activities = fetch_objs(Activity)
schedules = fetch_objs(Schedule)
scheduled_activities = json.loads(schedules[-1].result)

events = []
for a in scheduled_activities:
    activity = [x for x in activities if x.id == scheduled_activities[a]['activity_id']][0]
    events.append({
        "title": scheduled_activities[a]['title'],
        "daysOfWeek": [scheduled_activities[a]['days_of_week']],  # Recurring
        "startTime": scheduled_activities[a]["start_time"],
        "endTime": scheduled_activities[a]['end_time'],
        "resourceId": scheduled_activities[a]["group_id"],
        "extendedProps": {
            "teacherId": scheduled_activities[a]['instructor_id'],
            "venueId": scheduled_activities[a]['venue_id'],
        }
    })

calendar_options = {
    "editable": True,
    "selectable": True,
    "initialDate": "2024-04-01",  # Start on a Monday
    "firstDay": 1,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": 'Weekly,timeGridDay'
    },
    "dayHeaderFormat": { "weekday": "short" },  # 🗓️ Show only "Mon", "Tue", etc.
    "slotDuration": "00:15:00",
    "slotMinTime": "08:00:00",
    "slotMaxTime": "18:00:00",
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
    events=events,
    options=calendar_options,
    key='calendar', # Assign a widget key to prevent state loss
    )
