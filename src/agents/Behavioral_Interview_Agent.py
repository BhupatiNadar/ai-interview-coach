import streamlit as st
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.agents.Technical_Interview_Agent import QuestionSet, evaluate_answers

llm = ChatOpenAI(
    model="meta-llama/Llama-3.1-8B-Instruct",
    api_key=st.secrets["HF_TOKEN"],
    base_url="https://router.huggingface.co/v1"
)

question_llm = llm.with_structured_output(QuestionSet, method="json_mode")

question_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Generate exactly 10 behavioral interview questions based on the candidate's resume.
Focus on:
- Leadership and teamwork
- Conflict resolution
- Past experiences and achievements
- Problem-solving scenarios using the STAR method

Return ONLY a JSON object like: {{"questions": ["q1", "q2", ...]}}
No other text.
"""),
    ("human", "Resume:\n{resume}")
])

def generate_questions(resume) -> QuestionSet:
    return (question_prompt | question_llm).invoke({"resume": resume})
