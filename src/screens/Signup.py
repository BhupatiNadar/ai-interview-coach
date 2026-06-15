import streamlit as st
import os
import bcrypt

from src.Ui.base_layout import Signup_screens_layout
from src.Database.db import create_new_user





def User_login(name,email,password,confirm_password):
    if not name:
        st.warning("Please enter your Full name")
                
    elif not email:
        st.warning("Please enter your email")
                
    elif not password:
        st.warning("please enter a password")
                
    elif password != confirm_password:
        st.warning("Password and Confirm Password Did not match")
                
    else:
        password_bytes = password.encode("utf-8")
                
        hashed_password = bcrypt.hashpw(
                password_bytes,
                bcrypt.gensalt()
                ).decode("utf-8")
        try:       
            create_new_user(name,email,hashed_password)
            st.success("Account created successfully")
            st.session_state["login_type"] = "Login"
            st.rerun()
        
        except Exception as e:
            st.warning(f"Something went Wrong problem : {e}")
            
            





def SignupScreen():
    Signup_screens_layout()
    
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    right_panel_img = os.path.join(base_path, "src", "assets", "right_panel_img.png")
    
    col1, col2 = st.columns([1, 1.2], gap="small")

    with col1:
        st.markdown(
f"""<div class="left-panel">
        <div class="logo">🎯 <b>AI Interview</b><br><span class="purple">Coach</span></div>
        <div class="heading">Create your account<br><span class="purple">and ace your next<br>job interview.</span></div>
        <div class="subtext">Join thousands of candidates who trust our AI to prepare smarter, not harder.</div>
        <div class="feature"><div class="feature-icon">🎤</div>
        <div>
            <div class="feature-title">Realistic Mock Interviews</div>
            <div class="feature-desc">Practice with AI interviewers tailored to your target role and industry.</div>
            </div>
            </div>
            <div class="feature">
                <div class="feature-icon">🛡️</div>
                <div>
                    <div class="feature-title">Secure & Private</div>
                    <div class="feature-desc">Your data is encrypted and your sessions stay private.</div>
                </div>
            </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <div>
                    <div class="feature-title">AI-Powered Feedback</div>
                    <div class="feature-desc">Get detailed analysis and actionable tips to improve your performance.</div>
                    </div>
                    </div>
                    """,
            unsafe_allow_html=True
        )
        
        st.image(right_panel_img, width="stretch")
        

    with col2:
        
        top_left, top_right = st.columns([4, 1], gap="small")
        with top_left:
            st.markdown('<div class="signin">Already have an account? </div>', unsafe_allow_html=True)
        with top_right:
            if st.button("Login", key="signup_btn",width='stretch'):
                st.session_state["login_type"] = "Login"
                st.rerun()

        st.markdown('<div class="form-title">Create your account 👋</div><div class="form-sub">Start your journey to acing every interview.</div>', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;gap:10px;"></div>', unsafe_allow_html=True)

        name = st.text_input("Full name", key="login_name")
        email = st.text_input("Email address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="login_confirm_password")
        
        st.divider()

        
        if st.button("Create Account",use_container_width=True):
            User_login(name,email,password,confirm_password)
            

        st.markdown(
"""<div class="footer">🔒 Your interview data is safe and encrypted</div>""",
            unsafe_allow_html=True
        )
