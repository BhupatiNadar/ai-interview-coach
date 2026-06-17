import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

from src.Database.db import (
    get_all_interviews,
    get_interview_evaluations
)
from src.agents.LearningPlanAgent import generate_learning_plan


# ─── Helper Functions ───────────────────────────────────────────────

def _extract_topics(question):
    """Extract relevant tech topics from a question string."""
    topic_keywords = {
        "Python": ["python", "django", "flask", "fastapi"],
        "JavaScript": ["javascript", "react", "node", "angular", "vue", "typescript"],
        "Machine Learning": ["machine learning", "ml", "deep learning", "neural", "tensorflow", "pytorch"],
        "Data Science": ["data science", "pandas", "numpy", "data analysis"],
        "SQL": ["sql", "database", "query", "postgres", "mysql", "mongodb"],
        "System Design": ["system design", "architecture", "scalability", "microservices"],
        "DSA": ["algorithm", "data structure", "sorting", "searching", "tree", "graph"],
        "API Design": ["api", "rest", "graphql", "endpoint"],
        "Cloud": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes"],
        "Communication": ["communication", "explain", "describe", "tell me about"],
        "Problem Solving": ["problem solving", "approach", "solve", "debug"],
        "Backend": ["backend", "server", "microservice", "caching", "redis"],
        "Frontend": ["frontend", "ui", "ux", "css", "html"],
        "Security": ["security", "authentication", "authorization", "encryption"],
        "Testing": ["testing", "unit test", "integration test", "tdd", "pytest"],
    }

    question_lower = question.lower()
    found = []
    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if kw in question_lower:
                found.append(topic)
                break
    if not found:
        found = ["General"]
    return found


def _parse_learning_data(evaluations):
    """Parse evaluations into learning-plan metrics."""
    all_scores = []
    all_feedback = []
    skill_scores = {}
    weaknesses = {}
    strengths = {}

    for eval_record in evaluations:
        total_score = eval_record.get("total_score", 0)
        overall_feedback = eval_record.get("overall_feedback", "")
        evals = eval_record.get("evaluations", [])

        if isinstance(evals, str):
            try:
                evals = json.loads(evals)
            except (json.JSONDecodeError, TypeError):
                evals = []
        if not isinstance(evals, list):
            evals = []

        num_q = len(evals) if evals else 1
        avg_score = round(total_score / num_q, 1) if num_q > 0 else 0
        all_scores.append(avg_score)

        if overall_feedback:
            all_feedback.append(overall_feedback)

        for e in evals:
            if isinstance(e, dict):
                question = e.get("question", "")
                score = e.get("score", 0)
                topics = _extract_topics(question)
                for topic in topics:
                    if topic not in skill_scores:
                        skill_scores[topic] = []
                    skill_scores[topic].append(score)

                    if score <= 3:
                        weaknesses[topic] = weaknesses.get(topic, 0) + 1
                    elif score >= 7:
                        strengths[topic] = strengths.get(topic, 0) + 1

    return all_scores, all_feedback, skill_scores, weaknesses, strengths


def _calculate_overall_progress(all_scores, skill_scores):
    """Calculate an overall learning progress percentage."""
    if not all_scores:
        return 0

    avg = sum(all_scores) / len(all_scores)
    # Progress = avg score out of 10, as percentage
    return min(round(avg * 10), 100)


def _count_completed_topics(skill_scores):
    """Count topics where avg score >= 7 (mastered)."""
    count = 0
    for topic, scores in skill_scores.items():
        avg = sum(scores) / len(scores)
        if avg >= 7:
            count += 1
    return count


def _calculate_streak(interviews):
    """Calculate consecutive days of activity."""
    if not interviews:
        return 0

    dates = set()
    for interview in interviews:
        created_at = interview.get("created_at", "")
        try:
            dt = datetime.fromisoformat(
                created_at.replace("+00", "+00:00").replace("Z", "+00:00")
            )
            dates.add(dt.date())
        except Exception:
            continue

    if not dates:
        return 0

    sorted_dates = sorted(dates, reverse=True)
    today = datetime.now().date()

    # Check if latest activity is today or yesterday
    if sorted_dates[0] < today - timedelta(days=1):
        return 0

    streak = 1
    for i in range(len(sorted_dates) - 1):
        diff = (sorted_dates[i] - sorted_dates[i + 1]).days
        if diff == 1:
            streak += 1
        else:
            break

    return streak


# ─── Main Learning Plan Page ───────────────────────────────────────

def learning_plan():

    st.title("📚 Learning Plan")
    st.caption("Your AI-powered personalized improvement roadmap")

    # ── Fetch Data ──────────────────────────────────────────────────
    user_data = st.session_state.get("User_data", {})
    user_id = user_data.get("user_id") if user_data else None

    if not user_id:
        st.warning("Please log in to view your learning plan.")
        return

    interviews = get_all_interviews(user_id)
    evaluations = get_interview_evaluations(user_id)

    # ── Empty State ─────────────────────────────────────────────────
    if not evaluations:
        st.divider()
        st.info(
            "📋 **No Interview Data Yet**\n\n"
            "Complete your first interview to unlock your personalized "
            "AI learning plan, practice tasks, and improvement roadmap.\n\n"
            "Go to **Interviews** to get started!"
        )
        if st.button("🎤 Start an Interview",width='stretch'):
            st.session_state["User_tab"] = "Interviews"
            st.rerun()
        return

    # ── Parse Data ──────────────────────────────────────────────────
    all_scores, all_feedback, skill_scores, weaknesses_map, strengths_map = _parse_learning_data(evaluations)

    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    total_interviews = len(interviews)
    overall_progress = _calculate_overall_progress(all_scores, skill_scores)
    completed_topics = _count_completed_topics(skill_scores)
    streak = _calculate_streak(interviews)
    weak_list = [w[0] for w in sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)]
    strong_list = [s[0] for s in sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)]

    # Skill averages for the agent
    skill_avg_dict = {}
    for skill, scores in skill_scores.items():
        skill_avg_dict[skill] = round(sum(scores) / len(scores), 1)

    recent_feedback = "; ".join(all_feedback[:3]) if all_feedback else ""

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 1: Progress Overview
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📊 Progress Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(label="📈 Overall Progress", value=f"{overall_progress}%")

    with c2:
        st.metric(label="⚠️ Weak Areas", value=len(weaknesses_map))

    with c3:
        st.metric(label="✅ Strengths", value=len(strengths_map))

    with c4:
        st.metric(label="🔥 Current Streak", value=f"{streak} Days")

    with c5:
        st.metric(label="📚 Mastered Topics", value=completed_topics)

    # ── Generate AI Learning Plan ───────────────────────────────────
    # Use session state to cache the plan and avoid regenerating on every rerun
    plan_key = "learning_plan_data"
    plan_version_key = "learning_plan_version"
    current_version = f"{total_interviews}_{len(evaluations)}_{avg_score}"

    if st.button("🤖 Generate AI Learning Plan",width='stretch'):
        with st.spinner("🧠 AI is analyzing your interview data and creating your personalized plan..."):
            plan = generate_learning_plan(
                avg_score=avg_score,
                total_interviews=total_interviews,
                weak_areas=weak_list[:5],
                strong_areas=strong_list[:5],
                skill_scores=skill_avg_dict,
                recent_feedback=recent_feedback
            )
            st.session_state[plan_key] = plan
            st.session_state[plan_version_key] = current_version
            st.rerun()

    # Check if we have a cached plan
    if plan_key not in st.session_state:
        st.divider()
        st.info(
            "🤖 **Click the button above** to generate your personalized AI learning plan.\n\n"
            "The AI will analyze your interview history and create:\n"
            "- 📅 4-week study roadmap\n"
            "- ✅ Daily practice tasks\n"
            "- 📚 Recommended resources\n"
            "- 🎯 Interview readiness scores\n"
            "- 🔮 Score improvement prediction"
        )

        # Still show data-driven sections below (weaknesses, strengths)
        _render_data_sections(
            weaknesses_map, strengths_map, skill_scores,
            all_scores, total_interviews
        )
        return

    plan = st.session_state[plan_key]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: AI Generated Roadmap
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🗺️ Your Personalized Roadmap")

    if plan.roadmap:
        for week in plan.roadmap:
            with st.expander(f"📅 Week {week.week_number} — {week.title}", expanded=(week.week_number == 1)):
                for topic in week.topics:
                    # Check if this topic is in strengths (completed)
                    if topic in strong_list:
                        st.write(f"✅ ~~{topic}~~ — Already strong!")
                    else:
                        st.write(f"☐ **{topic}**")
    else:
        st.info("Roadmap will appear after AI generation.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3: Weak Areas (data-driven)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🔴 Top Weak Areas")

    if weaknesses_map:
        sorted_weak = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_weak:
            topic_avg_scores = skill_scores.get(topic, [0])
            mastery = round((sum(topic_avg_scores) / len(topic_avg_scores) / 10) * 100)

            col_name, col_bar, col_pct = st.columns([1.5, 4, 0.8])
            with col_name:
                st.write(f"🔴 **{topic}**")
            with col_bar:
                st.progress(min(mastery / 100, 1.0))
            with col_pct:
                st.write(f"**{mastery}%**")

        st.caption("Weakness Frequency:")
        freq_data = {topic: count for topic, count in sorted_weak}
        df_freq = pd.DataFrame({
            "Topic": list(freq_data.keys()),
            "Times Appeared": list(freq_data.values())
        })
        st.dataframe(df_freq, width='stretch', hide_index=True)
    else:
        st.success("No weak areas identified — excellent performance! 💪")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 4: Recommended Resources
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📖 Recommended Resources")

    if plan.resources:
        # Group resources by topic
        resources_by_topic = {}
        for res in plan.resources:
            if res.topic not in resources_by_topic:
                resources_by_topic[res.topic] = []
            resources_by_topic[res.topic].append(res)

        for topic, resources in resources_by_topic.items():
            with st.expander(f"📂 {topic}", expanded=True):
                for res in resources:
                    icon = {"Book": "📚", "Video": "🎥", "Article": "📄", "Course": "🎓"}.get(res.type, "📌")
                    st.write(f"{icon} **{res.title}** ({res.type})")
                    st.caption(f"   {res.description}")
    else:
        st.info("Resources will be recommended after AI plan generation.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 5: Practice Tasks
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("✅ Today's Practice Tasks")

    if plan.practice_tasks:
        for i, task in enumerate(plan.practice_tasks):
            difficulty_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(task.difficulty, "🟡")

            # Use checkboxes for interactive tracking
            checked = st.checkbox(
                f"{task.task}",
                key=f"task_{i}",
                help=f"Category: {task.category} | Difficulty: {task.difficulty}"
            )
            if checked:
                st.caption(f"   ✅ Completed — {task.category} ({difficulty_icon} {task.difficulty})")
            else:
                st.caption(f"   📂 {task.category} | {difficulty_icon} {task.difficulty}")
    else:
        st.info("Practice tasks will appear after AI plan generation.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 6: Weekly Challenge
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🏆 Weekly Goal")

    weekly_target = 5
    # Count interviews this week
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    interviews_this_week = 0

    for interview in interviews:
        created_at = interview.get("created_at", "")
        try:
            dt = datetime.fromisoformat(
                created_at.replace("+00", "+00:00").replace("Z", "+00:00")
            )
            if dt.date() >= start_of_week.date():
                interviews_this_week += 1
        except Exception:
            continue

    progress_pct = min(interviews_this_week / weekly_target, 1.0)

    col_goal1, col_goal2 = st.columns([3, 1])
    with col_goal1:
        st.write("**Interviews Completed This Week**")
        st.progress(progress_pct)
    with col_goal2:
        st.metric(label="Progress", value=f"{interviews_this_week} / {weekly_target}")

    if interviews_this_week >= weekly_target:
        st.success("🎉 **Weekly goal achieved!** You completed all 5 interviews this week!")
    elif interviews_this_week > 0:
        remaining = weekly_target - interviews_this_week
        st.info(f"💪 Keep going! **{remaining} more interview(s)** to reach your weekly goal.")
    else:
        st.warning("🎯 Start your first interview this week to begin your weekly challenge!")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 7: Strength Tracker
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🟢 Your Strong Areas")

    if strengths_map:
        sorted_strengths = sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_strengths[:6]:
            topic_avg = skill_scores.get(topic, [0])
            avg = round(sum(topic_avg) / len(topic_avg), 1)
            st.success(f"✓ **{topic}** — Average score: **{avg}/10** (high in {count} question(s))")
    else:
        st.info("Complete more interviews to identify your strong areas 🌟")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 8: Improvement Prediction (WOW Feature)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🔮 AI Improvement Prediction")

    with st.container(border=True):
        col_curr, col_pred, col_conf = st.columns(3)

        with col_curr:
            st.metric(label="📊 Current Score", value=f"{avg_score}/10")

        with col_pred:
            st.metric(
                label="🎯 Predicted (30 Days)",
                value=f"{plan.predicted_score_30_days}/10",
                delta=f"+{round(plan.predicted_score_30_days - avg_score, 1)}" if plan.predicted_score_30_days > avg_score else "0"
            )

        with col_conf:
            st.metric(label="🔒 Confidence", value=f"{plan.prediction_confidence}%")

        st.caption(f"💡 {plan.prediction_reasoning}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 9: Interview Readiness Score
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🏢 Interview Readiness Score")

    if plan.readiness_scores:
        cols = st.columns(len(plan.readiness_scores))
        for i, readiness in enumerate(plan.readiness_scores):
            with cols[i]:
                company_icon = {"FAANG": "🏢", "Mid-size Companies": "🏬", "Startups": "🚀"}.get(
                    readiness.company_type, "🏢"
                )
                st.write(f"**{company_icon} {readiness.company_type}**")
                st.progress(min(readiness.score / 100, 1.0))
                st.write(f"**{readiness.score}%** Ready")
                st.caption(readiness.reason)
    else:
        st.info("Readiness scores will appear after AI plan generation.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 10: Next Recommended Interview
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🎤 Recommended Next Interview")

    with st.container(border=True):
        col_info, col_action = st.columns([3, 1])

        with col_info:
            st.write(f"**📝 Type:** {plan.next_interview_type}")
            st.write(f"**🎯 Focus:** {plan.next_interview_focus}")
            st.write(f"**⏱️ Estimated Time:** 20 Minutes")
            st.caption(f"💡 {plan.next_interview_reason}")

        with col_action:
            if st.button("🚀 Start Interview", width='stretch', key="start_recommended"):
                st.session_state["User_tab"] = "Interviews"
                st.rerun()

    # ── Overall AI Advice ───────────────────────────────────────────
    if plan.overall_advice:
        st.divider()
        st.subheader("💡 AI Coach Advice")
        st.info(f"🤖 {plan.overall_advice}")


# ─── Data-only sections (shown before AI plan is generated) ────────

def _render_data_sections(weaknesses_map, strengths_map, skill_scores,
                          all_scores, total_interviews):
    """Render sections that only need interview data, not the AI plan."""

    # Weak Areas
    st.divider()
    st.subheader("🔴 Top Weak Areas")

    if weaknesses_map:
        sorted_weak = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_weak:
            topic_avg_scores = skill_scores.get(topic, [0])
            mastery = round((sum(topic_avg_scores) / len(topic_avg_scores) / 10) * 100)

            col_name, col_bar, col_pct = st.columns([1.5, 4, 0.8])
            with col_name:
                st.write(f"🔴 **{topic}**")
            with col_bar:
                st.progress(min(mastery / 100, 1.0))
            with col_pct:
                st.write(f"**{mastery}%**")
    else:
        st.success("No weak areas identified 💪")

    # Strengths
    st.divider()
    st.subheader("🟢 Your Strong Areas")

    if strengths_map:
        sorted_strengths = sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_strengths[:6]:
            topic_avg = skill_scores.get(topic, [0])
            avg = round(sum(topic_avg) / len(topic_avg), 1)
            st.success(f"✓ **{topic}** — Average: **{avg}/10** (high in {count} question(s))")
    else:
        st.info("Complete more interviews to identify your strengths 🌟")