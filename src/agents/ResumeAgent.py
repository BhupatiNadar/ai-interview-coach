import streamlit as st

from typing import List, Optional
from pydantic import BaseModel

from agno.agent import Agent
from agno.models.openai import OpenAIChat


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


resume_agent = Agent(
    model=OpenAIChat(
        id="meta-llama/Llama-3.1-8B-Instruct",
        api_key=st.secrets["HF_TOKEN"],
        base_url="https://router.huggingface.co/v1"
    ),

    name="ResumeParserAgent",
    markdown=False,

    output_schema=ResumeData,
    use_json_mode=True,

    instructions="""
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

{
 "summary":"",
 "skills":[],
 "experience":[],
 "projects":[]
}
"""
)