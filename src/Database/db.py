import streamlit as st
import bcrypt

from src.Database.config import Supabase



def create_new_user(name, email, hashed_password):

    return (
        Supabase
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
        Supabase
        .table("users")
        .select("user_email,password_hash")
        .eq("user_email",email)
        .execute()
    )


    response2 = (
        Supabase
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

        Supabase \
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
            Supabase
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

            Supabase

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