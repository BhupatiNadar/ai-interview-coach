import streamlit as st
import pandas as pd
import json
from datetime import datetime

from src.Database.db import (
    get_all_interviews,
    get_interview_evaluations,
    get_recent_interviews,
    get_latest_resume
)


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


def _parse_dashboard_data(evaluations):
    """Parse evaluations into dashboard-friendly metrics."""
    all_scores = []
    skill_scores = {}
    weaknesses = {}
    strengths = {}

    for eval_record in evaluations:
        total_score = eval_record.get("total_score", 0)
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

    return all_scores, skill_scores, weaknesses, strengths


# ─── Main Dashboard Page ───────────────────────────────────────────

def dashboard():

    user_data = st.session_state.get("User_data", {})
    user_name = user_data.get("user_name", "User") if user_data else "User"
    user_id = user_data.get("user_id") if user_data else None

    st.header(f"Welcome back, {user_name} 👋")
    st.caption("Here's your progress overview for today")

    if not user_id:
        st.warning("Please log in to view your dashboard.")
        return

    # ── Fetch Data ──────────────────────────────────────────────────
    interviews = get_all_interviews(user_id)
    evaluations = get_interview_evaluations(user_id)
    recent_interviews = get_recent_interviews(user_id, limit=5)

    all_scores, skill_scores, weaknesses_map, strengths_map = _parse_dashboard_data(evaluations)

    total_interviews = len(interviews)
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    weak_area_count = len(weaknesses_map)

    # Calculate improvement
    if len(all_scores) >= 2:
        first_score = all_scores[-1]
        latest_score = all_scores[0]
        if first_score > 0:
            improvement_pct = round(((latest_score - first_score) / first_score) * 100)
        else:
            improvement_pct = 100 if latest_score > 0 else 0
    else:
        improvement_pct = 0

    improvement_str = f"+{improvement_pct}%" if improvement_pct >= 0 else f"{improvement_pct}%"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 1: Top Stats Cards
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🎯 Total Interviews",
            value=total_interviews,
            help="Total number of interview sessions completed"
        )

    with col2:
        st.metric(
            label="📈 Average Score",
            value=f"{avg_score}/10",
            help="Average score across all interviews"
        )

    with col3:
        st.metric(
            label="🚀 Skill Improvement",
            value=improvement_str,
            delta=improvement_str,
            help="Score improvement from first to latest interview"
        )

    with col4:
        st.metric(
            label="⚠️ Weak Areas",
            value=weak_area_count,
            help="Number of skill areas needing improvement"
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: Performance Overview + Top Skills (side by side)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()

    col_chart, col_skills = st.columns([3, 1])

    with col_chart:
        st.subheader("📉 Performance Overview")

        if all_scores:
            scores_chronological = list(reversed(all_scores))
            chart_data = pd.DataFrame({
                "Score": scores_chronological
            }, index=[f"I{i+1}" for i in range(len(scores_chronological))])

            st.line_chart(chart_data, color="#8b5cf6")
        else:
            st.info("Complete your first interview to see your performance chart.")

    with col_skills:
        st.subheader("🏅 Top Skills")

        if skill_scores:
            skill_averages = {}
            for skill, scores in skill_scores.items():
                skill_averages[skill] = round(sum(scores) / len(scores), 1)

            sorted_skills = sorted(skill_averages.items(), key=lambda x: x[1], reverse=True)

            for skill, avg in sorted_skills[:5]:
                st.progress(min(avg / 10, 1.0), text=f"**{skill}** — {avg}/10")
        else:
            st.info("Skills will appear after interviews.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3: Recent Interviews + Quick Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()

    col_recent, col_actions = st.columns([3, 1])

    with col_recent:
        st.subheader("📋 Recent Interviews")

        if evaluations:
            recent_rows = []
            for eval_rec in evaluations[:5]:
                interview_info = eval_rec.get("interview_session", {})
                created_at = eval_rec.get("created_at", "")
                interview_type = interview_info.get("interview_type", "General") if interview_info else "General"
                total = eval_rec.get("total_score", 0)
                evals = eval_rec.get("evaluations", [])

                if isinstance(evals, str):
                    try:
                        evals = json.loads(evals)
                    except (json.JSONDecodeError, TypeError):
                        evals = []
                if not isinstance(evals, list):
                    evals = []

                num_q = len(evals) if evals else 1
                avg = round(total / num_q, 1) if num_q > 0 else 0

                try:
                    dt = datetime.fromisoformat(
                        created_at.replace("+00", "+00:00").replace("Z", "+00:00")
                    )
                    date_str = dt.strftime("%d %b %Y")
                except Exception:
                    date_str = created_at[:10] if created_at else "—"

                recent_rows.append({
                    "📅 Date": date_str,
                    "📝 Type": interview_type,
                    "⭐ Score": f"{avg}/10",
                    "❓ Questions": num_q
                })

            df_recent = pd.DataFrame(recent_rows)
            st.dataframe(df_recent,width='stretch', hide_index=True)

            if st.button("📄 View All Reports",width='stretch'):
                st.session_state["User_tab"] = "Reports"
                st.rerun()
        else:
            st.info(
                "No interviews yet. Start your first interview to see results here!"
            )

    with col_actions:
        st.subheader("⚡ Quick Actions")

        if st.button("🎤 Start Interview", width='stretch'):
            st.session_state["User_tab"] = "Interviews"
            st.rerun()

        if st.button("📃 Upload Resume",width='stretch'):
            st.session_state["User_tab"] = "Resume"
            st.rerun()

        if st.button("📊 View Reports",width='stretch'):
            st.session_state["User_tab"] = "Reports"
            st.rerun()

        if st.button("📚 Learning Plan",width='stretch'):
            st.session_state["User_tab"] = "Learning Plan"
            st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 4: Weak Areas + Strengths Summary
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()

    col_weak, col_strong = st.columns(2)

    with col_weak:
        st.subheader("⚠️ Weak Areas")
        top_weaknesses = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_weaknesses:
            for topic, count in top_weaknesses:
                st.warning(f"⚡ **{topic}** — low score in {count} question(s)")
        else:
            st.success("No weak areas found — great job! 💪")

    with col_strong:
        st.subheader("✅ Strengths")
        top_strengths = sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_strengths:
            for topic, count in top_strengths:
                st.success(f"✓ **{topic}** — high score in {count} question(s)")
        else:
            st.info("Complete more interviews to discover your strengths 🌟")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 5: Resume Status
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📄 Resume Status")

    resume_data = get_latest_resume()
    if resume_data:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="📎 File Name", value=resume_data.get("file_name", "—"))
        with col_r2:
            uploaded_at = resume_data.get("uploaded_at", "")
            try:
                dt = datetime.fromisoformat(
                    uploaded_at.replace("+00", "+00:00").replace("Z", "+00:00")
                )
                upload_str = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                upload_str = uploaded_at[:10] if uploaded_at else "—"
            st.metric(label="📅 Uploaded On", value=upload_str)
        st.success("✅ Resume is uploaded and ready for interview preparation.")
    else:
        st.warning(
            "📌 **No resume uploaded yet.** Upload your resume to get "
            "personalized interview questions tailored to your skills."
        )
        if st.button("📃 Go to Resume Upload",width='stretch'):
            st.session_state["User_tab"] = "Resume"
            st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 6: Today's Quick Tip
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("💡 Quick Tip")

    # Generate contextual tip based on user's data
    if not evaluations:
        tip = (
            "🎯 **Getting Started:** Upload your resume first, then start a "
            "Technical Interview. The AI will generate questions based on your "
            "skills and experience!"
        )
    elif weak_area_count > 0:
        top_weak = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[0][0]
        tip = (
            f"📚 **Focus Area:** Your weakest skill is **{top_weak}**. "
            f"Practice questions related to this topic to boost your score. "
            f"Try starting another interview focusing on this area!"
        )
    elif avg_score >= 7:
        tip = (
            "🏆 **Excellent Performance!** You're scoring above 7/10 on average. "
            "Challenge yourself with harder topics or try Behavioral/Company-Specific "
            "interviews to round out your preparation."
        )
    else:
        tip = (
            "📈 **Keep Practicing!** Consistent practice leads to improvement. "
            "Try to do at least one interview session daily. Review your weak areas "
            "in the Reports section."
        )

    st.info(tip)