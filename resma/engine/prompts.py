def build_match_prompt(profile: dict, abstracts: list) -> str:
    """
    Build the Gemini prompt for matching a student profile
    against a list of research abstracts.
    """
    abstract_block = ""
    for i, ab in enumerate(abstracts):
        keywords = ", ".join(ab.get("keywords", []))
        abstract_block += f"""
[{i+1}] ID: {ab['id']}
Title: {ab['title']}
Keywords: {keywords}
Abstract: {ab['text'][:300]}
"""

    return f"""
You are a research advisor helping an undergraduate student find research opportunities.

Student Profile:
- Major: {profile['major']}
- Year: {profile['year']}
- Interests: {', '.join(profile['interests'])}
- Skills: {', '.join(profile['skills'])}

Below are {len(abstracts)} research abstracts. Return the top 3 to 5 best matches
for this student ranked from best to worst fit.

For each match return ONLY this exact JSON format with no extra text, no markdown, no code fences:
{{
  "matches": [
    {{
      "abstract_id": "ab_01",
      "rank": 1,
      "reason": "one sentence explaining why this matches the student"
    }}
  ]
}}

Abstracts:
{abstract_block}
"""


def build_simplify_prompt(abstract_text: str) -> str:
    """
    Build the Gemini prompt for simplifying a research abstract
    into 3 beginner-friendly bullet points.
    """
    return f"""
You are explaining a research project to an undergraduate student with no prior knowledge of the topic.

Summarize the following research abstract into exactly 3 bullet points:
1. Goal: What is this project trying to accomplish?
2. Skills needed: What technical skills or background would be helpful?
3. Why it matters: What is the real-world impact of this research?

Keep each bullet point to 1-2 sentences. Use plain language a first-year student can understand.

Return ONLY this exact JSON format with no extra text, no markdown, no code fences:
{{
  "bullets": [
    "Goal: ...",
    "Skills needed: ...",
    "Why it matters: ..."
  ]
}}

Abstract:
{abstract_text}
"""


def build_faq_prompt(user_query: str) -> str:
    """
    Build the Gemini prompt for answering a student FAQ about ResMAI
    and UCR undergraduate research.
    """
    return f"""
You are a helpful assistant for ResMAI, a web app that matches UCR undergraduate students
with faculty research opportunities.

You can answer questions about:
- How to use ResMAI (creating a profile, finding matches, generating emails)
- General UCR undergraduate research (how to get involved, what to expect, cold-emailing professors)
- What the app does and how matching works

If the question is completely unrelated to research, UCR, or this app, set "found" to false.

Return ONLY this exact JSON format with no extra text, no markdown, no code fences:
{{
  "found": true,
  "answer": "your answer here"
}}

If you cannot answer, return:
{{
  "found": false,
  "answer": ""
}}

Student question: {user_query}
"""


def build_email_prompt(profile: dict, abstract: dict) -> str:
    """
    Build the Gemini prompt for generating a professional
    outreach email from a student to a professor.
    """
    return f"""
You are helping an undergraduate student write a professional cold outreach email
to a professor whose research they are interested in joining.

Student Background:
- Major: {profile['major']}
- Year: {profile['year']}
- Interests: {', '.join(profile['interests'])}
- Skills: {', '.join(profile['skills'])}

Research Opportunity:
- Title: {abstract['title']}
- Professor: {abstract.get('professor', 'the professor')}
- Lab: {abstract.get('lab', 'the lab')}
- Abstract: {abstract['text'][:400]}

Write a professional, concise email (under 200 words) that:
- Has a clear subject line
- Introduces the student and their year/major
- References the specific research project by name
- Connects the student's skills/interests to the research
- Ends with a polite ask to discuss opportunities

Return ONLY this exact JSON format with no extra text, no markdown, no code fences:
{{
  "subject": "email subject line here",
  "body": "full email body here"
}}
"""