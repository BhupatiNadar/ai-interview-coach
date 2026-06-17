import streamlit as st

from src.Database.db import get_latest_resume

from src.agents.Technical_Interview_Agent import generate_questions



def technical_interview():

    st.header("💻 Technical Interview")

    if "resume_structured_data" not in st.session_state:
        resume_data = get_latest_resume()
        if resume_data:
            st.session_state["resume_structured_data"] = resume_data["structured_data"]
        else:
            st.warning("No Resume Found")
            return

    if "current_question" not in st.session_state:
        st.session_state["current_question"] = 0

    if "answers" not in st.session_state:
        st.session_state["answers"] = []

    resume = st.session_state["resume_structured_data"]

    if st.button("Generate Technical Questions"):
        with st.spinner("Generating..."):
            result = generate_questions(resume)
            st.session_state["questions"] = result.questions
            st.session_state["current_question"] = 0
            st.session_state["answers"] = []
            st.rerun()

    if "questions" not in st.session_state or st.session_state["questions"] == None:
        st.info("Click the button above to generate interview questions.")
        return

    questions = st.session_state["questions"]
    current = st.session_state["current_question"]

    if current >= len(questions):
        st.success("🎉 Interview Completed")
        st.subheader("Your Answers")

        for i, (q, a) in enumerate(zip(questions, st.session_state["answers"])):
            st.write(f"### Question {i + 1}")
            st.write(q)
            st.write("### Your Answer")
            st.write(a)

        if st.button("Start Over", key="start_over"):
            st.session_state["current_question"] = 0
            st.session_state["answers"] = []
            del st.session_state["questions"]
            st.rerun()
        return

    question = questions[current]

    st.subheader(f"Question {current + 1}/{len(questions)}")
    st.write(question)

    answer = st.text_area("Your Answer", key=f"answer_{current}")

    if st.button("Submit Answer", key="submit_answer"):
        if answer.strip() == "":
            st.warning("Please enter your answer")
        else:
            st.session_state["answers"].append(answer)
            st.session_state["current_question"] += 1
            st.rerun()

    
    
    