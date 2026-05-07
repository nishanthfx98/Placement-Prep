# PlacementAI — Placement Prep Chatbot

A full-stack AI chatbot + dashboard for placement preparation, trained on LeetCode problem datasets for 8 top companies.

## Features
- 🤖 **AI Chatbot** — answers questions about company-specific problems, tips, stats
- 📊 **Dashboard** — visual overview of all companies with difficulty breakdown
- 📋 **Problems Table** — filterable by difficulty, sorted Easy→Hard by frequency
- 🎯 **8 Companies** — Google, Amazon, Microsoft, Apple, Netflix, TCS, Accenture, Zoho

## Quick Start

### Option 1: Run the batch file
```
start.bat
```

### Option 2: Manual

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Backend: http://localhost:5000
- Frontend: http://localhost:5173

## How the AI Works
- **Intent detection** — parses user messages for company names, difficulty, and intent (problems/stats/tips/compare)
- **Priority sorting** — problems sorted Easy→Medium→Hard, then by frequency % (most asked first)
- **REST API** — `/api/chat`, `/api/stats`, `/api/problems/<company>`, `/api/companies`
