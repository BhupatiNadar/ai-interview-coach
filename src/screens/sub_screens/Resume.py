import streamlit as st
from pypdf import PdfReader

from src.Database.db import (
    save_resume_to_database,
    get_latest_resume
)



def extract_pdf_text(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        text += page.extract_text() or ""


    return text




def resume():


    st.header("Upload Your Resume")


    st.write(
        "Upload your resume and our AI will analyze it "
        "to personalize your interview experience"
    )



    file = st.file_uploader(
        "Browse Files",
        type=["pdf"]
    )



    if file:


        if st.button("Upload File"):


            with st.spinner("Analyzing Resume..."):


                resume_text = extract_pdf_text(file)


                saved = save_resume_to_database(
                    file.name,
                    resume_text
                )


                if saved:

                    st.success(
                        "Resume uploaded successfully"
                    )




    st.write("### Recently Uploaded File")



    # Fetch from database

    resume_data = get_latest_resume()



    if resume_data:


        col1,col2 = st.columns([3,1])


        with col1:

            st.write(
                resume_data["file_name"]
            )



        with col2:


            if st.button("View"):


                # send resume to next page

                st.session_state["resume_text"] = (
                    resume_data["resume_text"]
                )


                st.session_state["resume_name"] = (
                    resume_data["file_name"]
                )


                st.session_state["User_tab"] = (
                    "Resume_Analyze"
                )


                st.rerun()



    else:


        st.write(
            "No resume uploaded."
        )