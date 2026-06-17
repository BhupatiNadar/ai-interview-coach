import streamlit as st

from src.Database.db import get_latest_resume

from src.agents.Technical_Interview_Agent import generate_questions



def technical_interview():


    st.header("💻 Technical Interview")


    if "resume_structured_data" not in st.session_state:


        resume_data = get_latest_resume()


        if resume_data:

            st.session_state[
                "resume_structured_data"
            ] = resume_data["structured_data"]


        else:

            st.warning(
                "No Resume Found"
            )

            return



    resume = st.session_state[
        "resume_structured_data"
    ]




    if st.button(
        "Generate Technical Questions"
    ):



        with st.spinner(
            "Generating..."
        ):



            result = generate_questions(resume)



            st.session_state[
                "questions"
            ] = result.questions



    if "questions" in st.session_state:


        st.subheader(
            "Interview Questions"
        )


        for i, q in enumerate(
            st.session_state["questions"], 1
        ):
            st.markdown(f"**{i}.** {q}")