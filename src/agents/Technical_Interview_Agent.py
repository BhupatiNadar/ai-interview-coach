import streamlit as st
import json
import logging

from typing import List
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.exceptions import OutputParserException
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
    ("system", """You are an interview evaluator. You will receive {num_questions} question-answer pairs.

You MUST evaluate EVERY question-answer pair. Your response MUST contain exactly {num_questions} evaluation objects in the "evaluations" array.

For EACH question-answer pair, create an evaluation object with these exact keys:
- "question": the original question text (string)
- "score": your rating from 0 to 10 (integer)
- "feedback": your feedback on the answer (string)
- "improvement": how to improve the answer (string)

Also include:
- "total_score": the sum of all individual scores (integer)
- "overall_feedback": an overall summary of the candidate's performance (string)

Return ONLY valid JSON in this exact format:
{{"total_score": 0, "overall_feedback": "...", "evaluations": [{{"question": "...", "score": 0, "feedback": "...", "improvement": "..."}}]}}

CRITICAL RULES:
1. The "evaluations" array MUST contain exactly {num_questions} objects - one for each question.
2. The "evaluations" array must NEVER be empty.
3. Each evaluation MUST be a JSON object with all four keys: question, score, feedback, improvement.
4. Do NOT return any text outside the JSON object.
"""),
    ("human", "Here are the {num_questions} question-answer pairs to evaluate:\n\n{qa_text}")
])

evaluation_chain = evaluation_prompt | evaluation_llm

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def _format_qa_text(qa_input) -> str:
    """Convert list of Q&A dicts to a clean text format for the LLM."""
    if isinstance(qa_input, list):
        lines = []
        for i, item in enumerate(qa_input, 1):
            q = item.get("question", "N/A") if isinstance(item, dict) else str(item)
            a = item.get("answer", "N/A") if isinstance(item, dict) else ""
            lines.append(f"Question {i}: {q}")
            lines.append(f"Answer {i}: {a}")
            lines.append("")
        return "\n".join(lines)
    return str(qa_input)


def _count_questions(qa_input) -> int:
    """Count the number of questions in the input."""
    if isinstance(qa_input, list):
        return len(qa_input)
    return qa_input.count("Question ")


def evaluate_answers(qa_input) -> InterviewEvaluation:
    """Evaluate answers with retry logic to handle malformed LLM output."""
    qa_text = _format_qa_text(qa_input)
    num_questions = _count_questions(qa_input)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = evaluation_chain.invoke({
                "qa_text": qa_text,
                "num_questions": num_questions
            })

            # Validate: if evaluations is empty, retry
            if not result.evaluations:
                logger.warning(
                    f"Attempt {attempt}/{MAX_RETRIES}: LLM returned empty evaluations, retrying..."
                )
                if attempt == MAX_RETRIES:
                    break  # Fall through to fallback
                continue

            return result

        except (OutputParserException, Exception) as e:
            logger.warning(f"Evaluation attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break  # Fall through to fallback

    # Fallback: build a default evaluation so the app doesn't crash
    logger.error("All evaluation attempts failed. Returning fallback.")
    fallback_evals = []
    if isinstance(qa_input, list):
        for item in qa_input:
            q = item.get("question", "N/A") if isinstance(item, dict) else str(item)
            fallback_evals.append(Evaluation(
                question=q,
                score=0,
                feedback="Evaluation could not be completed due to a processing error.",
                improvement="Please try again."
            ))
    return InterviewEvaluation(
        total_score=0,
        overall_feedback="Evaluation failed after multiple attempts. Please try again.",
        evaluations=fallback_evals
    )