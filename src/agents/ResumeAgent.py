import streamlit as st
import re

from typing import List
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    years: str = ""


class Project(BaseModel):
    title: str = ""
    description: str = ""
    technologies: List[str] = []


class ResumeData(BaseModel):
    summary: str = ""
    skills: List[str] = []
    experience: List[Experience] = []
    projects: List[Project] = []



llm = ChatOpenAI(
    model="meta-llama/Llama-3.1-8B-Instruct",
    api_key=st.secrets["HF_TOKEN"],
    base_url="https://router.huggingface.co/v1"
)


structured_llm = llm.with_structured_output(
    ResumeData,
    method="json_mode"
)


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a Resume Parsing Agent.

Extract resume information:

- Summary
- Skills
- Experience:
  - Company
  - Role
  - Years

- Projects:
  - Title
  - Description
  - Technologies

Rules:
- Return ONLY valid JSON.
- No markdown.
- No explanation.

JSON:

{{
 "summary":"",
 "skills":[],
 "experience":[],
 "projects":[]
}}
"""),
    ("human", "{resume_text}")
])


chain = prompt | structured_llm


def parse_resume(resume_text: str) -> ResumeData:
    return chain.invoke({"resume_text": resume_text})