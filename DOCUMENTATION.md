# PlacementAI — Full Project Documentation

> A full-stack AI-powered placement preparation assistant built for the FSD AI Hackathon.
> Covers 8 top companies, skill-based role matching, roadmap generation, and an intelligent chatbot.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Features — Detailed Breakdown](#4-features--detailed-breakdown)
5. [How the AI Works](#5-how-the-ai-works)
6. [Skill Matching Model — How It Works](#6-skill-matching-model--how-it-works)
7. [Dataset Details](#7-dataset-details)
8. [API Reference](#8-api-reference)
9. [How to Run](#9-how-to-run)
10. [Mentor Q&A — Likely Questions & Answers](#10-mentor-qa--likely-questions--answers)

---

## 1. Project Overview

**PlacementAI** is a web application that helps engineering students prepare for campus placements at top tech companies. It combines:

- A **conversational AI chatbot** that answers placement-related questions
- A **skill analyzer** that tells you how well you fit each job role at each company
- A **personalized roadmap generator** that gives you a week-by-week study plan
- A **problems dashboard** with company-specific LeetCode questions sorted by frequency

**Target Users:** Final-year engineering students preparing for campus placements.

**Problem It Solves:** Students don't know *where to start*, *which skills to learn*, or *which company to target*. PlacementAI gives them a clear, data-driven answer.

---

## 2. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React (Vite) | Fast, component-based UI |
| Backend | Python + Flask | Lightweight REST API, easy ML integration |
| Data Processing | Pandas | CSV parsing, sorting, filtering |
| AI / Logic | Custom NLP + Weighted Scoring | Rule-based intent detection + skill matching |
| Dataset | CSV (LeetCode) + JSON (Skills) | Real company problem data |
| Styling | Plain CSS | Full control, no framework overhead |
| Communication | REST API (JSON) | Standard, simple, fast |

---

## 3. Project Structure

```
fsd-ai-hackathon/
│
├── backend/
│   ├── app.py              ← Flask server, all AI logic lives here
│   └── requirements.txt    ← Python dependencies
│
├── dataset/
│   ├── google.csv          ← LeetCode problems asked at Google
│   ├── amazon.csv          ← LeetCode problems asked at Amazon
│   ├── microsoft.csv
│   ├── apple.csv
│   ├── netflix.csv
│   ├── tcs.csv
│   ├── accenture.csv
│   ├── zoho.csv
│   └── skills_dataset.json ← Role definitions with required & good-to-have skills
│
├── frontend/
│   └── src/
│       ├── App.jsx         ← Main React app (all UI components)
│       └── App.css         ← All styles
│
├── start.bat               ← One-click launcher
└── DOCUMENTATION.md        ← This file
```

---

## 4. Features — Detailed Breakdown

### 💬 Feature 1: AI Chatbot

An intelligent chatbot that understands natural language questions across 8 categories:

| Category | Example Questions |
|---|---|
| General Placement | "What is the placement process?", "Skills required to get a job" |
| DSA / Coding | "Give me array problems", "Hard DSA questions", "Important graph problems" |
| Aptitude | "Give me aptitude questions", "Number series problems", "How to improve aptitude?" |
| Interview Prep | "Common HR questions", "Tell me about yourself answer", "STAR method" |
| Study Strategy | "How to prepare in 30 days?", "Daily study plan", "Best resources" |
| Company Tips | "Tips for Google", "How to crack Amazon interview" |
| Company Stats | "Stats for TCS", "How many problems does Netflix have?" |
| Compare | "Compare Google vs Amazon" |

---

### 💡 Feature 2: Skill Analyzer

The most unique feature of the project. The user enters their skills (e.g., Python, SQL, React) and the system:

1. Compares their skills against every role at every company
2. Calculates a **Fit Score (0–100%)** for each role
3. Shows **missing required skills** (highlighted in red)
4. Shows **missing good-to-have skills** (highlighted in yellow)
5. Generates a **personalized 8-week roadmap**
6. Ranks all roles across all companies by fit score

---

### 📊 Feature 3: Dashboard

- Visual cards for all 8 companies
- Shows total problems, Easy / Medium / Hard count, average acceptance rate
- Color-coded difficulty bar for each company
- Click any card to jump to that company's problem list

---

### 📋 Feature 4: Problems Table

- Company-specific LeetCode problems
- Sorted Easy → Medium → Hard, then by Frequency % (most asked first)
- Filter by difficulty (All / Easy / Medium / Hard)
- Direct links to LeetCode problems
- Shows Acceptance % and Frequency %

---

## 5. How the AI Works

The chatbot uses a **Rule-Based NLP Pipeline** — no external API, no paid model. Everything runs locally.

### Step 1 — Intent Detection (`extract_intent`)

The user's message is lowercased and scanned for keyword patterns:

```
User message → lowercase → keyword scan → intent label
```

**Intent categories and their trigger keywords:**

| Intent | Keywords |
|---|---|
| `skills` | "my skill", "i know", "roadmap", "fit for", "which role" |
| `aptitude` | "aptitude", "number series", "probability", "logical reasoning" |
| `interview` | "hr", "interview", "strengths", "weaknesses", "tell me about yourself" |
| `strategy` | "30 days", "study plan", "how many hours", "best resources" |
| `placement` | "placement", "placement process", "how to start", "get a job" |
| `dsa` | "array", "string", "graph", "tree", "dp", "coding question" |
| `stats` | "stat", "overview", "how many", "total" |
| `tips` | "tip", "advice", "how to", "guide" |
| `compare` | "compare", "vs", "versus" |
| `problems` | "show", "give", "top", "list", "practice" |

### Step 2 — Entity Extraction

Alongside intent, the system also extracts:
- **Company name** — scans for any of the 8 company names in the message
- **Difficulty** — detects "easy", "medium", "hard", "beginner", "difficult"

### Step 3 — Response Building (`build_response`)

Based on the intent + company + difficulty, the system returns a structured JSON response with a `type` field that tells the frontend how to render it:

| Response Type | Rendered As |
|---|---|
| `text` | Formatted markdown-style text bubble |
| `problems` | Clickable problem list with difficulty badges |
| `dsa_problems` | Curated LeetCode links for specific topics |
| `stats` | Grid of company stat cards |

---

## 6. Skill Matching Model — How It Works

This is the core "AI model" of the project. It is a **Weighted Skill Overlap Scoring Model**.

### The Formula

```
Fit Score = (Required Skill Match / Total Required) × 70
          + (Good-to-Have Match / Total Good-to-Have) × 30
```

**Why 70/30 split?**
- Required skills are non-negotiable for the role → weighted higher (70%)
- Good-to-have skills improve your candidacy but aren't blockers → weighted lower (30%)

### Example Calculation

**User skills:** Python, SQL, Machine Learning, Statistics

**Role:** Google — Machine Learning Engineer
- Required: Python ✅, Machine Learning ✅, Deep Learning ❌, TensorFlow ❌, PyTorch ❌, Linear Algebra ❌, Statistics ✅, Data Structures ❌, Algorithms ❌, SQL ✅
- Required match: 4/10 → 4/10 × 70 = **28**
- Good-to-have: NLP ❌, Computer Vision ❌, Kubernetes ❌, Spark ❌, Big Data ❌, Research Papers ❌
- Good-to-have match: 0/6 → 0/6 × 30 = **0**
- **Fit Score = 28%**

### Roadmap Generation Logic

The roadmap is generated based on the fit score band:

| Fit Score | Status | Roadmap Focus |
|---|---|---|
| 0–39% | Beginner | Core programming, Easy LeetCode, DSA basics |
| 40–69% | Intermediate | Fill required gaps, Medium problems, System Design intro |
| 70–100% | Advanced | Hard problems, System Design deep dive, Mock interviews |

The roadmap also lists:
- Missing required skills (must learn)
- Missing good-to-have skills (nice to learn)
- Week-by-week 8-week study plan

### Skill Normalization

All skills are lowercased and stripped before comparison to handle case mismatches:
```
"Python" == "python" == "PYTHON"  → all treated as the same skill
```

---

## 7. Dataset Details

### LeetCode CSVs (8 files)

Each CSV contains problems asked by that company in real interviews, sourced from LeetCode's company tag data.

**Columns:**
| Column | Description |
|---|---|
| ID | LeetCode problem number |
| Title | Problem name |
| Difficulty | Easy / Medium / Hard |
| Acceptance % | % of users who solved it correctly |
| Frequency % | How often this problem appears in interviews |
| URL | Direct LeetCode link |

**Sorting logic:** Problems are sorted Easy → Medium → Hard, then within each difficulty by Frequency % descending (most asked first).

### skills_dataset.json

A manually curated JSON file with role definitions for all 8 companies.

**Structure:**
```json
{
  "company_name": {
    "Role Name": {
      "required": ["skill1", "skill2", ...],
      "good_to_have": ["skill3", "skill4", ...],
      "description": "What this role does"
    }
  }
}
```

**Coverage:**
| Company | Roles Covered |
|---|---|
| Google | SWE, ML Engineer, Data Engineer, SRE |
| Amazon | SDE, Data Scientist, Cloud Architect, Business Analyst |
| Microsoft | SWE, Cloud Engineer, AI/ML Engineer, Product Manager |
| Apple | iOS Developer, SWE, ML Engineer, Hardware Engineer |
| Netflix | Senior SWE, Data Engineer, ML Engineer, Security Engineer |
| TCS | Software Developer, System Analyst, DevOps Engineer, Data Analyst |
| Accenture | Associate SWE, Cloud Engineer, Data Analyst, Cybersecurity Analyst |
| Zoho | Software Developer, Full Stack Developer, Data Scientist, QA Engineer |

**Total: 32 roles across 8 companies**

---

## 8. API Reference

### POST `/api/chat`
The main chatbot endpoint.

**Request:**
```json
{ "message": "Give me easy problems for Google" }
```

**Response:**
```json
{
  "text": "Top Easy problems for Google...",
  "type": "problems",
  "problems": [...],
  "company": "google",
  "difficulty": "Easy"
}
```

---

### POST `/api/skills`
Skill analysis and roadmap generation.

**Request:**
```json
{ "skills": ["Python", "SQL", "Machine Learning"] }
```

**Response:**
```json
{
  "google": {
    "Machine Learning Engineer": {
      "fit": 42.0,
      "description": "...",
      "missing_required": ["Deep Learning", "TensorFlow", ...],
      "missing_good_to_have": ["NLP", "Computer Vision", ...],
      "roadmap": ["📈 Good foundation!", "🔴 Must Learn: ...", "📚 Week 1-2: ..."]
    }
  }
}
```

---

### GET `/api/stats`
Returns problem counts for all companies.

### GET `/api/problems/<company>`
Returns problems for a specific company.

**Query params:** `?difficulty=Easy&limit=20`

### GET `/api/companies`
Returns list of all supported companies.

---

## 9. How to Run

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher

### Option 1 — One Click
```
Double-click start.bat
```

### Option 2 — Manual

**Terminal 1 (Backend):**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend → http://localhost:5173
- Backend API → http://localhost:5000

---

## 10. Mentor Q&A — Likely Questions & Answers

---

**Q: What kind of AI/ML model did you use?**

A: We built two AI components. First, a **rule-based NLP intent classifier** that parses user messages using keyword pattern matching to detect intent (DSA, aptitude, interview, etc.), company name, and difficulty level. Second, a **weighted skill overlap scoring model** for the skill analyzer — it computes a fit score using a 70/30 weighted formula (required skills = 70%, good-to-have = 30%) and generates a personalized roadmap based on the score band.

---

**Q: Why didn't you use a pre-trained model like GPT or BERT?**

A: Our use case is highly structured and domain-specific — placement prep for 8 specific companies. A rule-based approach gives us 100% predictable, accurate responses for this domain without latency, API costs, or hallucination risks. For a hackathon context, it also demonstrates that we understand the underlying logic rather than just calling an API.

---

**Q: How accurate is the skill matching?**

A: The model is deterministic — given the same skills, it always produces the same score. Accuracy depends on the quality of the skills dataset, which we manually curated based on real job descriptions for each role. The 70/30 weighting is a deliberate design choice reflecting industry norms where required skills are non-negotiable.

---

**Q: What is the dataset and where did it come from?**

A: We use two datasets. The LeetCode CSVs contain real interview problems tagged by company, with frequency and acceptance data. The skills JSON is a manually curated dataset of 32 role definitions across 8 companies, built from real job postings and interview guides.

---

**Q: How does the chatbot understand different questions?**

A: The chatbot uses a multi-step pipeline: (1) lowercase the message, (2) scan for company names, (3) scan for difficulty keywords, (4) scan for intent keywords in priority order. The priority order matters — for example, "aptitude" is checked before "problems" so "give me aptitude questions" doesn't fall into the generic problems handler.

---

**Q: What happens if the user asks something the bot doesn't understand?**

A: The intent detection falls back to the `problems` intent as default. If no company is mentioned, it prompts the user to specify one. The system never crashes — it always returns a helpful response.

---

**Q: How is the roadmap personalized?**

A: The roadmap is generated in three parts: (1) a status message based on fit score band (0-39%, 40-69%, 70%+), (2) a list of missing required and good-to-have skills specific to that role, and (3) a generic 8-week study plan calibrated to the fit score band. So two users with different skills get different roadmaps for the same role.

---

**Q: What is the frontend built with and why?**

A: React with Vite. React gives us a component-based architecture that makes it easy to manage the chat state, skills tab, and dashboard independently. Vite provides fast hot-reload during development. We avoided heavy UI libraries to keep the bundle small and the design fully custom.

---

**Q: How does the problems sorting work?**

A: When the CSV is loaded at server startup, Pandas sorts each company's problems first by difficulty (Easy=0, Medium=1, Hard=2) and then by Frequency % in descending order within each difficulty group. This means the most frequently asked Easy problems appear first, followed by the most frequent Medium, then Hard.

---

**Q: Can this scale to more companies or roles?**

A: Yes, very easily. To add a new company: (1) add a CSV file to the dataset folder, (2) add the company name to the COMPANIES list in app.py, (3) add role definitions to skills_dataset.json. No code changes needed beyond that. The skill matching and roadmap logic is fully generic.

---

**Q: What are the limitations of this project?**

A: Three main limitations: (1) The rule-based chatbot can miss intent if the user phrases things very unusually — a transformer-based model would handle this better. (2) The skills dataset is manually curated, so it may not reflect the very latest job requirements. (3) The roadmap is template-based per fit band, not fully individualized — a more advanced version could generate truly custom learning paths using a recommendation engine.

---

**Q: What would you improve with more time?**

A: Three things: (1) Replace keyword matching with a fine-tuned sentence classifier (e.g., using sentence-transformers) for better intent detection. (2) Add user authentication so students can track their progress over time. (3) Integrate a spaced repetition system for problem practice, similar to Anki, so the app reminds users to revisit problems they found hard.

---

*Built for FSD AI Hackathon | Stack: React + Flask + Pandas | No external AI APIs used*
