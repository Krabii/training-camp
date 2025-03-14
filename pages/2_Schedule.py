import streamlit as st
import datetime


st.set_page_config(
    page_title="Schedule",
    page_icon=":pencil:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title(":calendar: Schedule Activitys")

# Date Range Selection
date_range = st.date_input("Select a date range", [], format="YYYY-MM-DD")

# Display Selected Dates
if isinstance(date_range, tuple) and len(date_range) == 2:
    st.success(f"Start Date: {date_range[0]}  \nEnd Date: {date_range[1]}")
elif date_range:
    st.warning("Please select both start and end dates.")
