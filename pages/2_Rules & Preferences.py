import streamlit as st

st.set_page_config(page_title="Rules & Priorities", page_icon="🛠️", layout="wide")

st.title("🛠️ Set Rules & Priorities for Optimal Scheduling")

# Constraints Section
st.header("⚡ Constraints")
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
