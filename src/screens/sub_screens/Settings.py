import streamlit as st

def settings():
    st.title("Setting Page")
    
    if st.button("Logout"):
        st.session_state["login_type"] = None
        st.session_state["User_login"] = None
        st.session_state["User_data"] = None
        st.session_state["User_tab"] = "Dashboard"
        st.rerun()