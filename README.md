# ResMAI — Research Matching AI

ResMAI is a Streamlit web app that matches UCR students with faculty research opportunities using Google's Gemini AI. Students create a profile with their major, year, interests, and skills. The app queries a database of research abstracts, runs them through Gemini to rank and explain the best fits, and then lets students simplify dense abstracts into plain language or generate a ready-to-send outreach email to the professor — all saved to a personal email history.

---

## Repository Overview

| | Path |
|---|---|
| Source code | [resma/](resma/) |
| Tests | [resma/tests/](resma/tests/) |
| Requirement specification | [FUNCTIONALITY.md](FUNCTIONALITY.md) |
| Design document | [CONTRACT.md](CONTRACT.md) |
| Demo video |https://youtu.be/Wc5PvdlOc2k |

---

## Setup

### 1. Install dependencies

```bash
pip install -r resma/requirements.txt
```

Dependencies:
| Package | Version |
|---|---|
| `streamlit` | >=1.35.0 |
| `google-generativeai` | >=0.5.0 |
| `python-dotenv` | >=1.0.0 |

### 2. Configure credentials

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/).

### 3. Initialize the database

Run once to create tables and seed research abstracts:

```bash
python resma/storage/init_db.py
```

---

## How to Run

```bash
streamlit run resma/interface/app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## Usage Examples

### Example 1 — Create a student profile

Navigate to **Create Profile** and fill in the form:

| Field | Input |
|---|---|
| Major | Computer Science |
| Year | Junior |
| Research Interests | machine learning, compilers |
| Skills | Python, C++, Linux |
| UCR Email | example001@ucr.edu |

**Expected output:** A unique student ID such as `student_a3f92c1d`. Save this ID — it is used for all other pages.

---

### Example 2 — Find research matches

Navigate to **Find Matches**, enter your student ID, and click **Find Matches**.

**Expected output:** A ranked list of research abstracts. Each result shows:
- Lab, professor, and department
- A plain-language explanation of *why* it matches your profile
- The full abstract text
- Buttons to simplify the abstract or draft an outreach email

Clicking **Simplify This Abstract** returns three bullet points:
```
• Goal: Develop faster compiler optimizations for GPU workloads.
• Skills needed: C++, LLVM, parallel programming.
• Why it matters: Speeds up machine learning training by 30%.
```

---

### Example 3 — Generate an outreach email

From any match card, click **Generate Outreach Email**.

**Expected output:** A ready-to-edit draft saved to your Email History:

```
Subject: Interest in Joining Your Research Lab — Ivan Garcia

Dear Professor Smith,

My name is Ivan Garcia and I am a junior studying Computer Science at UCR.
I came across your work on GPU compiler optimizations and I am very interested
in contributing to your lab. I have experience with Python, C++, and Linux,
and have taken coursework in compilers and parallel systems...
```

---

## Project Structure

```
resma/
├── interface/
│   └── app.py                  Streamlit UI — all pages and user interactions
├── engine/
│   ├── match_engine.py         Gemini API call for ranking abstracts
│   ├── matching_service.py     Orchestrates matching with cache support
│   ├── profile_service.py      Profile creation and lookup logic
│   ├── simplifier.py           Abstract simplification via Gemini
│   ├── email_generator.py      Outreach email generation via Gemini
│   ├── prompts.py              Prompt templates for all Gemini calls
│   └── validate_profile.py     Input validation rules
├── storage/
│   ├── db.py                   SQLite connection helper
│   ├── profiles.py             Student profile reads/writes
│   ├── abstracts.py            Abstract reads
│   ├── match_cache.py          Caches Gemini match results
│   ├── email_history.py        Saves and retrieves email drafts
│   └── init_db.py              Creates tables and seeds abstracts.json
├── tests/
│   ├── test_matching.py        Match engine and service tests
│   ├── test_profile_flow.py    Profile creation and lookup tests
│   └── test_week4.py           Simplifier and email generator tests
├── data/
│   ├── abstracts.json          Source data for research abstracts
│   └── resma.db                SQLite database (auto-created)
└── requirements.txt
```
