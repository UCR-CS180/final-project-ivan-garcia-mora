import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from engine.profile_service import submit_profile, fetch_profile_by_email
from engine.matching_service import run_matching, refresh_matches
from engine.simplifier import simplify_abstract
from engine.email_generator import generate_outreach_email
from engine.faq_engine import get_faq_response
from storage.abstracts import get_abstract_by_id
from storage.profiles import get_profile
from storage.email_history import save_email_draft, get_email_history

st.set_page_config(page_title="ResMAI", page_icon="🔬")
st.title("🔬 ResMAI")
st.caption("Find UCR research opportunities matched to your skills and interests.")

page = st.sidebar.radio(
    "Navigate",
    ["Create Profile", "Find Matches", "Email History", "Look Up Profile", "FAQ"]
)

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
        placeholder="e.g. example001@ucr.edu"
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
            with st.spinner("Matching you with research opportunities..."):
                result = refresh_matches(profile_id) if refresh \
                    else run_matching(profile_id, use_cache=True)

            if result["status"] == "success":
                st.session_state["matches"] = result["data"]["matches"]
                st.session_state["matches_from_cache"] = result["data"].get("from_cache", False)
                st.session_state["matches_profile_id"] = profile_id
                st.session_state["simplify_results"] = {}
                st.session_state["email_results"] = {}

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

    if "matches" in st.session_state and st.session_state.get("matches_profile_id") == profile_id:
        matches = st.session_state["matches"]
        from_cache = st.session_state.get("matches_from_cache", False)

        st.success(f"Found {len(matches)} matches!")
        if from_cache:
            st.caption("Showing cached results. Click 'Refresh Results' to re-run matching.")

        profile_result = get_profile(profile_id)
        profile_data = profile_result["data"] if profile_result["status"] == "success" else {}

        for match in matches:
            abstract_result = get_abstract_by_id(match["abstract_id"])
            if abstract_result["status"] != "success":
                continue

            ab = abstract_result["data"]
            ab_id = match["abstract_id"]

            with st.expander(f"#{match['rank']} — {ab['title']}"):
                st.write(f"**Lab:** {ab['lab'] or 'N/A'}")
                st.write(f"**Professor:** {ab['professor'] or 'N/A'}")
                st.write(f"**Department:** {ab['department'] or 'N/A'}")
                st.write(f"**Keywords:** {', '.join(ab['keywords'])}")
                st.divider()
                st.write("**Why this matches you:**")
                st.info(match["reason"])
                st.divider()
                st.write("**Abstract:**")
                st.write(ab["text"])
                st.divider()

                # ── Simplify Button ──
                if st.button("✨ Simplify This Abstract", key=f"simplify_{ab_id}"):
                    with st.spinner("Simplifying..."):
                        sim_result = simplify_abstract(ab["text"])
                    if sim_result["status"] == "success":
                        st.session_state.setdefault("simplify_results", {})[ab_id] = sim_result["data"]["bullets"]
                    else:
                        st.error(f"Could not simplify: {sim_result.get('message', '')}")

                if ab_id in st.session_state.get("simplify_results", {}):
                    st.subheader("Simplified Summary")
                    for bullet in st.session_state["simplify_results"][ab_id]:
                        st.write(f"• {bullet}")

                # ── Email Generator Button ──
                if st.button("📧 Generate Outreach Email", key=f"email_{ab_id}"):
                    if not profile_data:
                        st.error("Could not load your profile. Check your student ID.")
                    else:
                        with st.spinner("Drafting your email..."):
                            email_result = generate_outreach_email(profile_data, ab)

                        if email_result["status"] == "success":
                            st.session_state.setdefault("email_results", {})[ab_id] = email_result["data"]
                            save_email_draft(
                                profile_id,
                                ab_id,
                                email_result["data"]["subject"],
                                email_result["data"]["body"]
                            )
                            st.caption("Draft saved to your Email History.")
                        elif email_result["status"] == "incomplete":
                            st.warning(f"Missing info: {', '.join(email_result['missing'])}")
                            st.caption("Make sure the abstract has a professor name.")
                        else:
                            st.error(f"Could not generate email: {email_result.get('message', '')}")

                if ab_id in st.session_state.get("email_results", {}):
                    draft = st.session_state["email_results"][ab_id]
                    st.subheader("📬 Your Outreach Email Draft")
                    st.write(f"**Subject:** {draft['subject']}")
                    st.text_area("Email Body", value=draft["body"], height=300, key=f"body_{ab_id}")

# ─────────────────────────────────────────────
# PAGE: Email History
# ─────────────────────────────────────────────
elif page == "Email History":
    st.header("📬 Saved Email Drafts")
    st.write("View all outreach emails you have generated.")

    profile_id = st.text_input("Student ID", placeholder="e.g. student_abc12345")
    load = st.button("Load History", type="primary")

    if load:
        if not profile_id:
            st.warning("Please enter your student ID.")
        else:
            result = get_email_history(profile_id)

            if result["status"] == "success":
                drafts = result["data"]
                st.success(f"{len(drafts)} saved draft(s) found.")

                for draft in drafts:
                    ab_result = get_abstract_by_id(draft["abstract_id"])
                    ab_title = ab_result["data"]["title"] \
                        if ab_result["status"] == "success" else draft["abstract_id"]

                    with st.expander(f"{draft['subject']} — {ab_title}"):
                        st.caption(f"Generated: {draft['created_at']}")
                        st.write(f"**Subject:** {draft['subject']}")
                        st.text_area(
                            "Email Body",
                            value=draft["body"],
                            height=250,
                            key=f"history_{draft['id']}"
                        )

            elif result["status"] == "not_found":
                st.info("No saved drafts yet. Generate emails from the Find Matches page.")
            else:
                st.error(f"Something went wrong: {result.get('message', '')}")

# ─────────────────────────────────────────────
# PAGE: Look Up Profile
# ─────────────────────────────────────────────
elif page == "Look Up Profile":
    st.header("Look Up Your Profile")
    st.write("Enter your UCR email to retrieve your student ID.")

    email_lookup = st.text_input("UCR Email", placeholder="e.g. example001@ucr.edu")
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

# ─────────────────────────────────────────────
# PAGE: FAQ
# ─────────────────────────────────────────────
elif page == "FAQ":
    st.header("FAQ")
    st.write("Ask anything about ResMAI or UCR undergraduate research.")

    question = st.text_input("Your question", placeholder="e.g. How does matching work?")
    ask = st.button("Ask", type="primary")

    if ask:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Looking that up..."):
                result = get_faq_response(question)

            if result["status"] == "success":
                st.info(result["data"]["answer"])
            elif result["status"] == "not_found":
                st.warning(result["message"])
            elif result["status"] == "invalid_input":
                st.warning(result["message"])
            else:
                st.error(f"Something went wrong: {result.get('message', 'unknown error')}")