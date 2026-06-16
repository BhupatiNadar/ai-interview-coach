import streamlit as st 

def resume_analyze():
    
    col1,col2=st.columns([3,0.8])
    
    with col2:
        if st.button("Back to previous page"):
            st.session_state["User_tab"] = "Resume"
            st.rerun()