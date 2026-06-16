import streamlit as st
import os

from src.screens.sub_screens.Dashboard import dashboard
from src.screens.sub_screens.Interviews import interviews
from src.screens.sub_screens.Resume import resume
from src.screens.sub_screens.Practice import practice
from src.screens.sub_screens.Reports import reports
from src.screens.sub_screens.LearningPlan import learning_plan
from src.screens.sub_screens.Settings import settings


def HomeScreen():

    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    logo_ai_interview_coach = os.path.join(
        base_path,
        "src",
        "assets",
        "logo_ai_interview_coach.png"
    )
    

    if "User_tab" not in st.session_state:
        st.session_state["User_tab"] = "Dashboard"


    col1, col2 = st.columns([0.8, 4])


    with col1:

        sub_col1, sub_col2 = st.columns([0.8, 4])


        with sub_col1:
            st.image(logo_ai_interview_coach, width=50)


        with sub_col2:
            st.header("AI Interview Coach")


        if st.button("🏠 Dashboard", width="stretch"):
            st.session_state["User_tab"] = "Dashboard"


        if st.button("📑 Interviews", width="stretch"):
            st.session_state["User_tab"] = "Interviews"


        if st.button("📃 Resume", width="stretch"):
            st.session_state["User_tab"] = "Resume"


        if st.button("🛡️ Practice", width="stretch"):
            st.session_state["User_tab"] = "Practice"


        if st.button("📄 Reports", width="stretch"):
            st.session_state["User_tab"] = "Reports"


        if st.button("📃 Learning plan", width="stretch"):
            st.session_state["User_tab"] = "Learning Plan"


        if st.button("⚙️ Setting", width="stretch"):
            st.session_state["User_tab"] = "Setting"


    with col2:


        match st.session_state["User_tab"]:


            case "Dashboard":
                dashboard()


            case "Interviews":
                interviews()


            case "Resume":
                resume()


            case "Practice":
                practice()


            case "Reports":
                reports()


            case "Learning Plan":
                learning_plan()


            case "Setting":
                settings()