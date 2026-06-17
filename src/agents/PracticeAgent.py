import streamlit as st
import json
import logging

from typing import List, Optional
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate


# ─── Pydantic Models ───────────────────────────────────────────────

class PracticeQuestion(BaseModel):
    question: str = ""
    category: str = ""
    difficulty: str = "Medium"
    hint: str = ""


class TechnicalFeedback(BaseModel):
    score: int = 0
    correct_points: List[str] = []
    missing_points: List[str] = []
    suggestions: str = ""


class BehavioralFeedback(BaseModel):
    score: int = 0
    situation: bool = False
    task: bool = False
    action: bool = False
    result: bool = False
    feedback: str = ""
    suggestions: str = ""


class SystemDesignFeedback(BaseModel):
    score: int = 0
    covered: List[str] = []
    missing: List[str] = []
    feedback: str = ""


class CodingFeedback(BaseModel):
    correctness: int = 0
    time_complexity: str = ""
    space_complexity: str = ""
    suggestions: List[str] = []
    feedback: str = ""


class DailyChallenge(BaseModel):
    question: str = ""
    category: str = ""
    difficulty: str = "Medium"
    xp_reward: int = 10


class AISuggestion(BaseModel):
    struggle_areas: List[str] = []
    recommended_practice: List[str] = []
    advice: str = ""


# ─── LLM Setup ─────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def _get_llm():
    """Lazily create LLM to avoid accessing secrets at import time."""
    return ChatOpenAI(
        model="meta-llama/Llama-3.1-8B-Instruct",
        api_key=st.secrets["HF_TOKEN"],
        base_url="https://router.huggingface.co/v1"
    )


# ─── Question Generation ──────────────────────────────────────────

QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical interviewer generating practice questions.

Generate exactly ONE practice question for the given category and difficulty.

Return ONLY valid JSON with these keys:
- "question": the practice question text
- "category": the category name
- "difficulty": "Easy", "Medium", or "Hard"
- "hint": a brief hint to help the user (1 sentence)

No other text outside JSON.
"""),
    ("human", """Category: {category}
Difficulty: {difficulty}
Weak areas to focus on: {weak_areas}

Generate one practice question as JSON.""")
])


def generate_practice_question(category, difficulty="Medium", weak_areas="") -> PracticeQuestion:
    """Generate a single practice question for a category."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(PracticeQuestion, method="json_mode")
    chain = QUESTION_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({
                "category": category,
                "difficulty": difficulty,
                "weak_areas": weak_areas or "None specified"
            })
            if result.question:
                return result
        except Exception as e:
            logger.warning(f"Question generation attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return PracticeQuestion(
        question=f"Explain the key concepts of {category} and how you would apply them in a real project.",
        category=category,
        difficulty=difficulty,
        hint="Think about fundamentals first, then practical applications."
    )


# ─── Technical Answer Evaluation ──────────────────────────────────

TECHNICAL_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical interviewer evaluating a practice answer.

Evaluate the answer to the given question. Be fair and constructive.

Return ONLY valid JSON with these keys:
- "score": integer 0-10
- "correct_points": list of things the user got right
- "missing_points": list of things the user missed
- "suggestions": brief suggestion for improvement (string)

No other text outside JSON.
"""),
    ("human", """Question: {question}
Answer: {answer}

Evaluate this answer as JSON.""")
])


def evaluate_technical_answer(question, answer) -> TechnicalFeedback:
    """Evaluate a technical practice answer."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(TechnicalFeedback, method="json_mode")
    chain = TECHNICAL_EVAL_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({"question": question, "answer": answer})
            return result
        except Exception as e:
            logger.warning(f"Technical eval attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return TechnicalFeedback(
        score=5, correct_points=["Answer provided"],
        missing_points=["Could not evaluate fully"],
        suggestions="Try providing more detail in your answer."
    )


# ─── Behavioral Answer Evaluation ────────────────────────────────

BEHAVIORAL_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an HR interviewer evaluating a behavioral answer using the STAR method.

Check if the answer includes:
- Situation: Did they describe the context?
- Task: Did they explain what they needed to do?
- Action: Did they describe what they specifically did?
- Result: Did they share the outcome?

Return ONLY valid JSON with these keys:
- "score": integer 0-10
- "situation": true/false - did they include situation
- "task": true/false - did they include task
- "action": true/false - did they include action
- "result": true/false - did they include result
- "feedback": brief feedback on the answer (string)
- "suggestions": how to improve (string)

No other text outside JSON.
"""),
    ("human", """Question: {question}
Answer: {answer}

Evaluate using STAR format as JSON.""")
])


def evaluate_behavioral_answer(question, answer) -> BehavioralFeedback:
    """Evaluate a behavioral answer using STAR format."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(BehavioralFeedback, method="json_mode")
    chain = BEHAVIORAL_EVAL_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({"question": question, "answer": answer})
            return result
        except Exception as e:
            logger.warning(f"Behavioral eval attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return BehavioralFeedback(
        score=5, situation=False, task=False, action=False, result=False,
        feedback="Could not fully evaluate.", suggestions="Use the STAR format."
    )


# ─── System Design Answer Evaluation ─────────────────────────────

SYSDESIGN_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a system design interviewer evaluating an answer.

Check which design components the candidate covered and which are missing.

Return ONLY valid JSON with these keys:
- "score": integer 0-10
- "covered": list of design components mentioned (e.g. "Database", "Caching", "Load Balancer")
- "missing": list of important components they missed
- "feedback": brief overall feedback (string)

No other text outside JSON.
"""),
    ("human", """Question: {question}
Answer: {answer}

Evaluate system design answer as JSON.""")
])


def evaluate_system_design_answer(question, answer) -> SystemDesignFeedback:
    """Evaluate a system design answer."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(SystemDesignFeedback, method="json_mode")
    chain = SYSDESIGN_EVAL_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({"question": question, "answer": answer})
            return result
        except Exception as e:
            logger.warning(f"SysDesign eval attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return SystemDesignFeedback(
        score=5, covered=["Some concepts mentioned"],
        missing=["Could not evaluate fully"], feedback="Try to be more specific."
    )


# ─── Coding Answer Evaluation ────────────────────────────────────

CODING_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a coding interviewer evaluating a code solution.

Evaluate the code for correctness, time complexity, and space complexity.

Return ONLY valid JSON with these keys:
- "correctness": integer 0-10 (how correct is the solution)
- "time_complexity": string (e.g. "O(n)", "O(n log n)")
- "space_complexity": string (e.g. "O(1)", "O(n)")
- "suggestions": list of improvement suggestions (strings)
- "feedback": brief overall feedback (string)

No other text outside JSON.
"""),
    ("human", """Question: {question}
Code Solution:
```
{answer}
```

Evaluate this code as JSON.""")
])


def evaluate_coding_answer(question, answer) -> CodingFeedback:
    """Evaluate a coding solution."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(CodingFeedback, method="json_mode")
    chain = CODING_EVAL_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({"question": question, "answer": answer})
            return result
        except Exception as e:
            logger.warning(f"Coding eval attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return CodingFeedback(
        correctness=5, time_complexity="Unknown", space_complexity="Unknown",
        suggestions=["Could not evaluate fully"], feedback="Try again."
    )


# ─── Daily Challenge Generation ──────────────────────────────────

DAILY_CHALLENGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Generate a daily practice challenge question.

The question should be interesting and educational. Base it on the user's weak areas if provided.

Return ONLY valid JSON with these keys:
- "question": the challenge question
- "category": topic category
- "difficulty": "Easy", "Medium", or "Hard"
- "xp_reward": integer 5-20 based on difficulty

No other text outside JSON.
"""),
    ("human", """Weak areas: {weak_areas}
Today's date: {today}

Generate a daily challenge as JSON.""")
])


def generate_daily_challenge(weak_areas="", today="") -> DailyChallenge:
    """Generate a daily challenge question."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(DailyChallenge, method="json_mode")
    chain = DAILY_CHALLENGE_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({
                "weak_areas": weak_areas or "General topics",
                "today": today
            })
            if result.question:
                return result
        except Exception as e:
            logger.warning(f"Daily challenge attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    return DailyChallenge(
        question="Explain the differences between SQL and NoSQL databases with examples.",
        category="Database", difficulty="Medium", xp_reward=10
    )


# ─── AI Suggestions Generation ───────────────────────────────────

SUGGESTIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI career coach analyzing practice performance.

Based on the user's weak areas and skill scores, provide actionable suggestions.

Return ONLY valid JSON with these keys:
- "struggle_areas": list of top 3 areas they struggle with
- "recommended_practice": list of 3-5 specific practice activities
- "advice": 2-3 sentence personalized advice

No other text outside JSON.
"""),
    ("human", """Weak areas: {weak_areas}
Skill scores: {skill_scores}
Average score: {avg_score}/10

Generate AI suggestions as JSON.""")
])


def generate_ai_suggestions(weak_areas, skill_scores, avg_score) -> AISuggestion:
    """Generate AI-powered practice suggestions."""
    llm = _get_llm()
    structured_llm = llm.with_structured_output(AISuggestion, method="json_mode")
    chain = SUGGESTIONS_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({
                "weak_areas": str(weak_areas),
                "skill_scores": str(skill_scores),
                "avg_score": str(avg_score)
            })
            if result.struggle_areas or result.recommended_practice:
                return result
        except Exception as e:
            logger.warning(f"AI suggestions attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    weak_list = weak_areas if isinstance(weak_areas, list) else []
    return AISuggestion(
        struggle_areas=weak_list[:3] or ["General skills"],
        recommended_practice=[f"Practice {w}" for w in weak_list[:3]] or ["Complete a mock interview"],
        advice="Keep practicing consistently. Focus on your weak areas to see the fastest improvement."
    )
