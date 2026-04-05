import os
import random
import re
import psycopg
import requests
from questions import all_questions
from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

# =========================================================
# 🚀 FLASK APP
# =========================================================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# =========================================================
# 🧠 AI ENGINE (LEVEL 4 - GROQ)
# =========================================================
def ai_explanation(question, correct):

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "AI Key Missing"

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",  # Faster + lighter (best for Render)
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Explain This Aptitude Question Step By Step Clearly.

Question: {question}
Correct Answer: {correct}

Break It Down Like A Teacher. Keep It Short And Smart.
"""
                }
            ]
        }

        res = requests.post(url, headers=headers, json=data, timeout=8)

        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]

        return "AI Response Failed"

    except Exception:
        return "AI Timeout / Error"


# =========================================================
# 🧠 EXPLANATION ENGINE (LEVEL 1-3)
# =========================================================
def generate_explanation(q, user_answer=None):

    question = q.get("q", "")
    correct = q.get("answer", "")
    qtype = q.get("type", "")
    subtype = q.get("subtype", "")

    def join_steps(steps):
        return "\n".join(steps)

    nums = list(map(int, re.findall(r'\d+', question)))

    # ================= WRONG ANALYSIS =================
    why_wrong = ""
    if user_answer and user_answer != correct:
        why_wrong = join_steps([
            f"Your Answer: {user_answer}",
            f"Correct Answer: {correct}",
            "",
            "Mistake Insight:",
            "Calculation Error / Pattern Miss / Concept Gap"
        ])

    # =====================================================
    # 🧠 QUANT ENGINE
    # =====================================================
    if qtype == "quant":

        if subtype == "percentage" and len(nums) >= 2:
            p, v = nums[0], nums[1]
            result = (p/100)*v

            return {
                "level1": correct,
                "level2": f"{p}% Of {v} = {result}",
                "level3": "Formula → (P/100 × Value)",
                "level4": ai_explanation(question, correct),
                "concept": "Percentage",
                "why_wrong": why_wrong
            }

        elif subtype == "average" and nums:
            total = sum(nums)
            avg = total / len(nums)

            return {
                "level1": correct,
                "level2": f"Sum={total}, Count={len(nums)}, Avg={avg}",
                "level3": "Average = Sum / Count",
                "level4": ai_explanation(question, correct),
                "concept": "Average",
                "why_wrong": why_wrong
            }

        elif subtype == "speed" and len(nums) >= 2:
            d, t = nums[0], nums[1]

            return {
                "level1": correct,
                "level2": f"Speed={d}/{t}={d/t}",
                "level3": "Speed = Distance / Time",
                "level4": ai_explanation(question, correct),
                "concept": "Speed",
                "why_wrong": why_wrong
            }

        elif subtype in ["interest", "compound_interest"]:
            return {
                "level1": correct,
                "level2": "Apply Interest Formula Carefully",
                "level3": "SI=(P×R×T)/100 | CI Uses Compounding",
                "level4": ai_explanation(question, correct),
                "concept": "Interest",
                "why_wrong": why_wrong
            }

        elif subtype in ["profit_loss", "profit_logic"]:
            return {
                "level1": correct,
                "level2": "Profit = SP - CP",
                "level3": "Profit% = (Profit/CP)*100",
                "level4": ai_explanation(question, correct),
                "concept": "Profit Loss",
                "why_wrong": why_wrong
            }

        elif subtype == "ratio":
            return {
                "level1": correct,
                "level2": "Divide Total Based On Ratio",
                "level3": "Part = (Ratio/Total Ratio)*Value",
                "level4": ai_explanation(question, correct),
                "concept": "Ratio",
                "why_wrong": why_wrong
            }

        elif subtype == "time_work":
            return {
                "level1": correct,
                "level2": "Work = Rate × Time",
                "level3": "Use LCM Or Reciprocal Method",
                "level4": ai_explanation(question, correct),
                "concept": "Time Work",
                "why_wrong": why_wrong
            }

        elif subtype in ["hcf", "lcm", "hcf_lcm"]:
            return {
                "level1": correct,
                "level2": "Use Prime Factorization",
                "level3": "LCM=Max Power, HCF=Min Power",
                "level4": ai_explanation(question, correct),
                "concept": "HCF LCM",
                "why_wrong": why_wrong
            }

        elif subtype in ["modulus", "clock", "age"]:
            return {
                "level1": correct,
                "level2": "Apply Concept Logic Carefully",
                "level3": "Break Into Equations Or Patterns",
                "level4": ai_explanation(question, correct),
                "concept": subtype,
                "why_wrong": why_wrong
            }

    # =====================================================
    # 🧠 LOGIC ENGINE
    # =====================================================
    elif qtype == "logic":

        if subtype == "series":
            diffs = [nums[i+1]-nums[i] for i in range(len(nums)-1)] if len(nums) >= 2 else []

            return {
                "level1": correct,
                "level2": f"Differences → {diffs}",
                "level3": "Check +, ×, Alternating Pattern",
                "level4": ai_explanation(question, correct),
                "concept": "Series",
                "why_wrong": why_wrong
            }

        elif subtype in ["pattern", "pattern_mix", "coding", "alphabet"]:
            return {
                "level1": correct,
                "level2": "Identify Hidden Rule",
                "level3": "Look For Increment / Encoding Logic",
                "level4": ai_explanation(question, correct),
                "concept": "Pattern Logic",
                "why_wrong": why_wrong
            }

        elif subtype == "odd_one":
            return {
                "level1": correct,
                "level2": "Find Mismatch",
                "level3": "Compare Category Or Property",
                "level4": ai_explanation(question, correct),
                "concept": "Classification",
                "why_wrong": why_wrong
            }

    # =====================================================
    # 🧠 VERBAL ENGINE
    # =====================================================
    elif qtype == "verbal":
        return {
            "level1": correct,
            "level2": "Check Grammar / Meaning",
            "level3": "Apply Rule Or Context",
            "level4": ai_explanation(question, correct),
            "concept": "Verbal",
            "why_wrong": why_wrong
        }

    # =====================================================
    # 📊 DI ENGINE
    # =====================================================
    elif qtype == "di":
        return {
            "level1": correct,
            "level2": "Interpret Data Carefully",
            "level3": "Apply Percentage / Ratio",
            "level4": ai_explanation(question, correct),
            "concept": "Data Interpretation",
            "why_wrong": why_wrong
        }

    # =====================================================
    # ⚠️ FALLBACK
    # =====================================================
    return {
        "level1": correct,
        "level2": "Apply Logic",
        "level3": "Break Stepwise",
        "level4": ai_explanation(question, correct),
        "concept": "General",
        "why_wrong": why_wrong
    }


# =========================================================
# 🧠 XP + QUESTIONS
# =========================================================
def get_xp(difficulty):
    return {"easy": 5, "medium": 10, "hard": 20}.get(difficulty, 5)


def get_questions(user_xp):
    level = "easy" if user_xp < 100 else "medium" if user_xp < 300 else "hard"

    filtered = [q for q in all_questions if q["difficulty"] == level]
    random.shuffle(filtered)

    selected = filtered[:10]

    for i, q in enumerate(selected):
        q["id"] = i

    return selected


# =========================================================
# 🗄️ DATABASE
# =========================================================
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL Missing")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg.connect(db_url, sslmode='require')


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            total_score INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()


# =========================================================
# 🏆 RANK SYSTEM
# =========================================================
def get_rank(xp):
    if xp >= 1000: return "Elite"
    elif xp >= 600: return "Expert"
    elif xp >= 300: return "Advanced"
    elif xp >= 100: return "Intermediate"
    return "Beginner"


# =========================================================
# 🌐 ROUTES
# =========================================================
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect('/quiz')

        elif not user:
            hashed = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username, hashed))
            conn.commit()
            session['username'] = username
            return redirect('/quiz')

        return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():

    if 'username' not in session:
        return redirect('/')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT xp FROM users WHERE username=%s", (session['username'],))
    xp = cur.fetchone()[0]

    questions = get_questions(xp)
    session['questions'] = questions

    return render_template("quiz.html", questions=questions)


@app.route('/submit', methods=['POST'])
def submit():

    questions = session.get('questions', [])
    username = session.get('username')

    score = 0
    xp_earned = 0
    wrong = []

    for i, q in enumerate(questions):
        ans = request.form.get(f"q{i}")

        if ans == q["answer"]:
            score += 1
            xp_earned += get_xp(q["difficulty"])
        else:
            wrong.append({
                "q": q["q"],
                "correct": q["answer"],
                "exp": generate_explanation(q, ans)
            })

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT xp FROM users WHERE username=%s", (username,))
    current_xp = cur.fetchone()[0]

    new_xp = current_xp + xp_earned

    cur.execute("""
        UPDATE users
        SET total_score = total_score + %s,
            total_attempts = total_attempts + %s,
            xp = %s
        WHERE username = %s
    """, (score, len(questions), new_xp, username))

    conn.commit()
    cur.close()
    conn.close()

    return render_template("result.html",
        score=score,
        total=len(questions),
        wrong=wrong,
        xp_earned=xp_earned,
        new_xp=new_xp,
        rank=get_rank(new_xp)
    )


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================================================
# ▶ RUN
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
