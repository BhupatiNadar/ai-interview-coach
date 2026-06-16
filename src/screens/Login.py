import streamlit as st 
import os

from src.Ui.base_layout import Login_screens_layout
from src.Database.db import check_user






def Check_Login_User(email, password):
    if not email:
        st.warning("Please enter your email")
    elif not password:
        st.warning("Please enter your password")
    else:
        try:
            login,user_data=check_user(email, password)
            if login:
                st.session_state["User_login"] = True
                st.session_state["User_data"]=user_data[0]
                st.rerun()
            else:
                st.warning("Password or email doesn't match")
        except Exception as e:
            st.warning(f"Something Went Wrong: {e}")






def LoginScreen():
    Login_screens_layout()
    
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    Signup_right_panel_img = os.path.join(base_path, "src", "assets", "Signup_right_panel_img.jpg")
    
    col1, col2 = st.columns([1, 1.2], gap="small")
    
    with col1:
        st.markdown("""
                 <div class="left-panel">
                  <div class="logo">🎯 <b>AI Interview</b><span class="purple">Coach</span></div>
                  
                  <div class="heading">Your Interview Prep. Smarter Practice.</div>
                  
                  <div class="subtext">Practice mock interviews and get real-time AI feedback to land your dream job</div>
                  
                    <div class="feature">
                        <div class="feature-icon">🎤</div>
                        <div>
                            <div class="feature-title">Mock Interviews</div>
                            <div class="feature-desc">Practice with AI-powered interviews tailored to your target role</div>
                        </div>
                    </div>
                    
                    <div class="feature">
                        <div class="feature-icon">📊</div>
                        <div>
                            <div class="feature-title">Instant Feedback</div>
                            <div class="feature-desc">Get detailed performance analysis and tips to improve your answers</div>
                        </div>
                    </div>
                    
                    <div class="feature">
                        <div class="feature-icon">🔒</div>
                        <div>
                            <div class="feature-title">Secure & Private</div>
                            <div class="feature-desc">Your sessions and data are always secure and private</div>
                        </div>
                    </div>
                    
                 </div>
                    """,unsafe_allow_html=True)
        
        st.image(Signup_right_panel_img)
    
    with col2:

        top_left, top_right = st.columns([4, 1], gap="small")
        with top_left:
            st.markdown('<div class="signin">Don\'t have an account? </div>', unsafe_allow_html=True)
        with top_right:
            if st.button("Signup", key="signup_btn",width='stretch'):
                st.session_state["login_type"] = "Signup"
                st.rerun()

        st.markdown('<div class="form-title">Welcome back 👋</div><div class="form-sub">Sign in to continue to your AI Interview Coach</div>', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;gap:10px;"></div>', unsafe_allow_html=True)

        email = st.text_input("Email address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        st.divider()

        
        if st.button("Login",use_container_width=True):
            Check_Login_User(email,password)

        st.markdown(
"""<div class="footer">🔒 Your interview data is safe and encrypted</div>""",
            unsafe_allow_html=True
        )

    