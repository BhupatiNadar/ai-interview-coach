import streamlit as st

from typing import List
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class QuestionSet(BaseModel):
    questions: List[str] = []


class Evaluation(BaseModel):
    question: str = ""
    score: int = 0
    feedback: str = ""
    improvement: str = ""


class InterviewEvaluation(BaseModel):
    total_score: int = 0
    overall_feedback: str = ""
    evaluations: List[Evaluation] = []



llm = ChatOpenAI(
    model="meta-llama/Llama-3.1-8B-Instruct",
    api_key=st.secrets["HF_TOKEN"],
    base_url="https://router.huggingface.co/v1"
)



question_llm = llm.with_structured_output(
    QuestionSet,
    method="json_mode"
)

question_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Generate exactly 10 technical interview questions.
Use the candidate resume.
Focus on:
- Skills
- Projects
- Experience
- Technologies

Return ONLY a JSON object like: {{"questions": ["q1", "q2", ...]}}
No other text.
"""),
    ("human", "Resume:\n{resume}")
])

question_chain = question_prompt | question_llm


def generate_questions(resume) -> QuestionSet:
    return question_chain.invoke({"resume": resume})



evaluation_llm = llm.with_structured_output(
    InterviewEvaluation,
    method="json_mode"
)

evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Evaluate the candidate answers.

Give:
- score (0-10 per question)
- feedback
- improvement

Return ONLY a JSON object like:
{{"total_score": 0, "overall_feedback": "", "evaluations": [{{"question": "", "score": 0, "feedback": "", "improvement": ""}}]}}
No other text.
"""),
    ("human", "{qa_text}")
])

evaluation_chain = evaluation_prompt | evaluation_llm


def evaluate_answers(qa_text) -> InterviewEvaluation:
    return evaluation_chain.invoke({"qa_text": qa_text})