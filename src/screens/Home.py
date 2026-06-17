import streamlit as st

from src.screens.sub_screens.Dashboard import dashboard
from src.screens.sub_screens.Interviews import interviews
from src.screens.sub_screens.Resume import resume
from src.screens.sub_screens.Practice import practice
from src.screens.sub_screens.Reports import reports
from src.screens.sub_screens.LearningPlan import learning_plan
from src.screens.sub_screens.Settings import settings
from src.screens.sub_screens.Resume_Analyze import resume_analyze

from src.screens.sub_screens.InterviewType_screens.Behavioral_Interview import behavioral_interview
from src.screens.sub_screens.InterviewType_screens.Coding_Interview import coding_interview
from src.screens.sub_screens.InterviewType_screens.Company_Specific import company_specific
from src.screens.sub_screens.InterviewType_screens.Technical_Interview import technical_interview
from src.screens.sub_screens.InterviewType_screens.Voice_Interview import voice_interview


def HomeScreen():

    if "User_tab" not in st.session_state:
        st.session_state["User_tab"] = "Dashboard"
        
    if "interview_type" not in st.session_state:
        st.session_state["interview_type"] = None


    col1, col2 = st.columns([0.8, 4])


    with col1:

        st.header("AI Interview Coach")


        if st.button("🏠 Dashboard", width="stretch"):
            st.session_state["User_tab"] = "Dashboard"
            st.session_state["interview_type"] = None


        if st.button("📑 Interviews", width="stretch"):
            st.session_state["User_tab"] = "Interviews"
            st.session_state["interview_type"] = None


        if st.button("📃 Resume", width="stretch"):
            st.session_state["User_tab"] = "Resume"
            st.session_state["interview_type"] = None


        if st.button("🛡️ Practice", width="stretch"):
            st.session_state["User_tab"] = "Practice"
            st.session_state["interview_type"] = None


        if st.button("📄 Reports", width="stretch"):
            st.session_state["User_tab"] = "Reports"
            st.session_state["interview_type"] = None


        if st.button("📃 Learning plan", width="stretch"):
            st.session_state["User_tab"] = "Learning Plan"
            st.session_state["interview_type"] = None


        if st.button("⚙️ Setting", width="stretch"):
            st.session_state["User_tab"] = "Setting"
            st.session_state["interview_type"] = None


    with col2:


        match (st.session_state["User_tab"], st.session_state.get("interview_type")):

            case ("Dashboard", _):
                dashboard()

            case ("Interviews", None):
                interviews()


            case ("Interviews", "Technical Interview"):
                technical_interview()


            case ("Interviews", "Behavioral Interview"):
                behavioral_interview()


            case ("Interviews", "Company Specific"):
                company_specific()


            case ("Interviews", "Voice Interview"):
                voice_interview()


            case ("Interviews", "Coding Interview"):
                coding_interview()


            case ("Resume", _):
                resume()


            case ("Practice", _):
                practice()


            case ("Reports", _):
                reports()


            case ("Learning Plan", _):
                learning_plan()


            case ("Setting", _):
                settings()


            case ("Resume_Analyze", _):
                resume_analyze()