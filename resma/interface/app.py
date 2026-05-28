import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from engine.profile_service import submit_profile, fetch_profile_by_email

st.set_page_config(page_title="ResearchMatch AI", page_icon="🔬")
st.title("🔬 ResMa AI")
st.caption("Find UCR research opportunities matched to your skills and interests.")

page = st.sidebar.radio("Navigate", ["Create Profile", "Look Up Profile"])

# ─────────────────────────────────────────────
# PAGE: Create Profile
# ─────────────────────────────────────────────
if page == "Create Profile":
    st.header("Create Your Student Profile")
    st.write("Fill out your information below to get started.")

    major = st.text_input("Major", placeholder="e.g. Computer Science")

    year = st.selectbox(
        "Year",
        ["", "freshman", "sophomore", "junior", "senior"],
        format_func=lambda x: "Select your year..." if x == "" else x.capitalize()
    )

    interests = st.text_input(
        "Research Interests",
        placeholder="e.g. machine learning, robotics, compilers"
    )

    skills = st.text_input(
        "Skills",
        placeholder="e.g. Python, Rust, C, Linux"
    )

    email = st.text_input(
        "UCR Email",
        placeholder="e.g. igarc001@ucr.edu"
    )

    submitted = st.button("Save Profile", type="primary")

    if submitted:
        if not year:
            st.warning("Please select your year.")
        else:
            result = submit_profile({
                "email": email,
                "major": major,
                "year": year,
                "interests": interests,
                "skills": skills
            })

            if result["status"] == "success":
                st.success("Profile saved!")
                st.info(f"Your Student ID: **{result['id']}**")
                st.caption("Save this ID — you will need it to find matches.")

            elif result["status"] == "incomplete":
                st.error(f"Missing required fields: {', '.join(result['missing'])}")

            elif result["status"] == "validation_error":
                st.error(f"Invalid input: {result['message']}")

            elif result["status"] == "exists":
                st.warning("An account with that email already exists.")
                st.caption("Use 'Look Up Profile' to retrieve your student ID.")

            else:
                st.error(f"Something went wrong: {result.get('message', 'unknown error')}")

# ─────────────────────────────────────────────
# PAGE: Look Up Profile
# ─────────────────────────────────────────────
elif page == "Look Up Profile":
    st.header("Look Up Your Profile")
    st.write("Enter your UCR email to retrieve your student ID.")

    email_lookup = st.text_input("UCR Email", placeholder="e.g. igarc001@ucr.edu")
    lookup = st.button("Look Up", type="primary")

    if lookup:
        if not email_lookup:
            st.warning("Please enter your email.")
        else:
            result = fetch_profile_by_email(email_lookup)

            if result["status"] == "success":
                profile = result["data"]
                st.success("Profile found!")
                st.info(f"Your Student ID: **{profile['id']}**")

                with st.expander("View your profile details"):
                    st.write(f"**Major:** {profile['major']}")
                    st.write(f"**Year:** {profile['year'].capitalize()}")
                    st.write(f"**Interests:** {', '.join(profile['interests'])}")
                    st.write(f"**Skills:** {', '.join(profile['skills'])}")

            elif result["status"] == "not_found":
                st.error("No profile found with that email.")
                st.caption("Head to 'Create Profile' to get started.")

            else:
                st.error(f"Something went wrong: {result.get('message', 'unknown error')}")