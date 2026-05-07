import os
import re
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'dataset')
COMPANIES = ['accenture', 'amazon', 'apple', 'google', 'microsoft', 'netflix', 'tcs', 'zoho']

# Load LeetCode CSVs
def load_data():
    data = {}
    for company in COMPANIES:
        path = os.path.join(DATASET_DIR, f'{company}.csv')
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.strip() for c in df.columns]
            df['Frequency %'] = df['Frequency %'].str.replace('%', '').astype(float)
            df['Acceptance %'] = df['Acceptance %'].str.replace('%', '').astype(float)
            difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
            df['diff_order'] = df['Difficulty'].map(difficulty_order)
            df = df.sort_values(['diff_order', 'Frequency %'], ascending=[True, False])
            data[company] = df
    return data

DATA = load_data()

# Load skills dataset
with open(os.path.join(DATASET_DIR, 'skills_dataset.json')) as f:
    SKILLS_DATA = json.load(f)

# ── Skill Matching ──────────────────────────────────────────────────────────

def normalize(skill):
    return skill.lower().strip()

def compute_fit(user_skills, required, good_to_have):
    user_set = set(normalize(s) for s in user_skills)
    req_set  = set(normalize(s) for s in required)
    gth_set  = set(normalize(s) for s in good_to_have)

    req_match = len(user_set & req_set)
    gth_match = len(user_set & gth_set)

    # Required skills = 70%, good_to_have = 30%
    req_score = (req_match / len(req_set)) * 70 if req_set else 0
    gth_score = (gth_match / len(gth_set)) * 30 if gth_set else 0
    fit = round(req_score + gth_score, 1)

    missing_required = [s for s in required if normalize(s) not in user_set]
    missing_gth      = [s for s in good_to_have if normalize(s) not in user_set]
    return fit, missing_required, missing_gth

def generate_roadmap(missing_required, missing_gth, fit):
    steps = []
    if fit >= 80:
        steps.append("✅ You're well-prepared! Focus on mock interviews and system design practice.")
    elif fit >= 50:
        steps.append("📈 Good foundation! Bridge the gaps below to become a strong candidate.")
    else:
        steps.append("🚀 Start with the required skills — build a solid foundation first.")

    if missing_required:
        steps.append(f"🔴 **Must Learn (Required):** {', '.join(missing_required[:6])}" +
                     (f" +{len(missing_required)-6} more" if len(missing_required) > 6 else ""))
    if missing_gth:
        steps.append(f"🟡 **Nice to Have:** {', '.join(missing_gth[:4])}" +
                     (f" +{len(missing_gth)-4} more" if len(missing_gth) > 4 else ""))

    # Generic learning path based on fit
    if fit < 40:
        steps.append("📚 **Week 1-2:** Learn core programming (Python/Java) + Data Structures basics")
        steps.append("📚 **Week 3-4:** Practice Easy LeetCode problems daily (5-10/day)")
        steps.append("📚 **Week 5-6:** Study Algorithms (sorting, searching, recursion)")
        steps.append("📚 **Week 7-8:** Move to Medium problems + start missing required skills")
    elif fit < 70:
        steps.append("📚 **Week 1-2:** Fill required skill gaps with focused study")
        steps.append("📚 **Week 3-4:** Practice Medium LeetCode problems (5/day)")
        steps.append("📚 **Week 5-6:** System Design basics + mock interviews")
        steps.append("📚 **Week 7-8:** Work on good-to-have skills + company-specific prep")
    else:
        steps.append("📚 **Week 1-2:** Advanced DSA (DP, Graphs, Trees) + Hard problems")
        steps.append("📚 **Week 3-4:** System Design deep dive + distributed systems")
        steps.append("📚 **Week 5-6:** Mock interviews + behavioral prep (STAR method)")
        steps.append("📚 **Week 7-8:** Company-specific problem sets + good-to-have skills")

    return steps

def analyze_skills(user_skills):
    results = {}
    for company, roles in SKILLS_DATA.items():
        results[company] = {}
        for role, data in roles.items():
            fit, miss_req, miss_gth = compute_fit(user_skills, data['required'], data['good_to_have'])
            roadmap = generate_roadmap(miss_req, miss_gth, fit)
            results[company][role] = {
                'fit': fit,
                'description': data['description'],
                'missing_required': miss_req,
                'missing_good_to_have': miss_gth,
                'roadmap': roadmap
            }
    return results

# ── LeetCode helpers ────────────────────────────────────────────────────────

def get_stats(company):
    df = DATA[company]
    return {
        'total': len(df),
        'easy': int((df['Difficulty'] == 'Easy').sum()),
        'medium': int((df['Difficulty'] == 'Medium').sum()),
        'hard': int((df['Difficulty'] == 'Hard').sum()),
        'top_frequency': round(float(df['Frequency %'].max()), 1),
        'avg_acceptance': round(float(df['Acceptance %'].mean()), 1),
    }

def get_problems(company, difficulty=None, limit=10):
    df = DATA[company].copy()
    if difficulty:
        df = df[df['Difficulty'].str.lower() == difficulty.lower()]
    rows = df.head(limit)
    return rows[['ID', 'Title', 'Difficulty', 'Acceptance %', 'Frequency %', 'URL']].to_dict(orient='records')

# ── Intent Detection ────────────────────────────────────────────────────────

def extract_intent(message):
    msg = message.lower()

    company = None
    for c in COMPANIES:
        if c in msg:
            company = c
            break

    difficulty = None
    if 'easy' in msg or 'beginner' in msg:
        difficulty = 'Easy'
    elif 'medium' in msg:
        difficulty = 'Medium'
    elif 'hard' in msg or 'difficult' in msg:
        difficulty = 'Hard'

    # Skills / roadmap intent
    if any(w in msg for w in ['my skill', 'i know', 'i have', 'skills are', 'skill set', 'roadmap', 'fit for', 'which role', 'what role', 'career path']):
        return 'skills', company, difficulty

    # Aptitude intent
    if any(w in msg for w in ['aptitude', 'number series', 'time and work', 'probability', 'logical reasoning', 'reasoning', 'quantitative', 'improve aptitude']):
        return 'aptitude', company, difficulty

    # Interview intent
    if any(w in msg for w in ['hr', 'interview', 'tell me about yourself', 'strengths', 'weaknesses', 'behavioral', 'hr round', 'hr question']):
        return 'interview', company, difficulty

    # Strategy / preparation plan intent
    if any(w in msg for w in ['30 days', 'study plan', 'daily plan', 'how many hours', 'resources', 'roadmap for placement', 'preparation plan', 'improve problem solving', 'best resources']):
        return 'strategy', company, difficulty

    # General placement intent
    if any(w in msg for w in ['placement', 'what topics', 'how to start', 'placement process', 'skills required', 'get a job', 'common placement']):
        return 'placement', company, difficulty

    # DSA / coding intent
    if any(w in msg for w in ['dsa', 'array', 'string', 'coding question', 'data structure', 'algorithm', 'dynamic programming', 'graph', 'tree', 'linked list', 'stack', 'queue', 'most asked coding', 'coding problem']):
        return 'dsa', company, difficulty

    # Existing intents
    if any(w in msg for w in ['stat', 'overview', 'summary', 'how many', 'count', 'total']):
        return 'stats', company, difficulty
    if any(w in msg for w in ['tip', 'advice', 'strategy', 'approach', 'how to', 'guide']):
        return 'tips', company, difficulty
    if any(w in msg for w in ['hi', 'hello', 'hey', 'help', 'what can']):
        return 'greet', company, difficulty
    if any(w in msg for w in ['compare', 'vs', 'versus', 'difference']):
        return 'compare', company, difficulty
    if any(w in msg for w in ['top', 'list', 'show', 'give', 'problems', 'questions', 'practice', 'prepare', 'start']):
        return 'problems', company, difficulty

    return 'problems', company, difficulty

# ── Static Response Data ────────────────────────────────────────────────────

TIPS = {
    'google': "Google focuses heavily on algorithms and data structures. Master dynamic programming, graphs (BFS/DFS), and system design. Expect multiple rounds with increasing difficulty.",
    'amazon': "Amazon loves behavioral questions (STAR method) alongside coding. Focus on arrays, trees, graphs, and DP. Leadership principles are key — prepare stories for each.",
    'microsoft': "Microsoft values problem-solving clarity. Practice trees, graphs, and DP. Explain your thought process clearly. Expect design questions in senior roles.",
    'tcs': "TCS focuses on aptitude, basic DSA, and verbal ability. Easy-Medium LeetCode problems are sufficient. Focus on arrays, strings, and basic math.",
    'accenture': "Accenture tests aptitude, coding basics, and communication. Focus on Easy problems, sorting, searching, and basic DP. Verbal and logical reasoning matter too.",
    'zoho': "Zoho has a strong coding round. Practice Medium-Hard problems. They test real-world problem solving — focus on strings, arrays, and OOP concepts.",
    'apple': "Apple values elegant, efficient code. Focus on system design, algorithms, and clean code. Expect deep dives into your past projects.",
    'netflix': "Netflix focuses on system design and scalability. Strong DSA fundamentals required. Expect questions on distributed systems and high-level design.",
}

APTITUDE_RESPONSE = """**📊 Aptitude & Reasoning Preparation Guide**

**Key Topics:**
• **Number Series** — Find the pattern (arithmetic, geometric, Fibonacci)
• **Time & Work** — Work = Rate × Time; use LCM method for efficiency
• **Probability** — P(A) = Favorable outcomes / Total outcomes
• **Logical Reasoning** — Syllogisms, blood relations, seating arrangements
• **Quantitative Aptitude** — Percentages, profit/loss, ratio & proportion, speed-distance-time

**Sample Questions:**
1. 2, 6, 12, 20, 30, ? → Answer: 42 (differences: 4,6,8,10,12)
2. A can do work in 10 days, B in 15 days. Together? → 6 days (LCM=30, A=3, B=2, together=5 units/day)
3. Probability of getting a head in 2 coin tosses? → 3/4

**How to Improve Speed:**
• Practice 20 questions daily with a timer
• Learn shortcut formulas (Vedic math tricks)
• Use IndiaBix, PrepInsta, or RS Aggarwal book
• Time yourself: aim for <60 seconds per question"""

INTERVIEW_RESPONSE = """**🎤 Interview Preparation Guide**

**Common HR Questions & Tips:**

1. **"Tell me about yourself"**
   → 3-part formula: Background + Skills/Experience + Why this role
   → Keep it under 2 minutes, professional, and relevant

2. **"Strengths & Weaknesses"**
   → Strength: Pick one relevant to the role (e.g., "strong problem-solver")
   → Weakness: Pick a real one + show how you're improving it

3. **"Why this company?"**
   → Research the company, mention specific products/values

4. **Technical Interview Tips:**
   • Think out loud — explain your approach before coding
   • Clarify edge cases before starting
   • Start with brute force, then optimize
   • Test your code with examples

5. **STAR Method for Behavioral Questions:**
   • **S**ituation → **T**ask → **A**ction → **R**esult

**Common Technical Questions for Freshers:**
• OOP concepts (inheritance, polymorphism, encapsulation)
• Difference between Array and LinkedList
• What is recursion? Give an example
• Explain time complexity with Big O notation"""

STRATEGY_RESPONSE = """**📅 Placement Preparation Strategy**

**30-Day Intensive Plan:**

🗓️ **Week 1 — Foundation**
• Day 1-3: Arrays, Strings, Basic Math
• Day 4-5: Sorting & Searching algorithms
• Day 6-7: Solve 15 Easy LeetCode problems

🗓️ **Week 2 — Core DSA**
• Day 8-10: Linked Lists, Stacks, Queues
• Day 11-12: Trees & Binary Search
• Day 13-14: Solve 10 Medium problems

🗓️ **Week 3 — Advanced Topics**
• Day 15-17: Dynamic Programming (top 20 patterns)
• Day 18-19: Graphs (BFS, DFS, Dijkstra)
• Day 20-21: System Design basics

🗓️ **Week 4 — Mock & Polish**
• Day 22-25: Company-specific problem sets
• Day 26-27: Mock interviews (Pramp, Interviewing.io)
• Day 28-29: HR prep + behavioral questions
• Day 30: Revision + confidence building

**Best Resources:**
• LeetCode, GeeksforGeeks, NeetCode.io
• Striver's DSA Sheet (180 problems)
• System Design Primer (GitHub)
• CS50 (Harvard free course)

**Daily Study Hours:**
• Minimum: 3-4 hours/day
• Optimal: 6-8 hours/day for 30-day sprint"""

PLACEMENT_RESPONSE = """**🎯 Placement Preparation Guide**

**Common Placement Process:**
1. **Online Test** — Aptitude + Coding + Verbal
2. **Technical Round 1** — DSA + OOP + Projects
3. **Technical Round 2** — System Design / Advanced DSA
4. **HR Round** — Behavioral + Salary negotiation

**Key Topics to Prepare:**
• **DSA:** Arrays, Strings, Trees, Graphs, DP, Sorting
• **CS Fundamentals:** OS, DBMS, CN, OOP
• **Aptitude:** Quant, Logical Reasoning, Verbal
• **Projects:** 2-3 solid projects with GitHub

**Skills Required to Get a Job:**
• Programming language (Python/Java/C++)
• Data Structures & Algorithms
• Problem-solving mindset
• Communication skills
• Basic system design knowledge

**How to Start:**
1. Pick one language and master it
2. Learn DSA fundamentals (arrays → trees → graphs)
3. Solve 100+ LeetCode problems (Easy→Medium)
4. Build 2-3 projects
5. Practice mock interviews"""

DSA_TOPICS = {
    'array': [
        {"title": "Two Sum", "difficulty": "Easy", "url": "https://leetcode.com/problems/two-sum/"},
        {"title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Maximum Subarray (Kadane's)", "difficulty": "Medium", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Product of Array Except Self", "difficulty": "Medium", "url": "https://leetcode.com/problems/product-of-array-except-self/"},
        {"title": "Trapping Rain Water", "difficulty": "Hard", "url": "https://leetcode.com/problems/trapping-rain-water/"},
    ],
    'string': [
        {"title": "Valid Anagram", "difficulty": "Easy", "url": "https://leetcode.com/problems/valid-anagram/"},
        {"title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"},
        {"title": "Longest Palindromic Substring", "difficulty": "Medium", "url": "https://leetcode.com/problems/longest-palindromic-substring/"},
        {"title": "Minimum Window Substring", "difficulty": "Hard", "url": "https://leetcode.com/problems/minimum-window-substring/"},
    ],
    'dp': [
        {"title": "Climbing Stairs", "difficulty": "Easy", "url": "https://leetcode.com/problems/climbing-stairs/"},
        {"title": "Coin Change", "difficulty": "Medium", "url": "https://leetcode.com/problems/coin-change/"},
        {"title": "Longest Increasing Subsequence", "difficulty": "Medium", "url": "https://leetcode.com/problems/longest-increasing-subsequence/"},
        {"title": "Edit Distance", "difficulty": "Hard", "url": "https://leetcode.com/problems/edit-distance/"},
    ],
    'graph': [
        {"title": "Number of Islands", "difficulty": "Medium", "url": "https://leetcode.com/problems/number-of-islands/"},
        {"title": "Clone Graph", "difficulty": "Medium", "url": "https://leetcode.com/problems/clone-graph/"},
        {"title": "Course Schedule", "difficulty": "Medium", "url": "https://leetcode.com/problems/course-schedule/"},
        {"title": "Word Ladder", "difficulty": "Hard", "url": "https://leetcode.com/problems/word-ladder/"},
    ],
    'tree': [
        {"title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"},
        {"title": "Validate Binary Search Tree", "difficulty": "Medium", "url": "https://leetcode.com/problems/validate-binary-search-tree/"},
        {"title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "url": "https://leetcode.com/problems/binary-tree-level-order-traversal/"},
        {"title": "Serialize and Deserialize Binary Tree", "difficulty": "Hard", "url": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/"},
    ],
    'general': [
        {"title": "Two Sum", "difficulty": "Easy", "url": "https://leetcode.com/problems/two-sum/"},
        {"title": "Valid Parentheses", "difficulty": "Easy", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Merge Intervals", "difficulty": "Medium", "url": "https://leetcode.com/problems/merge-intervals/"},
        {"title": "LRU Cache", "difficulty": "Medium", "url": "https://leetcode.com/problems/lru-cache/"},
        {"title": "Median of Two Sorted Arrays", "difficulty": "Hard", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
    ]
}

# ── Response Builder ────────────────────────────────────────────────────────

def build_response(intent, company, difficulty, message):
    msg = message.lower()

    if intent == 'greet':
        return {
            'text': "👋 Hi! I'm your **Placement Prep AI**.\n\n"
                    "I can help you with:\n"
                    "• 🎯 Company-specific LeetCode problems\n"
                    "• 🧠 Aptitude & reasoning questions\n"
                    "• 🎤 Interview preparation tips\n"
                    "• 📅 Study plans & strategies\n"
                    "• 💡 Skill analysis & career roadmap\n\n"
                    "Try: *'Analyze my skills: Python, SQL, Machine Learning'*\n"
                    "Or: *'Give me array problems'*, *'HR interview tips'*, *'30-day plan'*",
            'type': 'text'
        }

    if intent == 'aptitude':
        return {'text': APTITUDE_RESPONSE, 'type': 'text'}

    if intent == 'interview':
        return {'text': INTERVIEW_RESPONSE, 'type': 'text'}

    if intent == 'strategy':
        return {'text': STRATEGY_RESPONSE, 'type': 'text'}

    if intent == 'placement':
        return {'text': PLACEMENT_RESPONSE, 'type': 'text'}

    if intent == 'dsa':
        # Detect topic
        topic = 'general'
        if 'array' in msg: topic = 'array'
        elif 'string' in msg: topic = 'string'
        elif any(w in msg for w in ['dp', 'dynamic programming']): topic = 'dp'
        elif 'graph' in msg: topic = 'graph'
        elif 'tree' in msg: topic = 'tree'

        problems = DSA_TOPICS[topic]
        if difficulty:
            problems = [p for p in problems if p['difficulty'].lower() == difficulty.lower()]
        if not problems:
            problems = DSA_TOPICS[topic]

        label = topic.upper() if topic != 'general' else 'DSA'
        diff_label = f" ({difficulty})" if difficulty else ""
        return {
            'text': f"**💻 Top {label} Problems{diff_label} for Placement Prep:**",
            'type': 'dsa_problems',
            'problems': problems
        }

    if intent == 'tips':
        if company and company in TIPS:
            return {'text': f"**{company.capitalize()} Preparation Tips:**\n\n{TIPS[company]}", 'type': 'text'}
        tips_all = "\n\n".join([f"**{c.capitalize()}:** {t}" for c, t in TIPS.items()])
        return {'text': f"**General Placement Tips:**\n\n{tips_all}", 'type': 'text'}

    if intent == 'stats':
        if not company:
            all_stats = [{'company': c.capitalize(), **get_stats(c)} for c in COMPANIES]
            return {'text': 'Here are stats for all companies:', 'type': 'stats', 'data': all_stats}
        s = get_stats(company)
        return {
            'text': f"**{company.capitalize()} Stats:**\n\n"
                    f"📊 Total Problems: {s['total']}\n"
                    f"🟢 Easy: {s['easy']} | 🟡 Medium: {s['medium']} | 🔴 Hard: {s['hard']}\n"
                    f"⚡ Max Frequency: {s['top_frequency']}%\n"
                    f"✅ Avg Acceptance: {s['avg_acceptance']}%",
            'type': 'text', 'stats': s, 'company': company
        }

    if intent == 'compare':
        mentioned = [c for c in COMPANIES if c in msg]
        if len(mentioned) < 2:
            mentioned = COMPANIES[:2]
        result = [{'company': c.capitalize(), **get_stats(c)} for c in mentioned[:3]]
        return {'text': f"Comparing {', '.join([r['company'] for r in result])}:", 'type': 'stats', 'data': result}

    # Default: problems
    if not company:
        return {
            'text': "Please mention a company name! I support: " + ', '.join([c.capitalize() for c in COMPANIES]),
            'type': 'text'
        }
    problems = get_problems(company, difficulty, limit=10)
    diff_label = difficulty if difficulty else 'All'
    return {
        'text': f"**Top {diff_label} problems for {company.capitalize()}** (sorted Easy→Hard by frequency):",
        'type': 'problems',
        'problems': problems,
        'company': company,
        'difficulty': difficulty
    }

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    body = request.json
    message = body.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    intent, company, difficulty = extract_intent(message)
    response = build_response(intent, company, difficulty, message)
    return jsonify(response)

@app.route('/api/skills', methods=['POST'])
def skills():
    body = request.json
    user_skills = body.get('skills', [])
    if not user_skills:
        return jsonify({'error': 'No skills provided'}), 400
    results = analyze_skills(user_skills)
    return jsonify(results)

@app.route('/api/stats', methods=['GET'])
def stats():
    result = [{'company': c.capitalize(), **get_stats(c)} for c in COMPANIES]
    return jsonify(result)

@app.route('/api/problems/<company>', methods=['GET'])
def problems(company):
    company = company.lower()
    if company not in DATA:
        return jsonify({'error': 'Company not found'}), 404
    difficulty = request.args.get('difficulty')
    limit = int(request.args.get('limit', 20))
    return jsonify(get_problems(company, difficulty, limit))

@app.route('/api/companies', methods=['GET'])
def companies():
    return jsonify(COMPANIES)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
