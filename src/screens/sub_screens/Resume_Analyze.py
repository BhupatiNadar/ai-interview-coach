import streamlit as st


def resume_analyze():

    col1, col2 = st.columns([3, 0.8])


    with col2:

        if st.button("Back to previous page"):

            st.session_state["User_tab"] = "Resume"
            st.rerun()



    st.header("Resume Analysis")

    st.write(
        "Our AI has analyzed your resume successfully"
    )



    data = st.session_state.get(
        "resume_structured_data",
        {}
    )




    # ---------------- SUMMARY ----------------


    col1, col2 = st.columns(2)



    with col1:

        st.subheader("Summary")


        st.write(
            data.get(
                "summary",
                "No summary found"
            )
        )


    with col2:

        st.subheader("Top Skills")


        skills = data.get(
            "skills",
            []
        )


        if skills:

            import math
            n = math.ceil(len(skills) / 3)

            s_col1, s_col2, s_col3 = st.columns(3)

            for col, chunk in zip(
                [s_col1, s_col2, s_col3],
                [skills[:n], skills[n:2*n], skills[2*n:]]
            ):
                with col:
                    for skill in chunk:
                        st.write("•", skill)





    # ---------------- EXPERIENCE ----------------


    col1, col2 = st.columns(2)



    with col1:

        st.subheader("Experience")


        experience = data.get(
            "experience",
            []
        )


        for exp in experience:


            st.write(
                f"""
            **Company:** {exp.get("company","N/A")}

            **Role:** {exp.get("role","N/A")}

            **Years:** {exp.get("years","N/A")}
            """
            )





    # ---------------- PROJECTS ----------------


    with col2:

        st.subheader("Projects")


        projects = data.get(
            "projects",
            []
        )


        for project in projects:


            technologies = project.get(
                "technologies",
                []
            )






            st.write(
                f"""
### {project.get("title","No Title")}


{project.get("description","No Description")}


**Technologies:**


{", ".join(
    tech.strip() for tech in technologies
)}

"""
            )