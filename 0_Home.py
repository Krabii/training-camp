import streamlit as st


st.set_page_config(
    page_title="Training Facility",
    page_icon=":house:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title("Traning Facility Scheduler :soccer:")
st.write(
    "Weekly planner :calendar: for scheduling training sessions in a soccer training facility."
)

st.sidebar.header("Home Page")

if st.sidebar.button("Init DB"):
    from db import create_db
    create_db()