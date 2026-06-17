import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """Lazily create and cache the Supabase client.

    This avoids accessing st.secrets at module-import time,
    which causes KeyError when Streamlit reloads modules.
    """
    if "supabase_client" not in st.session_state:
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]
