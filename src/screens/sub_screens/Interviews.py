import streamlit as st


def interviews():

    st.header("Choose Interview Type")
    st.write("Select the type of interview you want to practice.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💻")
        st.write("### Technical Interview")
        st.write("Practice technical questions based on your skills.")
        if st.button("Start Technical", key="technical"):
            st.session_state["interview_type"] = "Technical Interview"
            st.rerun()


    with col2:
        st.subheader("👤")
        st.write("### Behavioral Interview")
        st.write("Practice behavioral and HR questions.")
        if st.button("Start Behavioral", key="behavioral"):
            st.session_state["interview_type"] = "Behavioral Interview"
            st.rerun()


    with col3:
        st.subheader("🏢")
        st.write("### Company Specific")
        st.write("Practice questions asked by top companies.")
        if st.button("Start Company", key="company"):
            st.session_state["interview_type"] = "Company Specific"
            st.rerun()


    st.divider()

    st.subheader("Advanced Options")

    
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("🎙️ Voice Interview")
        st.write("Practice interview with voice interaction.")

        if st.button("Start Voice Interview", key="voice"):
            st.session_state["interview_type"] = "Voice Interview"
            st.rerun()


    with col5:
        st.subheader("💻 Coding Interview")
        st.write("Solve coding problems and get AI feedback.")

        if st.button("Start Coding Interview", key="coding"):
            st.session_state["interview_type"] = "Coding Interview"
            st.rerun()

