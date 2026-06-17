import streamlit as st

from src.Database.db import get_latest_resume, save_interview_result, save_interview_evaluation
from src.agents.Behavioral_Interview_Agent import generate_questions, evaluate_answers


def behavioral_interview():

    st.header("🗣️ Behavioral Interview")
    st.caption("Focus on Leadership, Teamwork, and STAR Method Scenarios")

    if "resume_structured_data" not in st.session_state:
        resume_data = get_latest_resume()
        if resume_data:
            st.session_state["resume_structured_data"] = resume_data["structured_data"]
        else:
            st.warning("No Resume Found. Please upload a resume to continue.")
            if st.button("Go to Resume Upload"):
                st.session_state["User_tab"] = "Resume"
                st.rerun()
            return

    if "current_question" not in st.session_state:
        st.session_state["current_question"] = 0

    if "answers" not in st.session_state:
        st.session_state["answers"] = []

    resume = st.session_state["resume_structured_data"]

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("Back to Previous Page", width='stretch'):
            st.session_state["current_question"] = 0
            st.session_state["answers"] = []
            st.session_state["interview_saved"] = False
            st.session_state["interview_type"] = None

            if "questions" in st.session_state:
                del st.session_state["questions"]

            st.rerun()

    with col1:

        if st.button("Generate Behavioral Questions", width='stretch'):
            with st.spinner("🤖 Analyzing resume and generating behavioral questions..."):
                result = generate_questions(resume)
                st.session_state["questions"] = result.questions
                st.session_state["current_question"] = 0
                st.session_state["answers"] = []
                st.rerun()

        if "questions" not in st.session_state or st.session_state["questions"] == None:
            st.info("Click the button above to generate your personalized behavioral interview questions.")
            return

        questions = st.session_state["questions"]
        current = st.session_state["current_question"]

        if current >= len(questions):
            st.success("🎉 Behavioral Interview Completed!")

            if not st.session_state.get("interview_saved", False):
                with st.spinner("🤖 Evaluating your answers using the STAR method..."):
                    interview_answers = []

                    for q, a in zip(questions, st.session_state["answers"]):
                        interview_answers.append(
                            {
                                "question": q,
                                "answer": a
                            }
                        )

                    interview_response = save_interview_result(
                        user_id=st.session_state["User_data"].get("user_id"),
                        interview_type="Behavioral",
                        question_answers=interview_answers
                    )
                    
                    interview_id = interview_response.data[0]["interview_id"] if interview_response.data else None
                    
                    try:
                        Evaluation = evaluate_answers(interview_answers)
                        
                        if "Evaluation" not in st.session_state:
                            st.session_state["Evaluation"]=None
                        
                        st.session_state["Evaluation"]=Evaluation.model_dump()
                        
                        if interview_id:
                            save_interview_evaluation(interview_id=interview_id, evaluation_data=st.session_state["Evaluation"])
                        
                        st.session_state["interview_saved"] = True
                        st.success("✅ Interview evaluated and saved successfully!")
                        
                    except Exception as e:
                        st.error(f"Failed to evaluate answers: {e}")
            else:
                st.success("✅ Interview evaluated and saved successfully!")

            st.divider()
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("View Full Report", width='stretch'):
                    st.session_state["User_tab"] = "Reports"
                    st.rerun()
            with col_b2:
                if st.button("Start Over", key="start_over", width='stretch'):
                    st.session_state["current_question"] = 0
                    st.session_state["answers"] = []
                    st.session_state["interview_saved"] = False
                    if "questions" in st.session_state:
                        del st.session_state["questions"]
                    st.rerun()

            return

        question = questions[current]

        with st.container(border=True):
            st.subheader(f"Question {current + 1} of {len(questions)}")
            st.write(f"**{question}**")

        st.info("💡 **Tip:** Use the **STAR** method for behavioral questions: **S**ituation, **T**ask, **A**ction, **R**esult.")

        answer = st.text_area("Your Answer", height=200, key=f"answer_{current}", placeholder="Type your detailed answer here using the STAR format...")

        col_sub, col_skip = st.columns([1, 3])
        with col_sub:
            if st.button("Submit Answer", key="submit_answer", width='stretch'):
                if answer.strip() == "":
                    st.warning("Please enter your answer")
                else:
                    st.session_state["answers"].append(answer)
                    st.session_state["current_question"] += 1
                    st.rerun()