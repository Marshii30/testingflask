from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'   # Needed for flash messages

# ── MySQL connection ────────────────────────────────────────────────────────────
db = mysql.connector.connect(
    host="localhost",
    user="root",          # ← replace if different
    password="Maharshi@2004",  # ← replace if different
    database="session1"   # ← replace if different
)
cursor = db.cursor()

# ── Basic pages ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')            # NEW: contact page
def contact():
    return render_template('contact.html')

# ── Registration ───────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username        = request.form['username']
        raw_password    = request.form['password']
        hashed_password = generate_password_hash(raw_password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            db.commit()
            flash("✅ Registration successful!", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("❌ Username already exists!", "error")
            return redirect(url_for('register'))

    return render_template('register.html')

# ── Login ──────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username       = request.form['username']
        password_input = request.form['password']

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            stored_hash = result[0]
            if check_password_hash(stored_hash, password_input):
                flash("✅ Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("❌ Incorrect password!", "error")
        else:
            flash("❌ Username not found!", "error")

        return redirect(url_for('login'))

    return render_template('login.html')

# ── Review form & insertion ────────────────────────────────────────────────────
@app.route('/review_form')
def review_form():
    return render_template('add_review.html')

@app.route('/add_review', methods=['POST'])
def add_review():
    movie_name = request.form['movie_name']
    reviewer   = request.form['reviewer']
    review     = request.form['review']
    rating     = int(request.form['rating'])

    sql    = "INSERT INTO reviews (movie_name, reviewer, review, rating) VALUES (%s, %s, %s, %s)"
    values = (movie_name, reviewer, review, rating)

    try:
        cursor.execute(sql, values)
        db.commit()
        flash("✅ Review added successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"❌ Error: {e}", "danger")

    return redirect(url_for('index'))

# ── Run the server ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)