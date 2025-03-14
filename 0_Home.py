import streamlit as st


st.set_page_config(
    page_title="TimeTabling Made Easy",
    page_icon=":calendar:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a demo page. Use without warranty."
    }
)

st.title(":house: Timetabling for Education/Sport Venues")
st.write(
    "Timetabling for Educational and Sporting Centers. Get Optimal Timetables that meet your preferences and goals."
)

st.sidebar.header("Home")

if st.sidebar.button("Init DB"):
    from db import create_db
    create_db()