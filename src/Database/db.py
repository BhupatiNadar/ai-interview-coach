import streamlit as st
import bcrypt

from src.Database.config import get_supabase_client



def create_new_user(name, email, hashed_password):

    return (
        get_supabase_client()
        .table("users")
        .insert({
            "user_name": name,
            "user_email": email,
            "password_hash": hashed_password
        })
        .execute()
    )



def check_user(email, password):

    response1 = (
        get_supabase_client()
        .table("users")
        .select("user_email,password_hash")
        .eq("user_email",email)
        .execute()
    )


    response2 = (
        get_supabase_client()
        .table("users")
        .select("user_id,user_name,user_email")
        .eq("user_email",email)
        .execute()
    )


    if not response1.data or not response2.data:

        return False,{}


    stored_hash = response1.data[0]["password_hash"]


    return (
        bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        ),
        response2.data[0]
    )




def save_resume_to_database(file_name, resume_text, structured_data):

    try:

        user_id = st.session_state["User_data"]["user_id"]

        get_supabase_client() \
            .table("resumes") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()


        data = {
            "user_id": user_id,
            "file_name": file_name,
            "resume_text": resume_text,
            "structured_data": structured_data
        }


        response = (
            get_supabase_client()
            .table("resumes")
            .insert(data)
            .execute()
        )


        if response.data:
            return True

        return False


    except Exception as e:

        st.error(f"Database Error: {e}")

        return False






def get_latest_resume():

    try:


        user_id = st.session_state["User_data"]["user_id"]



        response = (

            get_supabase_client()

            .table("resumes")

            .select("*")

            .eq("user_id",user_id)

            .order(
                "uploaded_at",
                desc=True
            )

            .limit(1)

            .execute()

        )



        if response.data:

            return response.data[0]


        return None



    except Exception as e:

        st.error(e)

        return None
    
def save_interview_result(
        user_id,
        interview_type,
        question_answers
):

    response = (
        get_supabase_client()
        .table("interview_session")
        .insert(
            {
                "user_id": user_id,
                "interview_type": interview_type,
                "question_answers": question_answers
            }
        )
        .execute()
    )


    return response


def save_interview_evaluation(interview_id, evaluation_data):

    response = (
        get_supabase_client()
        .table("interview_evaluations")
        .insert(
            {
                "interview_id": interview_id,

                "total_score":
                evaluation_data["total_score"],


                "overall_feedback":
                evaluation_data["overall_feedback"],


                "evaluations":
                evaluation_data["evaluations"]
            }
        )
        .execute()
    )


    return response


# ─── Reports Page Database Functions ────────────────────────────────

def get_all_interviews(user_id):
    """Fetch all interview sessions for a user, ordered by date."""
    try:
        response = (
            get_supabase_client()
            .table("interview_session")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching interviews: {e}")
        return []


def get_interview_evaluations(user_id):
    """Fetch all evaluations joined with interview sessions for a user."""
    try:
        response = (
            get_supabase_client()
            .table("interview_evaluations")
            .select("*, interview_session!inner(user_id, interview_type, created_at)")
            .eq("interview_session.user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching evaluations: {e}")
        return []


def get_report_data(user_id):
    """Aggregate all data needed for the Reports page."""
    interviews = get_all_interviews(user_id)
    evaluations = get_interview_evaluations(user_id)
    return {
        "interviews": interviews,
        "evaluations": evaluations
    }


# ─── Dashboard Page Database Functions ──────────────────────────────

def get_recent_interviews(user_id, limit=5):
    """Fetch the most recent interview sessions for a user."""
    try:
        response = (
            get_supabase_client()
            .table("interview_session")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching recent interviews: {e}")
        return []