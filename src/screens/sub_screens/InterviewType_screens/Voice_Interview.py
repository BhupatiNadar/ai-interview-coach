import streamlit as st
import streamlit.components.v1 as components
import os
import json
from src.Database.db import save_interview_result, save_interview_evaluation
from src.agents.Technical_Interview_Agent import generate_questions, evaluate_answers

# Ensure absolute path is used and correct
COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "components", "voice_interviewer")
_voice_interviewer = components.declare_component(
    "voice_interviewer",
    path=os.path.abspath(COMPONENT_DIR)
)

def voice_interviewer(question_text, key=None):
    return _voice_interviewer(question_text=question_text, key=key)


def voice_interview():
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🗣️ Voice Interview Coach</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if 'voice_started' not in st.session_state:
        st.session_state.voice_started = False
    if 'voice_questions' not in st.session_state:
        st.session_state.voice_questions = []
    if 'voice_answers' not in st.session_state:
        st.session_state.voice_answers = []
    if 'voice_current_q' not in st.session_state:
        st.session_state.voice_current_q = 0

    if not st.session_state.voice_started:
        st.markdown("""
        ### Welcome to the Hands-Free Voice Interview.
        
        **How it works:**
        1. Click **Start Interview** below.
        2. The AI will speak a question aloud.
        3. After a 3-second pause, the microphone will automatically turn on.
        4. Speak your answer clearly.
        5. Stop speaking for **10 seconds**, and the system will automatically submit your answer and proceed.
        """)
        
        st.info("💡 Ensure your browser has microphone permissions enabled.")
        
        # Simple input to let user set the topic or use default
        role_topic = st.text_input("Job Role or Topic (Optional)", placeholder="e.g., Software Engineer, Marketing, etc.")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🎤 Start Interview", use_container_width=True):
                with st.spinner("Generating interview questions..."):
                    # Use the agent to generate questions
                    context = f"Candidate for {role_topic} role." if role_topic else "General candidate for technical role."
                    question_set = generate_questions(context)
                    st.session_state.voice_questions = question_set.questions
                
                st.session_state.voice_answers = []
                st.session_state.voice_current_q = 0
                st.session_state.voice_started = True
                st.rerun()
            
    else:
        # Interview is active
        idx = st.session_state.voice_current_q
        questions = st.session_state.voice_questions
        
        if idx < len(questions):
            current_question = questions[idx]
            
            st.markdown(f"### Question {idx + 1} of {len(questions)}")
            st.info(current_question)
            
            # Render the custom component
            # The component plays audio, waits 3s, listens, waits 10s silence, and returns text
            transcript = voice_interviewer(question_text=current_question, key=f"q_{idx}")
            
            if transcript:
                if str(transcript).startswith("ERROR"):
                    st.error(transcript)
                    if st.button("Next Question Manually"):
                        st.session_state.voice_answers.append({"question": current_question, "answer": "Skipped due to error"})
                        st.session_state.voice_current_q += 1
                        st.rerun()
                else:
                    # Save transcript
                    st.session_state.voice_answers.append({
                        "question": current_question,
                        "answer": transcript
                    })
                    st.session_state.voice_current_q += 1
                    st.rerun()
                
        else:
            st.success("🎉 Interview Complete!")
            st.balloons()
            
            st.markdown("### Your Responses")
            for i, qa in enumerate(st.session_state.voice_answers):
                with st.expander(f"Q{i+1}: {qa['question']}"):
                    st.write(f"**Answer:** {qa['answer']}")
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Finish, Evaluate & Save", use_container_width=True):
                    if "User_data" in st.session_state and "user_id" in st.session_state["User_data"]:
                        user_id = st.session_state["User_data"]["user_id"]
                        try:
                            with st.spinner("Evaluating your answers..."):
                                evaluation = evaluate_answers(st.session_state.voice_answers)
                                # Convert Pydantic model to dict for database
                                eval_dict = evaluation.dict() if hasattr(evaluation, "dict") else evaluation.model_dump()
                                
                            # Save to Database using the provided function
                            response = save_interview_result(user_id, "Voice Interview", st.session_state.voice_answers)
                            
                            if response.data:
                                interview_id = response.data[0]["interview_id"]
                                save_interview_evaluation(interview_id, eval_dict)
                                st.success("Results and evaluation saved successfully!")
                                st.session_state.voice_started = False
                            else:
                                st.error("Failed to save interview session.")
                                
                        except Exception as e:
                            st.error(f"Error evaluating or saving to database: {e}")
                    else:
                        st.warning("User not logged in. Could not save results to database.")
            
            with col2:
                if st.button("Restart Interview", use_container_width=True):
                    st.session_state.voice_started = False
                    st.rerun()