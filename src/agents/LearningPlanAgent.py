import streamlit as st
import json
import logging

from typing import List, Optional
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate


# ─── Pydantic Models ───────────────────────────────────────────────

class WeekPlan(BaseModel):
    week_number: int = 0
    title: str = ""
    topics: List[str] = []


class PracticeTask(BaseModel):
    task: str = ""
    category: str = ""
    difficulty: str = "Medium"


class Resource(BaseModel):
    topic: str = ""
    title: str = ""
    type: str = ""  # Book, Video, Article, Course
    description: str = ""


class ReadinessScore(BaseModel):
    company_type: str = ""
    score: int = 0
    reason: str = ""


class LearningPlanOutput(BaseModel):
    roadmap: List[WeekPlan] = []
    practice_tasks: List[PracticeTask] = []
    resources: List[Resource] = []
    predicted_score_30_days: float = 0.0
    prediction_confidence: int = 0
    prediction_reasoning: str = ""
    readiness_scores: List[ReadinessScore] = []
    next_interview_type: str = ""
    next_interview_focus: str = ""
    next_interview_reason: str = ""
    overall_advice: str = ""


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


# ─── Prompt ────────────────────────────────────────────────────────

LEARNING_PLAN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI career coach and interview preparation advisor.

Based on the candidate's interview performance data, generate a comprehensive personalized learning plan.

INPUT DATA:
- Average Score: {{avg_score}}/10
- Total Interviews: {{total_interviews}}
- Weak areas (topics with low scores): {{weak_areas}}
- Strong areas (topics with high scores): {{strong_areas}}
- Skill scores (topic: average score): {{skill_scores}}
- Recent feedback: {{recent_feedback}}

GENERATE the following in valid JSON:

1. "roadmap": A 4-week study plan. Each week has:
   - "week_number": 1-4
   - "title": short title like "Foundations" or "Advanced Topics"
   - "topics": list of 2-3 specific topics to study that week (prioritize weak areas)

2. "practice_tasks": 5 specific, actionable practice tasks for today. Each has:
   - "task": description of what to do
   - "category": which skill area
   - "difficulty": "Easy", "Medium", or "Hard"

3. "resources": 6 recommended learning resources. Each has:
   - "topic": which topic it covers
   - "title": name of the resource
   - "type": "Book", "Video", "Article", or "Course"
   - "description": 1-sentence description

4. "predicted_score_30_days": estimated average score after 30 days of following this plan (float)
5. "prediction_confidence": confidence percentage 0-100 (integer)
6. "prediction_reasoning": short explanation for the prediction

7. "readiness_scores": Interview readiness for 3 company types. Each has:
   - "company_type": e.g. "FAANG", "Mid-size Companies", "Startups"
   - "score": readiness percentage 0-100
   - "reason": short explanation

8. "next_interview_type": recommended next interview type ("Technical", "Behavioral", etc.)
9. "next_interview_focus": specific topic to focus on
10. "next_interview_reason": why this is recommended

11. "overall_advice": 2-3 sentence personalized advice

Return ONLY valid JSON. No other text.
"""),
    ("human", """Here is my interview data:

Average Score: {avg_score}/10
Total Interviews: {total_interviews}
Weak Areas: {weak_areas}
Strong Areas: {strong_areas}
Skill Scores: {skill_scores}
Recent Feedback: {recent_feedback}

Generate my personalized learning plan as JSON.""")
])


# ─── Main Function ─────────────────────────────────────────────────

def generate_learning_plan(
    avg_score,
    total_interviews,
    weak_areas,
    strong_areas,
    skill_scores,
    recent_feedback
) -> LearningPlanOutput:
    """Generate a personalized learning plan using the AI agent."""

    llm = _get_llm()
    structured_llm = llm.with_structured_output(
        LearningPlanOutput,
        method="json_mode"
    )
    chain = LEARNING_PLAN_PROMPT | structured_llm

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = chain.invoke({
                "avg_score": str(avg_score),
                "total_interviews": str(total_interviews),
                "weak_areas": str(weak_areas),
                "strong_areas": str(strong_areas),
                "skill_scores": str(skill_scores),
                "recent_feedback": str(recent_feedback[:500] if recent_feedback else "No feedback yet")
            })

            # Validate we got meaningful data
            if result.roadmap or result.practice_tasks:
                return result

            logger.warning(f"Attempt {attempt}/{MAX_RETRIES}: Empty learning plan, retrying...")
            if attempt == MAX_RETRIES:
                break
            continue

        except (OutputParserException, Exception) as e:
            logger.warning(f"Learning plan attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                break

    # Fallback: build a default plan so the page doesn't crash
    logger.error("All learning plan attempts failed. Returning fallback.")
    return _build_fallback_plan(weak_areas, strong_areas, avg_score)


def _build_fallback_plan(weak_areas, strong_areas, avg_score):
    """Build a sensible fallback plan when AI generation fails."""

    weak_list = weak_areas if isinstance(weak_areas, list) else []
    strong_list = strong_areas if isinstance(strong_areas, list) else []

    # Build roadmap from weak areas
    roadmap = []
    all_topics = weak_list + ["Practice & Review"]
    for i in range(4):
        start = i * 2
        topics = all_topics[start:start + 2] if start < len(all_topics) else ["General Practice", "Mock Interviews"]
        roadmap.append(WeekPlan(
            week_number=i + 1,
            title=f"Week {i + 1} Focus",
            topics=topics if topics else ["Review & Practice"]
        ))

    # Build practice tasks
    tasks = []
    for w in weak_list[:3]:
        tasks.append(PracticeTask(task=f"Study and practice {w} concepts", category=w, difficulty="Medium"))
    tasks.append(PracticeTask(task="Complete a mock interview session", category="General", difficulty="Medium"))
    tasks.append(PracticeTask(task="Review feedback from previous interviews", category="General", difficulty="Easy"))

    # Build resources
    resources = []
    for w in weak_list[:3]:
        resources.append(Resource(topic=w, title=f"{w} - Complete Guide", type="Article", description=f"Comprehensive guide covering {w} fundamentals."))
        resources.append(Resource(topic=w, title=f"{w} Tutorial", type="Video", description=f"Video tutorial on {w} concepts and practice."))

    # Predicted score
    predicted = min(avg_score + 1.5, 10.0) if avg_score > 0 else 5.0

    # Readiness scores
    readiness = [
        ReadinessScore(company_type="FAANG", score=max(int(avg_score * 8), 10), reason="Based on current skill levels."),
        ReadinessScore(company_type="Mid-size Companies", score=max(int(avg_score * 9), 20), reason="Good foundation, needs refinement."),
        ReadinessScore(company_type="Startups", score=max(int(avg_score * 10), 30), reason="Practical skills are valued."),
    ]

    focus = weak_list[0] if weak_list else "General"

    return LearningPlanOutput(
        roadmap=roadmap,
        practice_tasks=tasks[:5],
        resources=resources[:6],
        predicted_score_30_days=round(predicted, 1),
        prediction_confidence=60,
        prediction_reasoning="Based on your current performance and typical improvement rates.",
        readiness_scores=readiness,
        next_interview_type="Technical",
        next_interview_focus=focus,
        next_interview_reason=f"Focus on {focus} to address your weakest area.",
        overall_advice="Keep practicing consistently. Focus on your weak areas first, then strengthen your existing skills."
    )
