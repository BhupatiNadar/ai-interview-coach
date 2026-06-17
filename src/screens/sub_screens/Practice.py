import streamlit as st
import pandas as pd
import json
from datetime import datetime

from src.Database.db import (
    get_all_interviews,
    get_interview_evaluations
)
from src.agents.PracticeAgent import (
    generate_practice_question,
    evaluate_technical_answer,
    evaluate_behavioral_answer,
    evaluate_system_design_answer,
    evaluate_coding_answer,
    generate_daily_challenge,
    generate_ai_suggestions
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


def _parse_practice_data(evaluations):
    """Parse evaluations into practice-friendly metrics."""
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


def _init_practice_state():
    """Initialize all practice-related session state keys."""
    defaults = {
        "practice_mode": None,
        "practice_question": None,
        "practice_feedback": None,
        "practice_history": [],
        "daily_challenge": None,
        "daily_challenge_date": None,
        "ai_suggestions": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ─── Main Practice Page ────────────────────────────────────────────

def practice():

    st.title("🎯 Practice Center")
    st.caption("Improve one skill at a time — your personalized training ground")

    _init_practice_state()

    # ── Fetch Data ──────────────────────────────────────────────────
    user_data = st.session_state.get("User_data", {})
    user_id = user_data.get("user_id") if user_data else None

    if not user_id:
        st.warning("Please log in to access the Practice Center.")
        return

    evaluations = get_interview_evaluations(user_id)
    all_scores, skill_scores, weaknesses_map, strengths_map = _parse_practice_data(evaluations)

    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    weak_list = [w[0] for w in sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)]
    skill_avg_dict = {}
    for skill, scores in skill_scores.items():
        skill_avg_dict[skill] = round(sum(scores) / len(scores), 1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 1: Quick Practice Cards — Choose Practice Mode
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🎮 Choose Practice Mode")

    modes = [
        ("💻 Technical", "Technical"),
        ("🗣️ Behavioral", "Behavioral"),
        ("🏗️ System Design", "System Design"),
        ("💬 Communication", "Communication"),
        ("🧮 Aptitude", "Aptitude"),
        ("👔 HR Round", "HR Round"),
        ("🧑‍💻 Coding", "Coding"),
        ("📝 General", "General"),
    ]

    # 2 rows of 4 buttons
    row1 = st.columns(4)
    row2 = st.columns(4)

    for i, (label, mode) in enumerate(modes[:4]):
        with row1[i]:
            if st.button(label,width='stretch', key=f"mode_{mode}"):
                st.session_state["practice_mode"] = mode
                st.session_state["practice_question"] = None
                st.session_state["practice_feedback"] = None
                st.rerun()

    for i, (label, mode) in enumerate(modes[4:]):
        with row2[i]:
            if st.button(label,width='stretch', key=f"mode_{mode}"):
                st.session_state["practice_mode"] = mode
                st.session_state["practice_question"] = None
                st.session_state["practice_feedback"] = None
                st.rerun()

    current_mode = st.session_state["practice_mode"]

    if current_mode:
        st.info(f"🎯 Current Mode: **{current_mode}**")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: Weak Area Practice — Recommended For You
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🎯 Recommended For You")

    if weaknesses_map:
        sorted_weak = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:4]
        cols = st.columns(len(sorted_weak))

        for i, (topic, count) in enumerate(sorted_weak):
            with cols[i]:
                topic_avg = skill_scores.get(topic, [0])
                mastery = round((sum(topic_avg) / len(topic_avg) / 10) * 100)

                st.write(f"**🔴 {topic}**")
                st.progress(min(mastery / 100, 1.0))
                st.caption(f"Progress: {mastery}%")

                if st.button("Practice Now", key=f"weak_practice_{topic}", width='stretch'):
                    st.session_state["practice_mode"] = topic
                    st.session_state["practice_question"] = None
                    st.session_state["practice_feedback"] = None
                    st.rerun()
    else:
        st.success("No weak areas detected! Choose any practice mode above to keep improving. 💪")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3-6: Practice Question Area (depends on mode)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if current_mode:
        st.divider()
        _render_practice_area(current_mode, weak_list)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 8: Daily Challenge
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    _render_daily_challenge(weak_list)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 9: Practice History
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    _render_practice_history()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 10: AI Suggestions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    _render_ai_suggestions(weak_list, skill_avg_dict, avg_score)


# ─── Practice Area Renderer ───────────────────────────────────────

def _render_practice_area(mode, weak_list):
    """Render the interactive practice question + feedback area."""

    # Map modes to evaluation categories
    mode_mapping = {
        "Technical": "technical",
        "Behavioral": "behavioral",
        "System Design": "system_design",
        "Communication": "behavioral",    # Use behavioral STAR eval
        "Aptitude": "technical",
        "HR Round": "behavioral",
        "Coding": "coding",
        "General": "technical",
    }

    eval_type = mode_mapping.get(mode, "technical")

    # Mode-specific headers
    mode_icons = {
        "Technical": "💻", "Behavioral": "🗣️", "System Design": "🏗️",
        "Communication": "💬", "Aptitude": "🧮", "HR Round": "👔",
        "Coding": "🧑‍💻", "General": "📝"
    }
    icon = mode_icons.get(mode, "📝")
    st.subheader(f"{icon} {mode} Practice")

    # Difficulty selector
    col_diff, col_gen = st.columns([1, 2])
    with col_diff:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
            key="practice_difficulty"
        )

    with col_gen:
        st.write("")  # spacer
        st.write("")  # spacer
        if st.button("🎲 Generate Question",width='stretch', key="gen_question"):
            with st.spinner(f"🤖 Generating {mode} question..."):
                question = generate_practice_question(
                    category=mode,
                    difficulty=difficulty,
                    weak_areas=", ".join(weak_list[:3]) if weak_list else ""
                )
                st.session_state["practice_question"] = question
                st.session_state["practice_feedback"] = None
                st.rerun()

    # ── Display Question ────────────────────────────────────────────
    question_obj = st.session_state.get("practice_question")

    if not question_obj:
        st.info(f"Click **Generate Question** to get a {mode} practice question.")
        return

    with st.container(border=True):
        st.write(f"**📝 Question** ({question_obj.difficulty})")
        st.write(question_obj.question)

        with st.expander("💡 Hint"):
            st.write(question_obj.hint)

    # ── Answer Input ────────────────────────────────────────────────
    if eval_type == "coding":
        st.write("**💻 Your Code:**")
        answer = st.text_area(
            "Write your code here",
            height=250,
            key="practice_answer_input",
            placeholder="def solution():\n    # Write your code here\n    pass"
        )
    else:
        st.write("**✍️ Your Answer:**")
        answer = st.text_area(
            "Type your answer here",
            height=200,
            key="practice_answer_input",
            placeholder="Type your detailed answer..."
        )

    # ── Submit & Evaluate ───────────────────────────────────────────
    col_submit, col_skip = st.columns(2)

    with col_submit:
        if st.button("✅ Check Answer",width='stretch', key="check_answer"):
            if not answer or answer.strip() == "":
                st.warning("Please enter your answer first.")
            else:
                with st.spinner("🤖 AI is evaluating your answer..."):
                    feedback = _evaluate_answer(
                        eval_type, question_obj.question, answer
                    )
                    st.session_state["practice_feedback"] = {
                        "type": eval_type,
                        "feedback": feedback
                    }

                    # Save to practice history
                    history_entry = {
                        "category": mode,
                        "question": question_obj.question[:60] + "...",
                        "score": _get_feedback_score(eval_type, feedback),
                        "time": datetime.now().strftime("%H:%M"),
                    }
                    if "practice_history" not in st.session_state:
                        st.session_state["practice_history"] = []
                    st.session_state["practice_history"].insert(0, history_entry)

                    st.rerun()

    with col_skip:
        if st.button("⏭️ Skip Question",width='stretch', key="skip_question"):
            st.session_state["practice_question"] = None
            st.session_state["practice_feedback"] = None
            st.rerun()

    # ── Display Feedback ────────────────────────────────────────────
    feedback_data = st.session_state.get("practice_feedback")

    if feedback_data:
        st.divider()
        _render_feedback(feedback_data["type"], feedback_data["feedback"])


def _evaluate_answer(eval_type, question, answer):
    """Route to the correct evaluation function."""
    if eval_type == "behavioral":
        return evaluate_behavioral_answer(question, answer)
    elif eval_type == "system_design":
        return evaluate_system_design_answer(question, answer)
    elif eval_type == "coding":
        return evaluate_coding_answer(question, answer)
    else:
        return evaluate_technical_answer(question, answer)


def _get_feedback_score(eval_type, feedback):
    """Extract the score from feedback regardless of type."""
    if eval_type == "coding":
        return f"{feedback.correctness}/10"
    return f"{feedback.score}/10"


# ─── Feedback Renderers ───────────────────────────────────────────

def _render_feedback(eval_type, feedback):
    """Render feedback based on evaluation type."""

    st.subheader("🤖 AI Feedback")

    if eval_type == "technical":
        _render_technical_feedback(feedback)
    elif eval_type == "behavioral":
        _render_behavioral_feedback(feedback)
    elif eval_type == "system_design":
        _render_system_design_feedback(feedback)
    elif eval_type == "coding":
        _render_coding_feedback(feedback)


def _render_technical_feedback(fb):
    """Render technical answer feedback."""
    col_score, col_details = st.columns([1, 3])

    with col_score:
        st.metric(label="⭐ Score", value=f"{fb.score}/10")

    with col_details:
        if fb.correct_points:
            st.write("**✅ Correct Points:**")
            for point in fb.correct_points:
                st.write(f"  • {point}")

        if fb.missing_points:
            st.write("**❌ Missing Points:**")
            for point in fb.missing_points:
                st.write(f"  • {point}")

    if fb.suggestions:
        st.info(f"💡 **Suggestion:** {fb.suggestions}")


def _render_behavioral_feedback(fb):
    """Render behavioral STAR format feedback."""
    col_score, col_star = st.columns([1, 3])

    with col_score:
        st.metric(label="⭐ Score", value=f"{fb.score}/10")

    with col_star:
        st.write("**STAR Format Analysis:**")

        s_icon = "✅" if fb.situation else "❌"
        t_icon = "✅" if fb.task else "❌"
        a_icon = "✅" if fb.action else "❌"
        r_icon = "✅" if fb.result else "❌"

        st.write(f"  {s_icon} **Situation** — Context described")
        st.write(f"  {t_icon} **Task** — Objective explained")
        st.write(f"  {a_icon} **Action** — Specific actions described")
        st.write(f"  {r_icon} **Result** — Outcome shared")

    if fb.feedback:
        st.write(f"**💬 Feedback:** {fb.feedback}")

    if fb.suggestions:
        st.info(f"💡 **Suggestion:** {fb.suggestions}")


def _render_system_design_feedback(fb):
    """Render system design feedback."""
    col_score, col_details = st.columns([1, 3])

    with col_score:
        st.metric(label="⭐ Score", value=f"{fb.score}/10")

    with col_details:
        if fb.covered:
            st.write("**✅ Components Covered:**")
            for item in fb.covered:
                st.write(f"  ✓ {item}")

        if fb.missing:
            st.write("**❌ Components Missing:**")
            for item in fb.missing:
                st.write(f"  ✗ {item}")

    if fb.feedback:
        st.info(f"💡 **Feedback:** {fb.feedback}")


def _render_coding_feedback(fb):
    """Render coding solution feedback."""
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(label="✅ Correctness", value=f"{fb.correctness}/10")

    with c2:
        st.metric(label="⏱️ Time Complexity", value=fb.time_complexity)

    with c3:
        st.metric(label="💾 Space Complexity", value=fb.space_complexity)

    if fb.suggestions:
        st.write("**💡 Suggestions:**")
        for s in fb.suggestions:
            st.write(f"  • {s}")

    if fb.feedback:
        st.info(f"💬 **Feedback:** {fb.feedback}")


# ─── Daily Challenge Section ──────────────────────────────────────

def _render_daily_challenge(weak_list):
    """Render the daily challenge section."""
    st.subheader("🌟 Daily Challenge")

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if we already have today's challenge
    if (st.session_state.get("daily_challenge_date") != today
            or st.session_state.get("daily_challenge") is None):

        if st.button("🎲 Get Today's Challenge",width='stretch', key="get_daily"):
            with st.spinner("🤖 Generating today's challenge..."):
                challenge = generate_daily_challenge(
                    weak_areas=", ".join(weak_list[:3]) if weak_list else "",
                    today=today
                )
                st.session_state["daily_challenge"] = challenge
                st.session_state["daily_challenge_date"] = today
                st.rerun()
    
    challenge = st.session_state.get("daily_challenge")

    if challenge:
        with st.container(border=True):
            col_info, col_reward = st.columns([3, 1])

            with col_info:
                diff_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(
                    challenge.difficulty, "🟡"
                )
                st.write(f"**📂 Category:** {challenge.category}")
                st.write(f"**{diff_icon} Difficulty:** {challenge.difficulty}")
                st.divider()
                st.write(f"**❓ {challenge.question}**")

            with col_reward:
                st.metric(label="🏆 Reward", value=f"+{challenge.xp_reward} XP")

        # Answer area for daily challenge
        daily_answer = st.text_area(
            "Your Answer",
            height=150,
            key="daily_challenge_answer",
            placeholder="Type your answer to the daily challenge..."
        )

        if st.button("✅ Submit Challenge",width='stretch', key="submit_daily"):
            if daily_answer and daily_answer.strip():
                with st.spinner("🤖 Evaluating..."):
                    fb = evaluate_technical_answer(challenge.question, daily_answer)
                    st.session_state["daily_feedback"] = fb
                    st.rerun()
            else:
                st.warning("Please enter your answer first.")

        # Show daily challenge feedback
        daily_fb = st.session_state.get("daily_feedback")
        if daily_fb:
            st.divider()
            col_s, col_d = st.columns([1, 3])
            with col_s:
                st.metric(label="⭐ Score", value=f"{daily_fb.score}/10")
            with col_d:
                if daily_fb.correct_points:
                    st.write("**✅ Correct:**")
                    for p in daily_fb.correct_points:
                        st.write(f"  • {p}")
                if daily_fb.missing_points:
                    st.write("**❌ Missing:**")
                    for p in daily_fb.missing_points:
                        st.write(f"  • {p}")
            if daily_fb.suggestions:
                st.info(f"💡 {daily_fb.suggestions}")
    else:
        st.info("Click the button above to get today's challenge!")


# ─── Practice History Section ─────────────────────────────────────

def _render_practice_history():
    """Render the practice history section."""
    st.subheader("📊 Recent Practice Sessions")

    history = st.session_state.get("practice_history", [])

    if history:
        history_rows = []
        for entry in history[:10]:  # Last 10 sessions
            history_rows.append({
                "📂 Category": entry.get("category", "—"),
                "❓ Question": entry.get("question", "—"),
                "⭐ Score": entry.get("score", "—"),
                "🕐 Time": entry.get("time", "—")
            })

        df = pd.DataFrame(history_rows)
        st.dataframe(df, width='stretch', hide_index=True)

        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state["practice_history"] = []
            st.rerun()
    else:
        st.info("No practice sessions yet. Start practicing to see your history here!")


# ─── AI Suggestions Section ──────────────────────────────────────

def _render_ai_suggestions(weak_list, skill_avg_dict, avg_score):
    """Render AI-powered practice suggestions."""
    st.subheader("🤖 AI Suggestions")

    if st.button("💡 Get AI Suggestions", width='stretch', key="get_suggestions"):
        with st.spinner("🧠 AI is analyzing your performance..."):
            suggestions = generate_ai_suggestions(
                weak_areas=weak_list[:5],
                skill_scores=skill_avg_dict,
                avg_score=avg_score
            )
            st.session_state["ai_suggestions"] = suggestions
            st.rerun()

    suggestions = st.session_state.get("ai_suggestions")

    if suggestions:
        with st.container(border=True):
            # Struggle areas
            if suggestions.struggle_areas:
                st.write("**⚠️ You struggle with:**")
                for i, area in enumerate(suggestions.struggle_areas, 1):
                    st.write(f"  {i}. **{area}**")

            st.divider()

            # Recommended practice
            if suggestions.recommended_practice:
                st.write("**✅ Recommended Practice:**")
                for rec in suggestions.recommended_practice:
                    st.write(f"  ✓ {rec}")

            st.divider()

            # Advice
            if suggestions.advice:
                st.info(f"💡 **AI Advice:** {suggestions.advice}")
    else:
        st.info("Click the button above to get personalized AI suggestions based on your performance.")