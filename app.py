import os
import random
import flask
import psycopg2
import re
from flask import Flask, render_template, request, session, jsonify

# 🚀 Flask App
app = flask.Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# =========================================================
# 🧠 SMART EXPLANATION ENGINE (FULL SYSTEM)
# =========================================================

def generate_explanations(question, answer, qtype):
    if qtype in ["quant", "di"]:
        return solve_quant(question, answer)
    elif qtype == "logic":
        return solve_logic(question, answer)
    elif qtype == "verbal":
        return solve_verbal(question, answer)
    else:
        return default_explanation(question, answer)

# ---------------------------------------------------------
# 🔢 QUANT + DI SOLVER (STEP BY STEP)
# ---------------------------------------------------------
def solve_quant(question, answer):
    steps = []
    numbers = list(map(int, re.findall(r'\d+', question)))

    if "%" in question and "of" in question and len(numbers) >= 2:
        percent, total = numbers[0], numbers[1]
        result = (percent / 100) * total
        steps.append(f"Step 1: Convert {percent}% Into {percent}/100")
        steps.append(f"Step 2: Multiply ({percent}/100) × {total}")
        steps.append(f"Step 3: Result = {result}")
    elif "sum" in question.lower() or "+" in question:
        result = sum(numbers)
        steps.append(f"Step 1: Add → {' + '.join(map(str, numbers))}")
        steps.append(f"Step 2: Result = {result}")
    elif "×" in question or "cost" in question.lower():
        if len(numbers) >= 2:
            result = numbers[0] * numbers[1]
            steps.append(f"Step 1: Multiply → {numbers[0]} × {numbers[1]}")
            steps.append(f"Step 2: Result = {result}")
    elif "÷" in question or "divided" in question.lower():
        if len(numbers) >= 2:
            result = numbers[0] / numbers[1]
            steps.append(f"Step 1: Divide → {numbers[0]} ÷ {numbers[1]}")
            steps.append(f"Step 2: Result = {result}")
    else:
        steps.append("Step 1: Understand What Is Asked")
        steps.append("Step 2: Apply Correct Formula Or Logic")
        steps.append(f"Final Answer = {answer}")

    return build_levels(steps, answer)

# ---------------------------------------------------------
# 🧠 LOGIC SOLVER (PATTERN DETECTION)
# ---------------------------------------------------------
def solve_logic(question, answer):
    steps = []
    nums = list(map(int, re.findall(r'\d+', question)))

    if len(nums) >= 3:
        diff = nums[1] - nums[0]
        if all(nums[i+1] - nums[i] == diff for i in range(len(nums)-1)):
            steps.append(f"Pattern: +{diff} Each Step")
            steps.append(f"Next = {nums[-1]} + {diff}")
        elif nums[1] != 0 and nums[2] // nums[1] == nums[1] // nums[0]:
            ratio = nums[1] // nums[0]
            steps.append(f"Pattern: ×{ratio} Each Step")
            steps.append(f"Next = {nums[-1]} × {ratio}")
        else:
            steps.append("Pattern Is Increasing But Not Simple")
            steps.append("Observe Carefully Step By Step")
    else:
        steps.append("Identify Pattern From Given Data")

    steps.append(f"Final Answer = {answer}")
    return build_levels(steps, answer)

# ---------------------------------------------------------
# 📚 VERBAL SOLVER (RULE BASED)
# ---------------------------------------------------------
def solve_verbal(question, answer):
    steps = []
    if "___" in question:
        steps.append("Step 1: Identify Subject")
        steps.append("Step 2: Check Singular Or Plural")
        if answer in ["is", "am"]:
            steps.append("Rule: Singular Subject Uses Is/Am")
        elif answer == "are":
            steps.append("Rule: Plural Subject Uses Are")
    elif "synonym" in question.lower():
        steps.append("Step 1: Understand Meaning Of Word")
        steps.append("Step 2: Find Similar Meaning")
    elif "antonym" in question.lower():
        steps.append("Step 1: Understand Meaning")
        steps.append("Step 2: Find Opposite")
    else:
        steps.append("Apply Basic Grammar Rule")

    steps.append(f"Final Answer = {answer}")
    return build_levels(steps, answer)

# ---------------------------------------------------------
# 🧩 LEVEL BUILDER (3 LEVEL SYSTEM)
# ---------------------------------------------------------
def build_levels(steps, answer):
    lvl1 = " | ".join(steps[:2])
    lvl2 = "\n".join(steps)
    lvl3 = ["Let’s Understand This In A Very Simple Way:"]
    for s in steps:
        simple = s.replace("Step", "👉").replace("=", "Means")
        lvl3.append(simple)
    lvl3.append(f"So The Answer Is {answer} ✅")
    return {
        "level1": lvl1,
        "level2": lvl2,
        "level3": "\n".join(lvl3)
    }

# ---------------------------------------------------------
# 🧯 DEFAULT FALLBACK
# ---------------------------------------------------------
def default_explanation(question, answer):
    return {
        "level1": f"Basic Logic → {answer}",
        "level2": f"Understand And Solve Step By Step → {answer}",
        "level3": f"Think Slowly And You’ll Get → {answer}"
    }

# =========================================================
# 📊 QUESTION BANK
# =========================================================
all_questions = [
    {
        "q": "What Is The Main Cause Of SDK Usage Error?",
        "options": ["Incorrect API Key", "Network Issue", "Unsupported Version"],
        "answer": "Incorrect API Key",
        "type": "logic",
        "difficulty": "easy"
    },
    {
        "q": "How Can You Verify API Key Validity?",
        "options": ["Use SDK Test Method", "Guess Randomly", "Ignore It"],
        "answer": "Use SDK Test Method",
        "type": "logic",
        "difficulty": "easy"
    },
    {
        "q": "What Should You Do If SDK Version Is Unsupported?",
        "options": ["Update SDK", "Downgrade App", "Ignore Warning"],
        "answer": "Update SDK",
        "type": "logic",
        "difficulty": "medium"
    },
    {
        "q": "How Can Network Issues Affect SDK Usage?",
        "options": ["Timeout Errors", "Incorrect Results", "App Crash"],
        "answer": "Timeout Errors",
        "type": "logic",
        "difficulty": "medium"
    },
    {
        "q": "What Is The Recommended Way To Handle SDK Authentication?",
        "options": ["Hardcode Keys", "Use Environment Variables", "Ignore Auth"],
        "answer": "Use Environment Variables",
        "type": "logic",
        "difficulty": "hard"
    },
    {
        "q": "How Do You Debug Unexpected SDK Exceptions?",
        "options": ["Check Logs", "Restart App Only", "Ignore Error"],
        "answer": "Check Logs",
        "type": "logic",
        "difficulty": "hard"
    }
]

# =========================================================
# 🎯 QUESTION SELECTION
# =========================================================
def get_questions():
    easy = [q for q in all_questions if q.get("difficulty") == "easy"]
    medium = [q for q in all_questions if q.get("difficulty") == "medium"]
    hard = [q for q in all_questions if q.get("difficulty") == "hard"]

    random.shuffle(easy)
    random.shuffle(medium)
    random.shuffle(hard)

    selected = []
    selected += easy[:3]
    selected += medium[:5]
    selected += hard[:2]

    for i, q in enumerate(selected):
        q["id"] = i

    random.shuffle(selected)
    return selected

# =========================================================
# 🌐 ROUTES
# =========================================================

@app.route('/')
def home():
    return flask.render_template("home.html")

@app.route('/quiz', methods=['POST'])
def quiz():
    session['username'] = request.form.get('username')
    questions = get_questions()
    session['questions'] = questions
    return flask.render_template("quiz.html", questions=questions)

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    qid = data.get("id")
    user_answer = data.get("answer")

    questions = session.get('questions', [])
    q = next((q for q in questions if q.get("id") == qid), None)

    if not q:
        return jsonify({"error": "Question Not Found"}), 400

    correct = q["answer"] == user_answer
    response = {"correct": correct}

    if not correct:
        explanation = generate_explanations(q["q"], q["answer"], q["type"])
        response["explanation"] = explanation

    return jsonify(response)

# =========================================================
# 🗄️ DATABASE
# =========================================================
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL Not Set")
    return psycopg2.connect(db_url)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            username TEXT,
            score INTEGER,
            total INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print("DB ERROR:", e)

# =========================================================
# 📊 RESULT + ANALYTICS
# =========================================================
@app.route('/submit', methods=['POST'])
def submit():
    questions = session.get('questions', [])
    username = session.get('username', 'Guest')

    score = 0
    wrong = []

    for i, q in enumerate(questions):
        ans = request.form.get(f"q{i}")
        if ans == q["answer"]:
            score += 1
        else:
            explanation = generate_explanations(q["q"], q["answer"], q["type"])
            wrong.append({
                "q": q["q"],
                "correct": q["answer"],
                "exp": explanation
            })

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO results (username, score, total) VALUES (%s, %s, %s)",
        (username, score, len(questions))
    )
    conn.commit()
    conn.close()

    return flask.render_template(
        "result.html",
        score=score,
        total=len(questions),
        wrong=wrong
    )

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT score, total FROM results ORDER BY id ASC")
    data = c.fetchall()
    conn.close()

    scores = [d[0] for d in data]
    totals = [d[1] for d in data]
    attempts = len(scores)
    avg_score = round(sum(scores)/attempts, 2) if attempts > 0 else 0

    return render_template(
        "dashboard.html",
        scores=scores,
        totals=totals,
        attempts=attempts,
        avg_score=avg_score
    )

@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT username, score, total
        FROM results
        ORDER BY score DESC, timestamp ASC
        LIMIT 10
    """)
    data = c.fetchall()
    conn.close()

    return render_template("leaderboard.html", data=data)

# =========================================================
# ▶ RUN APP
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)