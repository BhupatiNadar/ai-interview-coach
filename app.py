import streamlit as st 

from src.screens.Login import LoginScreen
from src.screens.Signup import SignupScreen
from src.Ui.base_layout import style_base_layout
from src.screens.Home import HomeScreen

def main():
    st.set_page_config(
        page_title="Ai Interview Coach",
        layout="wide"
    )
    style_base_layout()
    
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None
        
    if "User_login" not in st.session_state:
        st.session_state["User_login"] = None
        
    if "User_data" not in st.session_state:
        st.session_state["User_data"] = None
        
    match (st.session_state["login_type"], st.session_state["User_login"]):

        case ("Login", None):
            LoginScreen()

        case ("Signup", None):
            SignupScreen()

        case (_, True):
            HomeScreen()

        case (None, False):
            LoginScreen()

        case (None, None):
            LoginScreen()

if __name__=="__main__":
    main()
