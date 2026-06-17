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
Generate exactly 5 coding interview questions (Data Structures and Algorithms).
Use the candidate's resume to gauge the appropriate difficulty and relevant languages/frameworks.
Focus on providing clear problem statements for coding challenges like:
- Arrays, Strings, Hash Maps
- Trees, Graphs, Dynamic Programming
- Give a specific problem description for each.

Return ONLY a JSON object like: {{"questions": ["q1", "q2", ...]}}
No other text.
"""),
    ("human", "Resume:\n{resume}")
])

def generate_questions(resume) -> QuestionSet:
    return (question_prompt | question_llm).invoke({"resume": resume})
