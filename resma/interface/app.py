import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from engine.profile_service import submit_profile, fetch_profile_by_email
from engine.matching_service import run_matching, refresh_matches
from storage.abstracts import get_abstract_by_id

st.set_page_config(page_title="ResMa AI", page_icon="🔬")
st.title("🔬 ResMa AI")
st.caption("Find UCR research opportunities matched to your skills and interests.")

page = st.sidebar.radio("Navigate", ["Create Profile", "Find Matches", "Look Up Profile"])

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
# PAGE: Find Matches
# ─────────────────────────────────────────────
elif page == "Find Matches":
    st.header("Find Research Matches")
    st.write("Enter your student ID to get matched with UCR research opportunities.")

    profile_id = st.text_input("Student ID", placeholder="e.g. student_abc12345")

    col1, col2 = st.columns([1, 1])
    find = col1.button("Find Matches", type="primary")
    refresh = col2.button("Refresh Results")

    if find or refresh:
        if not profile_id:
            st.warning("Please enter your student ID.")
        else:
            use_cache = not refresh

            with st.spinner("Matching you with research opportunities..."):
                result = run_matching(profile_id, use_cache=use_cache) \
                    if not refresh else refresh_matches(profile_id)

            if result["status"] == "success":
                matches = result["data"]["matches"]
                from_cache = result["data"].get("from_cache", False)

                st.success(f"Found {len(matches)} matches!")
                if from_cache:
                    st.caption("Showing cached results. Click 'Refresh Results' to re-run matching.")

                for match in matches:
                    abstract_result = get_abstract_by_id(match["abstract_id"])

                    if abstract_result["status"] == "success":
                        ab = abstract_result["data"]

                        with st.expander(f"#{match['rank']} — {ab['title']}"):
                            st.write(f"**Lab:** {ab['lab'] or 'N/A'}")
                            st.write(f"**Professor:** {ab['professor'] or 'N/A'}")
                            st.write(f"**Department:** {ab['department'] or 'N/A'}")
                            st.write(f"**Keywords:** {', '.join(ab['keywords'])}")
                            st.divider()
                            st.write(f"**Why this matches you:**")
                            st.info(match["reason"])
                            st.divider()
                            st.write(f"**Abstract:**")
                            st.write(ab["text"])

            elif result["status"] == "not_found":
                st.error("Student ID not found. Please create a profile first.")

            elif result["status"] == "no_abstracts":
                st.error("No research abstracts in the database yet.")
                st.caption("Run `python storage/init_db.py` to seed abstracts.")

            elif result["status"] == "no_matches":
                st.warning(result.get("message", "No matches found."))
                st.caption("Try broadening your interests in your profile.")

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