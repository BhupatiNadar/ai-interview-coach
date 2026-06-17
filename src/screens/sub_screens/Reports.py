import streamlit as st
import pandas as pd
import json
from datetime import datetime

from src.Database.db import get_report_data


# ─── Helper Functions ───────────────────────────────────────────────

def _parse_evaluations(evaluations_data):
    """Parse evaluations from database records into usable analytics."""
    all_scores = []
    all_feedback = []
    skill_scores = {}
    weaknesses = {}
    strengths = {}

    for eval_record in evaluations_data:
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

        num_questions = len(evals) if evals else 1
        avg_score = round(total_score / num_questions, 1) if num_questions > 0 else 0
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


def _extract_topics(question):
    """Extract relevant tech topics from a question string."""
    topic_keywords = {
        "Python": ["python", "django", "flask", "fastapi"],
        "JavaScript": ["javascript", "react", "node", "angular", "vue", "typescript"],
        "Machine Learning": ["machine learning", "ml", "deep learning", "neural", "tensorflow", "pytorch"],
        "Data Science": ["data science", "pandas", "numpy", "data analysis"],
        "SQL": ["sql", "database", "query", "postgres", "mysql", "mongodb"],
        "System Design": ["system design", "architecture", "scalability", "microservices", "distributed"],
        "DSA": ["algorithm", "data structure", "sorting", "searching", "tree", "graph", "linked list"],
        "API Design": ["api", "rest", "graphql", "endpoint"],
        "Cloud": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes"],
        "Git": ["git", "version control", "github", "ci/cd"],
        "Communication": ["communication", "explain", "describe", "tell me about"],
        "Problem Solving": ["problem solving", "approach", "solve", "debug", "troubleshoot"],
        "Backend": ["backend", "server", "microservice", "caching", "redis", "queue"],
        "Frontend": ["frontend", "ui", "ux", "css", "html", "responsive"],
        "DevOps": ["devops", "ci/cd", "pipeline", "jenkins", "terraform"],
        "Security": ["security", "authentication", "authorization", "encryption", "oauth"],
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


def _generate_ai_insights(all_scores, skill_scores, weaknesses, strengths, all_feedback):
    """Generate AI-like insights from the interview data."""
    insights = []

    if not all_scores:
        return ["Complete some interviews to get personalized AI insights."]

    avg = sum(all_scores) / len(all_scores)

    # Trend analysis
    if len(all_scores) >= 2:
        recent = all_scores[:max(1, len(all_scores) // 2)]
        older = all_scores[max(1, len(all_scores) // 2):]
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older) if older else recent_avg

        if recent_avg > older_avg:
            diff = round(recent_avg - older_avg, 1)
            insights.append(f"📈 **Great progress!** Your recent scores are up by **+{diff} points** compared to earlier interviews.")
        elif recent_avg < older_avg:
            diff = round(older_avg - recent_avg, 1)
            insights.append(f"📉 Your recent scores dipped by **{diff} points**. Consider revisiting your preparation strategy.")
        else:
            insights.append("📊 Your performance has been **consistent**. Push for improvement in weak areas.")

    # Strengths
    top_strengths = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_strengths:
        strength_names = ", ".join([s[0] for s in top_strengths])
        insights.append(f"💪 You show strong performance in **{strength_names}**. Keep building on these skills.")

    # Weaknesses
    top_weaknesses = sorted(weaknesses.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_weaknesses:
        weak_names = ", ".join([w[0] for w in top_weaknesses])
        insights.append(f"🎯 Areas needing attention: **{weak_names}**. Focus your next study sessions here.")

    # Recommendations
    if top_weaknesses:
        rec_lines = [f"  - **{w[0]}** — appeared as a weakness in {w[1]} question(s)" for w in top_weaknesses]
        insights.append("**Recommended focus areas:**\n" + "\n".join(rec_lines))

    # Overall assessment
    if avg >= 7:
        insights.append("🏆 Overall, you're performing at an **excellent level**. You're ready for real interviews!")
    elif avg >= 5:
        insights.append("📚 You're at a **good level** but there's room to improve. Keep practicing!")
    else:
        insights.append("🚀 You're building your foundation. **Consistent practice** will lead to rapid improvement.")

    return insights


def _generate_report_text(user_name, total_interviews, avg_score, best_score,
                          improvement_str, strengths_list, weaknesses_list, ai_insights):
    """Generate a text-based report for download."""
    lines = []
    lines.append("=" * 60)
    lines.append("       AI INTERVIEW COACH — PERFORMANCE REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Candidate:       {user_name}")
    lines.append(f"  Generated:       {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  SUMMARY STATISTICS")
    lines.append("-" * 60)
    lines.append(f"  Total Interviews:    {total_interviews}")
    lines.append(f"  Average Score:       {avg_score}/10")
    lines.append(f"  Best Score:          {best_score}/10")
    lines.append(f"  Improvement:         {improvement_str}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  TOP STRENGTHS")
    lines.append("-" * 60)
    if strengths_list:
        for s in strengths_list:
            lines.append(f"  ✓  {s}")
    else:
        lines.append("  No strengths identified yet.")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  AREAS FOR IMPROVEMENT")
    lines.append("-" * 60)
    if weaknesses_list:
        for i, w in enumerate(weaknesses_list, 1):
            lines.append(f"  {i}. {w}")
    else:
        lines.append("  No weaknesses identified yet.")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  AI RECOMMENDATIONS")
    lines.append("-" * 60)
    for insight in ai_insights:
        clean = insight.replace("**", "").replace("📈 ", "").replace("📉 ", "")
        clean = clean.replace("💪 ", "").replace("🎯 ", "").replace("🏆 ", "")
        clean = clean.replace("📚 ", "").replace("🚀 ", "").replace("📊 ", "")
        lines.append(f"  {clean}")
    lines.append("")
    lines.append("=" * 60)
    lines.append("  Generated by AI Interview Coach")
    lines.append("=" * 60)

    return "\n".join(lines)


# ─── Main Reports Page ─────────────────────────────────────────────

def reports():

    st.title("📊 Performance Reports")
    st.caption("Your complete interview analytics, insights, and improvement history")

    # ── Fetch Data ──────────────────────────────────────────────────
    user_data = st.session_state.get("User_data", {})
    user_id = user_data.get("user_id") if user_data else None

    if not user_id:
        st.warning("Please log in to view your reports.")
        return

    report_data = get_report_data(user_id)
    interviews = report_data["interviews"]
    evaluations = report_data["evaluations"]

    # ── Empty State ─────────────────────────────────────────────────
    if not interviews and not evaluations:
        st.divider()
        col_empty1, col_empty2, col_empty3 = st.columns([1, 2, 1])
        with col_empty2:
            st.info(
                "📋 **No Interview Data Yet**\n\n"
                "Complete your first interview to unlock detailed performance "
                "analytics, AI-powered insights, and progress tracking."
            )
        return

    # ── Parse Data ──────────────────────────────────────────────────
    all_scores, all_feedback, skill_scores, weaknesses_map, strengths_map = _parse_evaluations(evaluations)

    total_interviews = len(interviews)
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    best_score = round(max(all_scores), 1) if all_scores else 0

    # Calculate improvement percentage
    if len(all_scores) >= 2:
        first_score = all_scores[-1]  # oldest (list is newest-first)
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
    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="🎯 Total Interviews",
            value=total_interviews,
            help="Total number of interview sessions completed"
        )

    with c2:
        st.metric(
            label="📈 Average Score",
            value=f"{avg_score}/10",
            help="Average score across all interviews"
        )

    with c3:
        st.metric(
            label="🏆 Best Score",
            value=f"{best_score}/10",
            help="Your personal best score"
        )

    with c4:
        st.metric(
            label="🚀 Improvement",
            value=improvement_str,
            delta=improvement_str,
            help="Improvement from first to latest interview"
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: Performance Trend Chart
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📉 Performance Trend")

    if all_scores:
        scores_chronological = list(reversed(all_scores))
        chart_data = pd.DataFrame({
            "Score": scores_chronological
        }, index=[f"Interview {i+1}" for i in range(len(scores_chronological))])

        st.line_chart(chart_data, color="#8b5cf6")
    else:
        st.info("Complete interviews to see your performance trend.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3: Skills Breakdown
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🧩 Skills Breakdown")

    if skill_scores:
        skill_averages = {}
        for skill, scores in skill_scores.items():
            skill_averages[skill] = round(sum(scores) / len(scores), 1)

        sorted_skills = sorted(skill_averages.items(), key=lambda x: x[1], reverse=True)

        for skill, avg in sorted_skills[:10]:
            col_name, col_bar, col_score = st.columns([1.5, 4, 0.5])
            with col_name:
                st.write(f"**{skill}**")
            with col_bar:
                st.progress(min(avg / 10, 1.0))
            with col_score:
                st.write(f"**{avg}**/10")
    else:
        st.info("Skill breakdown will appear after your interviews are evaluated.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 4: Interview History Table
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📋 Interview History")

    if evaluations:
        history_rows = []
        for eval_rec in evaluations:
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

            feedback_text = eval_rec.get("overall_feedback", "—")
            if len(feedback_text) > 80:
                feedback_text = feedback_text[:80] + "..."

            history_rows.append({
                "📅 Date": date_str,
                "📝 Type": interview_type,
                "⭐ Score": f"{avg}/10",
                "❓ Questions": num_q,
                "💬 Feedback": feedback_text
            })

        df_history = pd.DataFrame(history_rows)
        st.dataframe(df_history,width='stretch', hide_index=True)
    else:
        st.info("No interview evaluations found yet.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 5 & 6: Weaknesses and Strengths
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()

    col_weak, col_strong = st.columns(2)

    with col_weak:
        st.subheader("⚠️ Weak Areas")
        top_weaknesses = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:6]
        if top_weaknesses:
            for topic, count in top_weaknesses:
                st.warning(f"⚡ **{topic}** — low score in {count} question(s)")
        else:
            st.success("No weak areas identified — keep going! 💪")

    with col_strong:
        st.subheader("✅ Strengths")
        top_strengths = sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)[:6]
        if top_strengths:
            for topic, count in top_strengths:
                st.success(f"✓ **{topic}** — high score in {count} question(s)")
        else:
            st.info("Complete more interviews to discover your strengths 🌟")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 7: AI Insights
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("🤖 AI-Powered Insights")

    ai_insights = _generate_ai_insights(all_scores, skill_scores, weaknesses_map, strengths_map, all_feedback)

    with st.container(border=True):
        for insight in ai_insights:
            st.markdown(insight)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 8: Interview Comparison (Latest vs Previous)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if len(evaluations) >= 2:
        st.divider()
        st.subheader("🔄 Interview Comparison")

        latest_eval = evaluations[0]
        previous_eval = evaluations[1]

        def _get_topic_scores(eval_record):
            evals = eval_record.get("evaluations", [])
            if isinstance(evals, str):
                try:
                    evals = json.loads(evals)
                except (json.JSONDecodeError, TypeError):
                    evals = []
            if not isinstance(evals, list):
                evals = []

            total = eval_record.get("total_score", 0)
            num_q = len(evals) if evals else 1
            avg = round(total / num_q, 1) if num_q > 0 else 0

            topic_scores = {}
            for e in evals:
                if isinstance(e, dict):
                    topics = _extract_topics(e.get("question", ""))
                    score = e.get("score", 0)
                    for t in topics:
                        if t not in topic_scores:
                            topic_scores[t] = []
                        topic_scores[t].append(score)

            return avg, {k: round(sum(v) / len(v), 1) for k, v in topic_scores.items()}

        latest_avg, latest_topics = _get_topic_scores(latest_eval)
        prev_avg, prev_topics = _get_topic_scores(previous_eval)

        all_topics_set = sorted(set(list(latest_topics.keys()) + list(prev_topics.keys())))[:6]

        # Build comparison table
        comparison_rows = []
        for topic in all_topics_set:
            prev_s = prev_topics.get(topic, "—")
            latest_s = latest_topics.get(topic, "—")

            if isinstance(prev_s, (int, float)) and isinstance(latest_s, (int, float)):
                diff = round(latest_s - prev_s, 1)
                if diff > 0:
                    change = f"+{diff} ↑"
                elif diff < 0:
                    change = f"{diff} ↓"
                else:
                    change = "0 →"
            else:
                change = "—"

            comparison_rows.append({
                "Skill": topic,
                "Previous": prev_s,
                "Latest": latest_s,
                "Change": change
            })

        df_comparison = pd.DataFrame(comparison_rows)

        col_prev, col_curr, col_diff = st.columns(3)

        with col_prev:
            st.markdown("**📌 Previous Interview**")
            for topic in all_topics_set:
                score = prev_topics.get(topic, "—")
                st.write(f"• {topic}: **{score}**")

        with col_curr:
            st.markdown("**🆕 Latest Interview**")
            for topic in all_topics_set:
                score = latest_topics.get(topic, "—")
                st.write(f"• {topic}: **{score}**")

        with col_diff:
            st.markdown("**🔺 Improvement**")
            for topic in all_topics_set:
                prev_s = prev_topics.get(topic, 0)
                latest_s = latest_topics.get(topic, 0)
                if isinstance(prev_s, (int, float)) and isinstance(latest_s, (int, float)):
                    diff = round(latest_s - prev_s, 1)
                    if diff > 0:
                        st.write(f"• {topic}: :green[**+{diff}**] ↑")
                    elif diff < 0:
                        st.write(f"• {topic}: :red[**{diff}**] ↓")
                    else:
                        st.write(f"• {topic}: **0** →")
                else:
                    st.write(f"• {topic}: —")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 9: Learning Progress
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if weaknesses_map:
        st.divider()
        st.subheader("📚 Learning Progress")

        weak_topics = sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:5]

        for topic, count in weak_topics:
            topic_avg = skill_scores.get(topic, [0])
            mastery = round((sum(topic_avg) / len(topic_avg) / 10) * 100)

            col_name, col_bar, col_pct = st.columns([1.5, 4, 0.5])
            with col_name:
                st.write(f"**{topic}**")
            with col_bar:
                st.progress(min(mastery / 100, 1.0))
            with col_pct:
                st.write(f"**{mastery}%**")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 10: Download Report
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.divider()
    st.subheader("📥 Download Report")

    user_name = user_data.get("user_name", "User")
    top_strength_names = [s[0] for s in sorted(strengths_map.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_weakness_names = [w[0] for w in sorted(weaknesses_map.items(), key=lambda x: x[1], reverse=True)[:5]]

    report_text = _generate_report_text(
        user_name=user_name,
        total_interviews=total_interviews,
        avg_score=avg_score,
        best_score=best_score,
        improvement_str=improvement_str,
        strengths_list=top_strength_names,
        weaknesses_list=top_weakness_names,
        ai_insights=ai_insights
    )

    st.info("📄 Download your complete performance report as a text file")

    st.download_button(
        label="📥 Download Performance Report",
        data=report_text,
        file_name=f"interview_report_{user_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
       width='stretch'
    )