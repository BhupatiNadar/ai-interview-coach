import streamlit as st

def dashboard():
    st.header(f"Welcome back, {(st.session_state["User_data"]).get("user_name")} 👋")
    st.write("Here's your progress overview")
    
    col1,col2,col3,col4=st.columns(4)
    
    with col1:
        st.write("Total Interviews")
        st.markdown(
                        """
                        <div id="interviews_count">
                            0
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
    with col2:
        st.write("Average Score")
        st.markdown(
                        """
                        <div id="average_score">
                            0
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
    with col3:
        st.write("Skill Improvment")
        st.markdown(
                        """
                        <div id="skill_score">
                            0
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
    with col4:
        st.write("Weak Areas")
        st.markdown(
                        """
                        <div id="weak_areas">
                            0
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
    col1,col2=st.columns([3,1])
    
    with col1:
        st.write("Performance Overview")
        
    with col2:
        st.write("Top skills")
        
    st.markdown("""
                
                <div>
                
                """,unsafe_allow_html=True)
    
    col1,col2=st.columns([3,1])
    
    with col1:
        st.write("Recent Interviews")
        
    with col2:
        st.button("View all")
        